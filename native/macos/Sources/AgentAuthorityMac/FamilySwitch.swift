import Foundation
import CoreFoundation

/// Native-only adapter to the existing KiraBridge family broker. No shell or URL input.
enum FamilySwitchError: Error { case invalidTarget, unavailable, failed, unknown, busy }

final class FamilySwitchClient {
    static let productIDs = ["kirabridge", "threaddesk", "4allpass", "tollgate", "agent-authority"]
    static var executableURL: URL {
        FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent(".local/bin/kirabridge")
    }
    static func arguments(target: String, sourcePID: Int32) throws -> [String] {
        guard productIDs.contains(target), sourcePID > 0 else { throw FamilySwitchError.invalidTarget }
        return ["--principal", "local", "family", "switch", target, "--source-pid", String(sourcePID)]
    }
    static func validateReply(_ data: Data, exitStatus: Int32, target: String) throws {
        func number(_ value: Any?) -> Double? {
            guard let n = value as? NSNumber, CFGetTypeID(n) != CFBooleanGetTypeID(), n.doubleValue.isFinite else { return nil }
            return n.doubleValue
        }
        guard exitStatus == 0, data.count <= 65536,
              let reply = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let success = reply["success"] as? NSNumber,
              CFGetTypeID(success) == CFBooleanGetTypeID(), success.boolValue,
              reply["error"] == nil, reply["active_product"] as? String == target,
              number(reply["visible_family_windows"]) == 1,
              let bounds = reply["actual_outer_bounds"] as? [String: Any],
              number(bounds["x"]) != nil, number(bounds["y"]) != nil,
              let width = number(bounds["width"]), width > 0,
              let height = number(bounds["height"]), height > 0,
              reply["execution_outcome_unknown"] == nil || (reply["execution_outcome_unknown"] as? Bool == false)
              else { throw FamilySwitchError.unknown }
    }

    typealias Transport = (URL, [String]) throws -> (Data, Int32)
    private let transport: Transport
    private var busy = false // Accessed on the main thread; repeated clicks never queue a replay.
    init(transport: @escaping Transport = FamilySwitchClient.run) { self.transport = transport }

    func switchProduct(_ target: String, completion: @escaping (Result<Void, Error>) -> Void) {
        precondition(Thread.isMainThread)
        guard !busy else { completion(.failure(FamilySwitchError.busy)); return }
        let arguments: [String]
        do { arguments = try Self.arguments(target: target, sourcePID: ProcessInfo.processInfo.processIdentifier) }
        catch { completion(.failure(error)); return }
        busy = true
        DispatchQueue.global(qos: .userInitiated).async {
            let result: Result<Void, Error>
            do {
                let (data, status) = try self.transport(Self.executableURL, arguments)
                try Self.validateReply(data, exitStatus: status, target: target)
                result = .success(())
            } catch { result = .failure(error) }
            DispatchQueue.main.async { self.busy = false; completion(result) }
        }
    }

    private static func run(_ executable: URL, _ arguments: [String]) throws -> (Data, Int32) {
        guard FileManager.default.isExecutableFile(atPath: executable.path) else { throw FamilySwitchError.unavailable }
        let process = Process(), output = Pipe()
        process.executableURL = executable; process.arguments = arguments
        process.standardInput = FileHandle.nullDevice
        process.standardOutput = output
        process.standardError = FileHandle.nullDevice // Never display raw broker diagnostics or paths.
        let capture = FamilyReplyCapture()
        output.fileHandleForReading.readabilityHandler = { handle in
            let data = handle.availableData
            if data.isEmpty { handle.readabilityHandler = nil; capture.finished.signal(); return }
            if !capture.append(data), process.isRunning { process.terminate() }
        }
        defer { output.fileHandleForReading.readabilityHandler = nil; try? output.fileHandleForReading.close() }
        try process.run()
        let timeout = DispatchWorkItem {
            capture.invalidate()
            if process.isRunning { process.terminate() }
            DispatchQueue.global().asyncAfter(deadline: .now() + 0.5) {
                if process.isRunning { kill(process.processIdentifier, SIGKILL) }
            }
        }
        DispatchQueue.global().asyncAfter(deadline: .now() + 20, execute: timeout)
        process.waitUntilExit(); timeout.cancel()
        guard capture.finished.wait(timeout: .now() + 1) == .success else { throw FamilySwitchError.unknown }
        guard let data = capture.result else { throw FamilySwitchError.unknown }
        return (data, process.terminationStatus)
    }
}

private final class FamilyReplyCapture {
    let finished = DispatchSemaphore(value: 0)
    private let lock = NSLock()
    private var data = Data(), valid = true
    func append(_ chunk: Data) -> Bool {
        lock.lock(); defer { lock.unlock() }
        guard valid, data.count + chunk.count <= 65536 else { valid = false; return false }
        data.append(chunk); return true
    }
    func invalidate() { lock.lock(); valid = false; lock.unlock() }
    var result: Data? { lock.lock(); defer { lock.unlock() }; return valid ? data : nil }
}
