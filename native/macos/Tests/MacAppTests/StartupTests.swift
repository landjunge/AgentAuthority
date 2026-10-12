import AppKit
import XCTest
import AuthorityCore
@testable import AgentAuthorityMac

final class StartupTests: XCTestCase {
    func testPassiveDiagnosticsDoNotLoadOrBuildMissingViews() {
        _ = NSApplication.shared
        let app = AppDelegate()
        app.split = MainSplitController(app.state)
        XCTAssertFalse(app.split.isViewLoaded)
        XCTAssertFalse(app.split.main.isViewLoaded)
        let record = app.normalUIState()
        XCTAssertEqual(record["main_loaded"] as? Bool, false)
        XCTAssertEqual(record["canvas_attached"] as? Bool, false)
        XCTAssertFalse(app.split.isViewLoaded)
        XCTAssertFalse(app.split.main.isViewLoaded)
    }

    func testInitialViewLoadsGraphWithoutExplicitRebuild() {
        _ = NSApplication.shared
        let state = AppState()
        let main = MainPanelController(state)
        let root = main.view
        root.frame = NSRect(x: 0, y: 0, width: 1000, height: 780)
        root.layoutSubtreeIfNeeded()
        XCTAssertTrue(main.canvas.superview === root)
        XCTAssertFalse(main.canvas.displayNodes.isEmpty)
        XCTAssertGreaterThan(main.canvas.bounds.width, 600)
        XCTAssertGreaterThan(main.canvas.bounds.height, 100)
        XCTAssertEqual(main.demoCaseCount, 6)
    }

    func testEmptySourceAndFilteredDemoRemainDistinguishable() {
        _ = NSApplication.shared
        let state = AppState()
        state.document = GraphDocument(source: "empty-real")
        state.selected = ""; state.graphMode = 0
        let main = MainPanelController(state)
        _ = main.view
        XCTAssertTrue(main.canvas.displayNodes.isEmpty)
        XCTAssertEqual(main.canvas.emptyMessage, L("graph.sourceEmpty"))
        XCTAssertFalse(main.state.document.isDemo)
        XCTAssertEqual(main.demoCaseCount, 0)
        state.document = DemoData.make()
        state.graphMode = 2; state.query = "no-matching-node-xyz"
        main.build()
        XCTAssertTrue(main.canvas.displayNodes.isEmpty)
        XCTAssertEqual(main.canvas.emptyMessage, L("graph.filteredEmpty"))
    }

    func testNormalAppLaunchAndSidebarNavigationWithoutDiagnosticRebuild() {
        _ = NSApplication.shared
        let app = AppDelegate()
        app.applicationDidFinishLaunching(Notification(name: NSApplication.didFinishLaunchingNotification))
        defer { app.window.close(); if let observer = app.observer { NotificationCenter.default.removeObserver(observer) } }
        let main = app.split.main
        XCTAssertFalse(main.canvas.displayNodes.isEmpty)
        XCTAssertGreaterThan(main.canvas.bounds.width, 600)
        XCTAssertGreaterThan(main.canvas.bounds.height, 100)
        app.navigate("overview")
        app.navigate("graph")
        XCTAssertFalse(main.canvas.displayNodes.isEmpty)
        XCTAssertTrue(main.canvas.superview === main.view)
        XCTAssertTrue(main.canvas.scale.isFinite)
        XCTAssertTrue(main.canvas.offset.x.isFinite)
        XCTAssertTrue(main.canvas.offset.y.isFinite)
    }
}
