import AppKit
import AuthorityCore

/// Opt-in native UI regression diagnostics. No permission requests or experiments.
extension AppDelegate {
    func runUIRegression() -> [String: Any] {
        let main = split.main, canvas = main.canvas
        var checks: [String: Bool] = [:]
        let originalDocument = state.document
        let original = main.navigationSnapshot()
        let originalPulse = canvas.pulseEnabled
        func settle() { main.view.needsLayout = true; main.view.layoutSubtreeIfNeeded(); canvas.updateWarningPulses() }

        state.document = DemoData.make()
        state.graphMode = 1; state.selected = "agent-013"; state.chainAnchor = "agent-013"
        state.filter = 2; state.query = "AA"; state.expandedGroups = ["branch-0", "branch-2"]
        main.build(); settle()
        canvas.scale = 0.8123456789; canvas.offset = NSPoint(x: -137.125, y: 92.875)
        let first = main.navigationSnapshot()
        checks["viewport_changes_do_not_record"] = state.history.count == 0 && !main.backEnabled
        canvas.onFocus?("agent-002"); settle()
        canvas.zoom(1.15); canvas.offset = NSPoint(x: 93.25, y: -120.5)
        let second = main.navigationSnapshot()
        canvas.onFocus?("agent-003"); settle()
        canvas.scale = 1.23456789; canvas.offset = NSPoint(x: -30.375, y: 59.0625)
        let third = main.navigationSnapshot()
        canvas.onFocus?("agent-005"); settle()
        checks["three_focus_steps"] = state.history.count == 3 && main.backEnabled
        main.goBack(); settle()
        checks["back_1_exact_all_fields"] = main.navigationSnapshot() == third && state.history.count == 2
        main.goBack(); settle()
        checks["back_2_exact_all_fields"] = main.navigationSnapshot() == second && state.history.count == 1
        main.goBack(); settle()
        checks["back_3_exact_all_fields_no_autofit"] = main.navigationSnapshot() == first && state.history.count == 0 && !main.backEnabled
        main.goBack(); settle()
        checks["empty_back_is_noop"] = main.navigationSnapshot() == first && state.history.count == 0

        // The actual cluster expansion callback also participates in history.
        state.graphMode = 2; state.filter = 0; state.query = ""; state.expandedGroups = []
        main.build(); settle()
        canvas.scale = 0.9123456; canvas.offset = NSPoint(x: -15.25, y: 80.5)
        let collapsed = main.navigationSnapshot()
        canvas.onExpand?("cluster:branch-0"); settle()
        checks["expansion_is_one_step"] = state.expandedGroups.contains("branch-0") && state.history.count == 1
        main.goBack(); settle()
        checks["back_restores_collapsed_groups_and_viewport"] = main.navigationSnapshot() == collapsed

        state.graphMode = 1; main.build(); main.updateGraph(fit: true); settle()
        checks["all_six_demo_cases_available"] = main.demoCaseCount == 6
        let expected: [WarningOutcome] = [.finding(.information), .finding(.attention), .finding(.warning), .finding(.critical), .notAssessable, .checkedClear]
        for (index, id) in UIWarningDemo.nodeIDs.enumerated() {
            checks["demo_case_\(index)_separate"] = canvas.warningOutcome(id) == expected[index]
        }
        checks["critical_has_persistent_message"] = main.criticalMessageVisible
        checks["critical_does_not_change_verified_proof"] = state.document.chainStatuses()["agent-003"] == .verified && Palette.status(.verified) == Palette.green
        canvas.pulseEnabled = true; canvas.forceReduceMotion = false; canvas.updateWarningPulses()
        let pulsing = canvas.activePulseCount
        checks["local_visible_warning_pulses"] = canvas.reduceMotion ? pulsing == 0 : pulsing == 2
        canvas.pulseEnabled = false
        checks["pulse_toggle_removes_animation"] = canvas.activePulseCount == 0
        canvas.pulseEnabled = true; canvas.forceReduceMotion = true
        checks["reduced_motion_removes_animation"] = canvas.activePulseCount == 0
        checks["reduced_motion_keeps_warning_and_message"] = canvas.warningOutcome("agent-003") == .finding(.critical) && main.criticalMessageVisible
        canvas.forceReduceMotion = false
        canvas.offset = NSPoint(x: -100000, y: -100000)
        checks["offscreen_nodes_have_no_animation"] = canvas.activePulseCount == 0

        main.focus("agent-002")
        state.document = GraphDocument(source: "regression-real", nodes: [GraphNode(id: "real", kind: .action, name: "real", status: .observed)])
        state.selected = "real"; state.graphMode = 0; main.build(); settle()
        checks["source_change_resets_navigation"] = state.history.count == 0 && !main.backEnabled
        checks["real_data_neutral_without_check"] = canvas.warningOutcome("real") == .notAssessable && !main.criticalMessageVisible && main.demoCaseCount == 0
        checks["real_observed_proof_unchanged"] = state.document.nodes[0].status == .observed

        // Restore the diagnostic window for optional subsequent native captures.
        state.document = originalDocument
        state.graphMode = original.mode; state.chainAnchor = original.chainAnchor; state.selected = original.selection
        state.filter = original.filter; state.query = original.query; state.expandedGroups = original.expandedGroups
        main.build(); settle(); canvas.scale = original.zoom; canvas.offset = NSPoint(x: original.panX, y: original.panY)
        canvas.pulseEnabled = originalPulse; split.inspector.reload()
        return ["checks": checks, "passed": checks.values.allSatisfy { $0 }, "check_count": checks.count,
                "method": "actual AppKit controllers, focus/expansion callbacks, Back action and local animation layers",
                "system_reduce_motion": NSWorkspace.shared.accessibilityDisplayShouldReduceMotion,
                "observed_visible_pulse_layers": pulsing, "permissions_or_experiments_started": false]
    }
}
