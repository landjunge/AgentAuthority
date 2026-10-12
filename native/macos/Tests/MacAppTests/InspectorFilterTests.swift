import AppKit
import XCTest
import AuthorityCore
@testable import AgentAuthorityMac

final class InspectorFilterTests: XCTestCase {
    private func descendants(_ view: NSView) -> [NSView] {
        [view] + view.subviews.flatMap(descendants)
    }

    func testProofFilterUsesTheChainStatusDisplayedOnAgentCards() throws {
        _ = NSApplication.shared
        let state = AppState()
        state.graphMode = 1
        let main = MainPanelController(state)
        let filter = try XCTUnwrap(main.view.subviews.compactMap { $0 as? NSPopUpButton }
            .first { $0.itemTitles.contains(L("graph.all")) })
        // AA-027 has verified local identity but an incomplete parent chain.
        XCTAssertEqual(state.document.chainStatuses()["agent-027"], .incomplete)
        filter.selectItem(at: 1)
        XCTAssertTrue(filter.sendAction(filter.action, to: filter.target))
        XCTAssertTrue(main.canvas.displayNodes.contains { $0.id == "agent-027" })
        filter.selectItem(at: 2)
        XCTAssertTrue(filter.sendAction(filter.action, to: filter.target))
        XCTAssertFalse(main.canvas.displayNodes.contains { $0.id == "agent-027" })
        // Independent warning severity must not influence the proof filter.
        XCTAssertTrue(main.canvas.displayNodes.contains { $0.id == "agent-003" })
        XCTAssertEqual(main.canvas.warningOutcome("agent-003"), .finding(.critical))
    }

    func testRawInspectorPreservesRealVersusSyntheticSourceBoundary() throws {
        _ = NSApplication.shared
        for (demo, reported, boundary) in [(true, false, "boundary.sample"),
                                         (false, false, "boundary.live"),
                                         (false, true, "boundary.product")] {
            let state = AppState()
            state.document = GraphDocument(source: "inspector-regression", demo: demo,
                nodes: [GraphNode(id: "n", kind: .action, name: "n", status: .observed)])
            if reported { state.document.reportJSON = "{}" }
            state.selected = "n"
            let inspector = InspectorController(state)
            let tabs = try XCTUnwrap(descendants(inspector.view).compactMap { $0 as? NSSegmentedControl }.first)
            tabs.selectedSegment = 1
            XCTAssertTrue(tabs.sendAction(tabs.action, to: tabs.target))
            let texts = descendants(inspector.view).compactMap { ($0 as? NSTextField)?.stringValue }
            XCTAssertTrue(texts.contains(L(boundary)), "Wrong raw inspector source boundary: \(boundary)")
            if !demo { XCTAssertFalse(texts.contains(L("boundary.sample"))) }
        }
    }
}
