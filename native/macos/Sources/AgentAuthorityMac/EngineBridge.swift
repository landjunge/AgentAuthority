import AppKit
import AuthorityCore

final class EngineBridge {
    private var running: Process?
    private let lock=NSLock()
    private var cancelled=false
    private let worker=DispatchQueue(label:"AgentAuthority.engine",qos:.userInitiated)
    var busy: Bool { lock.lock();defer{lock.unlock()};return running != nil }
    var engineDirectory: URL { Bundle.main.resourceURL!.appendingPathComponent("Engine") }
    var interpreter: URL? {
        if let p=UserDefaults.standard.string(forKey:"pythonPath"),FileManager.default.isExecutableFile(atPath:p) { return URL(fileURLWithPath:p) }
        let bundled=Bundle.main.resourceURL!.appendingPathComponent("Runtime/bin/python3.12")
        if FileManager.default.isExecutableFile(atPath:bundled.path) { return bundled }
        return nil
    }
    func cancel() { lock.lock();cancelled=true;let process=running;lock.unlock();if process?.isRunning == true{process?.terminate()} }
    func inspect(directory:URL,sourceID:String,completion:@escaping(Result<GraphDocument,Error>)->Void) {
        guard let python=interpreter else { completion(.failure(BridgeError.noRuntime));return }
        guard sourceID.range(of:"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$",options:.regularExpression) != nil else {completion(.failure(ModelError.invalidReport));return}
        guard !busy else { return }
        let process=Process(),stdout=Pipe(),stderr=Pipe()
        process.executableURL=python
        // Fixed bootstrap; all user-controlled paths are separate argv entries, never shell source.
        process.arguments=["-I","-X","utf8","-c","import sys,runpy;sys.path.insert(0,sys.argv.pop(1));runpy.run_module('agent_authority',run_name='__main__')",engineDirectory.path,
            "inspect","--source","json-directory","--input",directory.path,"--source-id",sourceID,"--format","json","--limit","100"]
        process.environment=["PATH":"/usr/bin:/bin","HOME":NSHomeDirectory(),"LANG":"en_US.UTF-8"]
        process.standardOutput=stdout;process.standardError=stderr
        lock.lock();running=process;cancelled=false;lock.unlock()
        worker.async {
            let capture=BoundedCapture(limit:8*1024*1024),errors=BoundedCapture(limit:65536)
            let stderrDone=DispatchSemaphore(value:0)
            stderr.fileHandleForReading.readabilityHandler={ handle in
                let data=handle.availableData;if data.isEmpty {handle.readabilityHandler=nil;stderrDone.signal();return}
                if !errors.append(data) {process.terminate()}
            }
            let timeout=DispatchWorkItem { if process.isRunning {capture.timedOut=true;process.terminate();DispatchQueue.global().asyncAfter(deadline:.now()+0.5){if process.isRunning{kill(process.processIdentifier,SIGKILL)}}} }
            var result:Result<GraphDocument,Error>
            do {
                try process.run();DispatchQueue.global().asyncAfter(deadline:.now()+30,execute:timeout)
                self.lock.lock();let cancelledBeforeStart=self.cancelled;self.lock.unlock();if cancelledBeforeStart{process.terminate()}
                while true{let chunk=stdout.fileHandleForReading.availableData;if chunk.isEmpty{break};if !capture.append(chunk),process.isRunning{process.terminate()}}
                process.waitUntilExit();timeout.cancel()
                _=stderrDone.wait(timeout:.now()+1);stderr.fileHandleForReading.readabilityHandler=nil
                self.lock.lock();let wasCancelled=self.cancelled;self.lock.unlock()
                if wasCancelled { throw BridgeError.cancelled }
                if capture.exceeded || capture.timedOut || errors.exceeded { throw BridgeError.limit }
                guard [0,2].contains(process.terminationStatus) else { throw BridgeError.failed }
                result = .success(try ReportProjection.decode(capture.data))
            } catch { result = .failure(error) }
            try? stdout.fileHandleForReading.close();try? stderr.fileHandleForReading.close()
            self.lock.lock();self.running=nil;self.lock.unlock()
            DispatchQueue.main.async { completion(result) }
        }
    }
}
enum BridgeError:Error { case noRuntime,cancelled,limit,failed }
private final class BoundedCapture {
    private let lock=NSLock();private var bytes=Data();let limit:Int
    private var overflow=false;private var timeout=false
    init(limit:Int){self.limit=limit}
    var exceeded:Bool{lock.lock();defer{lock.unlock()};return overflow}
    var timedOut:Bool{get{lock.lock();defer{lock.unlock()};return timeout}set{lock.lock();timeout=newValue;lock.unlock()}}
    var data:Data{lock.lock();defer{lock.unlock()};return bytes}
    func append(_ data:Data)->Bool {lock.lock();defer{lock.unlock()};guard bytes.count+data.count<=limit else {overflow=true;return false};bytes.append(data);return true}
}

func readBoundedReport(_ url:URL) throws -> Data {
    let fd=open(url.path,O_RDONLY|O_NOFOLLOW|O_NONBLOCK)
    guard fd>=0 else {throw BridgeError.failed};defer{Darwin.close(fd)}
    var st=stat();guard fstat(fd,&st)==0,(st.st_mode&S_IFMT)==S_IFREG,st.st_size<=8*1024*1024 else{throw ModelError.inputTooLarge}
    var data=Data(),buffer=[UInt8](repeating:0,count:8192)
    while true {let count=read(fd,&buffer,buffer.count);if count==0{break};guard count>0 else{throw BridgeError.failed};guard data.count+count<=8*1024*1024 else{throw ModelError.inputTooLarge};data.append(buffer,count:count)}
    return data
}
