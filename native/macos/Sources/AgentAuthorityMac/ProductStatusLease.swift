import Foundation

/// A display lease never gets younger after sleep or a partial clock rollback.
struct ProductStatusLease {
    private let startWall: TimeInterval
    private let startMono: TimeInterval
    private var lastWall: TimeInterval
    private var lastMono: TimeInterval
    private var age: TimeInterval = 0
    init(wall:TimeInterval = Date().timeIntervalSince1970, mono:TimeInterval = ProcessInfo.processInfo.systemUptime) {
        startWall = wall; startMono = mono; lastWall = wall; lastMono = mono
    }
    mutating func expired(wall:TimeInterval = Date().timeIntervalSince1970, mono:TimeInterval = ProcessInfo.processInfo.systemUptime) -> Bool {
        if ![startWall,startMono,wall,mono].allSatisfy({$0.isFinite}) || wall < lastWall || mono < lastMono {
            age = .infinity
        } else { age = max(age,wall-startWall,mono-startMono) }
        lastWall = wall; lastMono = mono
        return age >= 8
    }
}
