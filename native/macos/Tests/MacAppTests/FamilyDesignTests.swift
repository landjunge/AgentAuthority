import AppKit
import AuthorityCore
import XCTest
import CryptoKit
@testable import AgentAuthorityMac

final class FamilyDesignTests: XCTestCase {
    private func success(_ target: String = "threaddesk") -> [String: Any] {
        ["success": true, "active_product": target,
         "actual_outer_bounds": ["x": -1200, "y": 20, "width": 1150, "height": 730],
         "visible_family_windows": 1]
    }
    private func data(_ object: [String: Any]) throws -> Data { try JSONSerialization.data(withJSONObject: object) }

    func testFixedNativeArgumentsRejectPathsCommandsAndUnknownProducts() throws {
        for target in FamilySwitchClient.productIDs {
            XCTAssertEqual(try FamilySwitchClient.arguments(target: target, sourcePID: 123),
                ["--principal", "local", "family", "switch", target, "--source-pid", "123"])
        }
        for target in ["", "https://example.invalid", "threaddesk; open x", "/Applications/X.app", "unknown"] {
            XCTAssertThrowsError(try FamilySwitchClient.arguments(target: target, sourcePID: 123))
        }
        XCTAssertThrowsError(try FamilySwitchClient.arguments(target: "tollgate", sourcePID: 0))
    }

    func testBundledOriginalsMatchThePinnedSharedManifest() throws {
        let manifest = try XCTUnwrap(ProductHeaderAssetManifest.load())
        XCTAssertEqual(manifest.version, "1.2.0")
        XCTAssertEqual(manifest.files.map(\.appId), FamilySwitchClient.productIDs)
        for asset in manifest.files {
            let url = try XCTUnwrap(productHeaderResourceURL(asset.file, extension: nil))
            let digest = SHA256.hash(data: try Data(contentsOf: url)).map { String(format: "%02x", $0) }.joined()
            XCTAssertEqual(digest, asset.sha256)
            XCTAssertEqual(asset.viewport.count, 4)
        }
    }

    func testSuccessRequiresMatchingProductRealBoundsAndExactlyOneVisibleWindow() throws {
        XCTAssertNoThrow(try FamilySwitchClient.validateReply(data(success()), exitStatus: 0, target: "threaddesk"))
        var invalid: [[String: Any]] = [[:], ["ok": true], ["success": true]]
        for (key, value) in [("success", 1 as Any), ("active_product", "tollgate" as Any),
                             ("visible_family_windows", 2 as Any), ("visible_family_windows", true as Any),
                             ("execution_outcome_unknown", true as Any), ("error", ["code": "FAILED"] as Any)] {
            var row = success(); row[key] = value; invalid.append(row)
        }
        for bounds in [["x": 0, "y": 0, "width": 0, "height": 730] as [String: Any],
                       ["x": 0, "y": 0, "width": true, "height": 730],
                       ["x": "0", "y": 0, "width": 1150, "height": 730], ["width": 1150, "height": 730]] {
            var row = success(); row["actual_outer_bounds"] = bounds; invalid.append(row)
        }
        for row in invalid {
            XCTAssertThrowsError(try FamilySwitchClient.validateReply(data(row), exitStatus: 0, target: "threaddesk"))
        }
        XCTAssertThrowsError(try FamilySwitchClient.validateReply(data(success()), exitStatus: 1, target: "threaddesk"))
        XCTAssertThrowsError(try FamilySwitchClient.validateReply(Data("done".utf8), exitStatus: 0, target: "threaddesk"))
        XCTAssertThrowsError(try FamilySwitchClient.validateReply(Data(repeating: 32, count: 65537), exitStatus: 0, target: "threaddesk"))
    }

    func testNativeCallerPIDAndDoubleClickDoNotCreateTwoEffects() throws {
        let entered = expectation(description: "transport"), completed = expectation(description: "reply")
        let release = DispatchSemaphore(value: 0)
        let reply = try data(success())
        let client = FamilySwitchClient { url, argv in
            XCTAssertEqual(url, FamilySwitchClient.executableURL)
            XCTAssertEqual(argv, try FamilySwitchClient.arguments(target: "threaddesk", sourcePID: ProcessInfo.processInfo.processIdentifier))
            entered.fulfill(); _ = release.wait(timeout: .now() + 3); return (reply, 0)
        }
        client.switchProduct("threaddesk") { result in
            if case .failure = result { XCTFail("valid broker evidence rejected") }; completed.fulfill()
        }
        client.switchProduct("tollgate") { result in
            guard case .failure(FamilySwitchError.busy) = result else { XCTFail("duplicate effect admitted"); return }
        }
        wait(for: [entered], timeout: 2); release.signal(); wait(for: [completed], timeout: 2)
    }

    func testMissingBrokerAndUnknownReplyNeverBecomeSuccessOrAutoRetry() throws {
        for unavailable in [true, false] {
            let done = expectation(description: "failed switch")
            var calls = 0
            let client = FamilySwitchClient { _, _ in
                calls += 1
                if unavailable { throw FamilySwitchError.unavailable }
                return (Data("{\"success\":false,\"execution_outcome_unknown\":true}".utf8), 1)
            }
            client.switchProduct("threaddesk") { result in
                if case .success = result { XCTFail("failure became success") }; done.fulfill()
            }
            wait(for: [done], timeout: 2); XCTAssertEqual(calls, 1)
        }
    }

    func testHeaderRemainsCenteredAndOriginalButtonsStay44PointsInBothLanguages() throws {
        _ = NSApplication.shared
        let saved = Localization.shared.preference
        defer { Localization.shared.choose(saved, persist: false) }
        let header = FamilyHeaderView()
        for lang in ["de", "en"] {
            Localization.shared.choose(lang, persist: false); header.localize()
            for width: CGFloat in [900, 1120, 1150, 1360, 1680] {
                header.frame = NSRect(x: 0, y: 0, width: width, height: 64)
                header.needsLayout = true; header.layoutSubtreeIfNeeded()
                XCTAssertEqual(header.products.frame.midX, width/2, accuracy: 0.1)
                XCTAssertLessThan(header.wordmark.frame.maxX, header.products.frame.minX)
                XCTAssertGreaterThan(header.language.frame.minX, header.products.frame.maxX)
                XCTAssertEqual(header.products.arrangedSubviews.count, 5)
                for button in header.products.arrangedSubviews {
                    XCTAssertEqual(button.frame.width, 44, accuracy: 0.1)
                    XCTAssertEqual(button.frame.height, 44, accuracy: 0.1)
                    XCTAssertTrue((button as? NSButton)?.toolTip?.contains("·") == true)
                }
            }
        }
    }

    func testSmallSharedOuterFrameKeepsExistingSplitViewsAndAllowsEitherSidePane() {
        _ = NSApplication.shared
        let split = MainSplitController(AppState())
        let content = FamilyContentController(split: split)
        let root = content.view
        let originalMain = split.main.view
        root.frame = NSRect(x: 0, y: 0, width: 1120, height: 600)
        root.needsLayout = true; root.layoutSubtreeIfNeeded()
        XCTAssertEqual(split.splitViewItems.count, 3)
        XCTAssertTrue(split.splitViewItems[2].isCollapsed)
        split.toggleInspector()
        XCTAssertFalse(split.splitViewItems[2].isCollapsed)
        XCTAssertTrue(split.splitViewItems[0].isCollapsed)
        split.toggleSidebar()
        XCTAssertFalse(split.splitViewItems[0].isCollapsed)
        XCTAssertTrue(split.splitViewItems[2].isCollapsed)
        root.frame.size.width = 1360; root.needsLayout = true; root.layoutSubtreeIfNeeded()
        XCTAssertTrue(split.splitViewItems[2].isCollapsed, "manual choice must survive a size change")
        XCTAssertTrue(split.main.view === originalMain)
    }

    func testOnlyAutomaticInspectorCollapseIsRestoredOnWidening() {
        _ = NSApplication.shared
        let split = MainSplitController(AppState())
        _ = split.view
        XCTAssertFalse(split.splitViewItems[2].isCollapsed)
        split.adaptToFamilyWidth(1120)
        XCTAssertTrue(split.splitViewItems[2].isCollapsed)
        split.adaptToFamilyWidth(1360)
        XCTAssertFalse(split.splitViewItems[2].isCollapsed)
        split.toggleInspector()
        split.adaptToFamilyWidth(1120); split.adaptToFamilyWidth(1360)
        XCTAssertTrue(split.splitViewItems[2].isCollapsed)
    }

    func testHideAndReopenUseStoredMainWindowAndPreserveStateAndViews() throws {
        _ = NSApplication.shared
        let app = AppDelegate()
        app.applicationDidFinishLaunching(Notification(name: NSApplication.didFinishLaunchingNotification))
        defer { app.window.orderOut(nil); app.settingsWindow?.orderOut(nil)
            if let observer = app.observer { NotificationCenter.default.removeObserver(observer) } }
        let canvas = app.split.main.canvas, document = app.state.document
        app.state.query = "held-filter"; app.state.selected = "agent-007"; app.state.expandedGroups = ["group"]
        canvas.scale = 0.75; canvas.offset = NSPoint(x: 31, y: 19)
        let frame = app.window.frame
        app.settings()
        app.hideForFamilySwitch()
        XCTAssertTrue(app.applicationShouldTerminateAfterLastWindowClosed(NSApp))
        XCTAssertFalse(app.applicationShouldHandleReopen(NSApp, hasVisibleWindows: false))
        XCTAssertTrue(app.window.isVisible)
        XCTAssertTrue(app.window.contentViewController === app.familyContent)
        XCTAssertTrue(app.split.main.canvas === canvas)
        XCTAssertEqual(app.state.document.nodes.count, document.nodes.count)
        XCTAssertEqual(app.state.query, "held-filter"); XCTAssertEqual(app.state.selected, "agent-007")
        XCTAssertEqual(app.state.expandedGroups, ["group"])
        XCTAssertEqual(canvas.scale, 0.75); XCTAssertEqual(canvas.offset, NSPoint(x: 31, y: 19))
        XCTAssertEqual(app.window.frame, frame)
        let cards = app.split.main.view.subviews.compactMap { $0 as? MetricView }
        XCTAssertEqual(cards.count, 4); XCTAssertTrue(cards.allSatisfy { $0.frame.height == 66 })
    }
}
