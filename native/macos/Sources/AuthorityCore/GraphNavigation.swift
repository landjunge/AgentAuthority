import Foundation

/// Value snapshot; viewport changes alone never push a navigation entry.
public struct GraphNavigationState: Equatable {
    public var mode: Int
    public var chainAnchor: String
    public var selection: String
    public var filter: Int
    public var query: String
    public var expandedGroups: Set<String>
    public var zoom: Double
    public var panX: Double
    public var panY: Double

    public init(mode: Int, chainAnchor: String, selection: String, filter: Int,
                query: String, expandedGroups: Set<String>, zoom: Double, panX: Double, panY: Double) {
        self.mode = mode; self.chainAnchor = chainAnchor; self.selection = selection
        self.filter = filter; self.query = query; self.expandedGroups = expandedGroups
        self.zoom = zoom; self.panX = panX; self.panY = panY
    }
}

public struct GraphNavigationHistory {
    private var entries: [GraphNavigationState] = []
    public init() {}
    public var canGoBack: Bool { !entries.isEmpty }
    public var count: Int { entries.count }
    public mutating func record(_ state: GraphNavigationState) { entries.append(state) }
    public mutating func back() -> GraphNavigationState? { entries.popLast() }
    public mutating func reset() { entries.removeAll() }
}
