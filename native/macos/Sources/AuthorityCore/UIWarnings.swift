import Foundation

/// Presentation vocabulary only. No production risk detector or authorization policy.
public enum WarningSeverity: String, CaseIterable {
    case information, attention, warning, critical
    public var label: String { L("warning." + rawValue) }
    public var glyph: String {
        switch self { case .information: return "ⓘ"; case .attention: return "◇"
        case .warning: return "⚠︎"; case .critical: return "‼︎" }
    }
    public var requestsPulse: Bool { self == .warning || self == .critical }
}

public enum WarningDataState { case current, missing, stale, notEvaluated }
public enum WarningOutcome: Equatable {
    case notAssessable, checkedClear, finding(WarningSeverity)
    public var label: String {
        switch self { case .notAssessable: return L("warning.notAssessable")
        case .checkedClear: return L("warning.checkedClear")
        case .finding(let severity): return severity.label }
    }
    public var glyph: String {
        switch self { case .notAssessable: return "?"; case .checkedClear: return "○"
        case .finding(let severity): return severity.glyph }
    }
    public var text: String { glyph + " " + label }
    public func shouldPulse(enabled: Bool, reduceMotion: Bool, visible: Bool) -> Bool {
        guard enabled, !reduceMotion, visible, case .finding(let severity) = self else { return false }
        return severity.requestsPulse
    }
}

public struct WarningAssessment {
    public var nodeID: String
    public var relationship: String?
    public var severity: WarningSeverity?
    public var dataState: WarningDataState
    public var checkPerformed: Bool
    public var reasonKey: String
    public var timestamp: String?
    public var sourceKey: String
    public var evidence: [String]
    public var isSynthetic: Bool

    public init(nodeID: String, relationship: String? = nil, severity: WarningSeverity? = nil,
                dataState: WarningDataState = .notEvaluated, checkPerformed: Bool = false,
                reasonKey: String = "warning.uncheckedReason", timestamp: String? = nil,
                sourceKey: String = "warning.noCheck", evidence: [String] = [], isSynthetic: Bool = false) {
        self.nodeID = nodeID; self.relationship = relationship; self.severity = severity
        self.dataState = dataState; self.checkPerformed = checkPerformed; self.reasonKey = reasonKey
        self.timestamp = timestamp; self.sourceKey = sourceKey; self.evidence = evidence; self.isSynthetic = isSynthetic
    }
    public var isAssessable: Bool { checkPerformed && dataState == .current }
    public var outcome: WarningOutcome {
        guard isAssessable else { return .notAssessable }
        return severity.map(WarningOutcome.finding) ?? .checkedClear
    }
}

/// Synthetic findings live outside GraphDocument, report imports and the engine.
public enum UIWarningDemo {
    public static let nodeIDs = ["root", "agent-001", "agent-002", "agent-003", "agent-004", "agent-005"]
    public static func assessments(for document: GraphDocument) -> [String: WarningAssessment] {
        guard document.isDemo else { return [:] }
        let ids = Set(document.nodes.map(\.id))
        var result: [String: WarningAssessment] = [:]
        for (index, id) in nodeIDs.enumerated() where ids.contains(id) {
            result[id] = WarningAssessment(nodeID: id,
                relationship: index == 2 ? "root → agent-002" : nil,
                severity: index < 4 ? WarningSeverity.allCases[index] : nil,
                dataState: index == 4 ? .missing : .current, checkPerformed: index != 4,
                reasonKey: "warning.demoReason.\(index)", timestamp: "2026-10-12T12:00:00Z",
                sourceKey: "warning.syntheticSource", evidence: index == 2 ? ["UI-DEMO-002"] : [], isSynthetic: true)
        }
        return result
    }
    public static func assessment(nodeID: String, in document: GraphDocument) -> WarningAssessment {
        assessments(for: document)[nodeID] ?? WarningAssessment(nodeID: nodeID)
    }
}
