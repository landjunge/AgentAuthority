import XCTest
@testable import AuthorityCore

final class NavigationWarningTests: XCTestCase {
    private func state(_ id: String, zoom: Double, x: Double, y: Double) -> GraphNavigationState {
        GraphNavigationState(mode: id == "root" ? 2 : 0, chainAnchor: id, selection: id,
            filter: 1, query: "Änderung", expandedGroups: ["branch-0", "branch-2"],
            zoom: zoom, panX: x, panY: y)
    }
    func testMultipleBackStepsRestoreEveryFieldWithoutRecordingRestores() {
        var history = GraphNavigationHistory()
        let first = state("root", zoom: 0.731234567, x: -203.125, y: 77.875)
        let second = state("agent-002", zoom: 1.23456789, x: 93.25, y: -120.5)
        XCTAssertFalse(history.canGoBack)
        history.record(first); history.record(second)
        XCTAssertEqual(history.back(), second); XCTAssertEqual(history.count, 1)
        XCTAssertEqual(history.back(), first); XCTAssertFalse(history.canGoBack)
        XCTAssertNil(history.back())
    }
    func testViewportChangesDoNotImplicitlyRecordAndSourceResetInvalidatesHistory() {
        var history = GraphNavigationHistory()
        var viewport = state("root", zoom: 1, x: 0, y: 0)
        viewport.zoom = 2; viewport.panX = -999; viewport.panY = 400
        XCTAssertFalse(history.canGoBack)
        history.record(viewport); history.reset()
        XCTAssertNil(history.back())
    }
    func testClearRequiresExplicitCheckAndCurrentRequiredDataForEverySeverity() {
        for severity in [nil] + WarningSeverity.allCases.map(Optional.some) {
            for data in [WarningDataState.missing, .stale, .notEvaluated, .current] {
                for performed in [false, true] {
                    let a = WarningAssessment(nodeID: "n", severity: severity, dataState: data, checkPerformed: performed)
                    XCTAssertEqual(a.severity, severity)
                    XCTAssertEqual(a.isAssessable, performed && data == .current)
                    XCTAssertEqual(a.outcome, performed && data == .current ? severity.map(WarningOutcome.finding) ?? .checkedClear : .notAssessable)
                }
            }
        }
    }
    func testSixSyntheticCasesRemainSeparateFromRealDataAndProof() {
        var d = DemoData.make()
        let originalNodes = d.nodes, originalEdges = d.edges
        let cases = UIWarningDemo.assessments(for: d)
        XCTAssertEqual(cases.count, 6)
        XCTAssertEqual(Set(cases.values.compactMap(\.severity)), Set(WarningSeverity.allCases))
        XCTAssertEqual(cases["agent-004"]?.outcome, .notAssessable)
        XCTAssertEqual(cases["agent-005"]?.outcome, .checkedClear)
        XCTAssertTrue(cases.values.allSatisfy(\.isSynthetic))
        for a in cases.values { XCTAssertNotNil(Localization().catalog[a.reasonKey]) }
        XCTAssertEqual(cases["agent-003"]?.evidence, [])
        XCTAssertNotNil(cases["agent-002"]?.relationship)
        // A critical warning coexists with verified proof; no status mutation or inference.
        XCTAssertEqual(d.nodes.first { $0.id == "agent-003" }?.status, .verified)
        for index in d.nodes.indices { d.nodes[index].status = .contradictory }
        XCTAssertEqual(UIWarningDemo.assessments(for: d)["agent-005"]?.outcome, .checkedClear)
        d.isDemo = false
        XCTAssertTrue(UIWarningDemo.assessments(for: d).isEmpty)
        for node in d.nodes {
            let a = UIWarningDemo.assessment(nodeID: node.id, in: d)
            XCTAssertEqual(a.outcome, .notAssessable); XCTAssertFalse(a.isSynthetic)
            XCTAssertNil(a.severity); XCTAssertNil(a.timestamp); XCTAssertTrue(a.evidence.isEmpty)
        }
        let unmodified = DemoData.make()
        XCTAssertEqual(originalNodes, unmodified.nodes); XCTAssertEqual(originalEdges, unmodified.edges)
    }
    func testPulsePolicyPreservesAllLabelsAndRespectsVisibilityAndReducedMotion() {
        let outcomes: [WarningOutcome] = [.notAssessable, .checkedClear] + WarningSeverity.allCases.map(WarningOutcome.finding)
        for outcome in outcomes {
            XCTAssertFalse(outcome.shouldPulse(enabled: false, reduceMotion: false, visible: true))
            XCTAssertFalse(outcome.shouldPulse(enabled: true, reduceMotion: true, visible: true))
            XCTAssertFalse(outcome.shouldPulse(enabled: true, reduceMotion: false, visible: false))
            XCTAssertEqual(outcome.shouldPulse(enabled: true, reduceMotion: false, visible: true), outcome == .finding(.warning) || outcome == .finding(.critical))
            XCTAssertFalse(outcome.glyph.isEmpty); XCTAssertFalse(outcome.label.isEmpty)
        }
    }
}
