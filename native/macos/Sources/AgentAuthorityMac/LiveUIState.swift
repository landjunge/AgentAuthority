import AppKit

extension AppDelegate {
    /// Opt-in, bounded passive observation of normal startup. Never builds, fits,
    /// renders, navigates, changes data/preferences or terminates the application.
    func observeNormalStartup(_ url: URL, remaining: Int = 60) {
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
            guard let self else { return }
            let record = self.normalUIState()
            if let data = try? JSONSerialization.data(withJSONObject: record, options: [.prettyPrinted, .sortedKeys]) {
                try? data.write(to: url, options: .atomic)
            }
            if remaining > 1 { self.observeNormalStartup(url, remaining: remaining - 1) }
        }
    }
    func normalUIState() -> [String: Any] {
        let canvas = self.split.main.canvas
        let state = self.state
        let snapshot = self.split.main.navigationSnapshot()
        let record: [String: Any] = [
            "schema": "agent-authority-live-ui-state-v1",
            "time": Date().timeIntervalSince1970,
            "pid": ProcessInfo.processInfo.processIdentifier,
            "bundle": Bundle.main.bundleURL.path,
            "arguments": CommandLine.arguments,
            "source": state.document.source, "demo": state.document.isDemo,
            "source_nodes": state.document.nodes.count,
            "display_nodes": canvas.displayNodes.map(\.id),
            "last_draw_visible_count": canvas.visibleCount,
            "main_loaded": self.split.main.isViewLoaded,
            "canvas_attached": self.split.main.isViewLoaded && canvas.superview === self.split.main.view,
            "canvas_frame": NSStringFromRect(canvas.frame),
            "canvas_bounds": NSStringFromRect(canvas.bounds),
            "visible_rect": NSStringFromRect(canvas.visibleRect),
            "canvas_hidden": canvas.isHiddenOrHasHiddenAncestor,
            "main_frame": self.split.main.isViewLoaded ? NSStringFromRect(self.split.main.view.frame) : "not loaded",
            "split_frames": self.split.isViewLoaded ? self.split.splitView.subviews.map { NSStringFromRect($0.frame) } : [],
            "window_visible": self.window?.isVisible ?? false,
            "window_minimized": self.window?.isMiniaturized ?? false,
            "window_title": self.window?.title ?? "",
            "snapshot": ["mode": snapshot.mode, "anchor": snapshot.chainAnchor,
                "selection": snapshot.selection, "filter": snapshot.filter,
                "query": snapshot.query, "groups": snapshot.expandedGroups.sorted(),
                "zoom": snapshot.zoom, "pan_x": snapshot.panX, "pan_y": snapshot.panY],
            "history_count": state.history.count,
            "back_enabled": self.split.main.backEnabled,
            "demo_cases": self.split.main.demoCaseCount,
            "pulse_enabled": canvas.pulseEnabled,
            "reduce_motion": canvas.reduceMotion,
            "pulse_layers": canvas.activePulseCount,
            "critical_message_visible": self.split.main.criticalMessageVisible,
            "empty_message": canvas.displayNodes.isEmpty ? canvas.emptyMessage : ""
        ]
        return record
    }

}

func traceUIEvent(_ action:String,_ values:[String:Any]) {
    guard CommandLine.arguments.contains("--normal-state-json") else{return}
    let record:[String:Any]=["action":action,"time":Date().timeIntervalSince1970,"values":values]
    if let data=try? JSONSerialization.data(withJSONObject:record,options:[.sortedKeys]),let text=String(data:data,encoding:.utf8){print(text);fflush(stdout)}
}
