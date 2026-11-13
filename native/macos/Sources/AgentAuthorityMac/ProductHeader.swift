import AppKit
import AuthorityCore

/// UI metadata only. No collector, process or transport state is inferred.
final class ProductHeaderView: NSStackView {
    private let names = ["KiraBridge", "ThreadDesk", "4AllPass", "TollGate", "Agent Authority"]
    private let ids = FamilySwitchClient.productIDs
    var onOpen: ((String) -> Void)?
    var onDetail: ((String) -> Void)?

    private var buttons: [ProductIconButton] = []
    private var observer: NSObjectProtocol?
    private var statusObserver: NSObjectProtocol?
    private var expiry: Timer?
    private var lease: ProductStatusLease?
    private var connectionState = "unknown"
    init() {
        super.init(frame:.zero)
        orientation = .horizontal; alignment = .centerY; spacing = 4
        wantsLayer = true; layer?.backgroundColor = NSColor.clear.cgColor
        edgeInsets = NSEdgeInsets(top:0,left:0,bottom:0,right:0)
        let assets = ProductHeaderAssetManifest.load()?.files ?? []
        for index in ids.indices {
            let button = ProductIconButton(title:"",target:self,action:#selector(openProduct(_:)))
            button.identifier = NSUserInterfaceItemIdentifier(ids[index]); button.onFocus = { [weak self] text in self?.onDetail?(text) }; button.tag = index; button.isBordered = false; button.focusRingType = .exterior
            if let asset = assets.first(where: { $0.appId == ids[index] }), asset.viewport.count == 4,
               asset.viewport.allSatisfy({ $0.isFinite && $0 >= 0 }), asset.viewport[2] > 0, asset.viewport[3] > 0,
               let url = productHeaderResourceURL(asset.file, extension: nil) {
                button.crop = NSRect(x:asset.viewport[0], y:asset.viewport[1], width:asset.viewport[2], height:asset.viewport[3])
                button.original = NSImage(contentsOf:url); button.original?.size = NSSize(width:256,height:256)
            }
            button.translatesAutoresizingMaskIntoConstraints = false
            NSLayoutConstraint.activate([button.widthAnchor.constraint(equalToConstant:44),button.heightAnchor.constraint(equalToConstant:44)])
            addArrangedSubview(button); buttons.append(button)
        }
        localize()
        statusObserver = NotificationCenter.default.addObserver(forName:Notification.Name("AgentAuthorityCollectorStatus"),object:nil,queue:.main){[weak self] note in
            guard let self,let state = note.userInfo?["state"] as? String,["confirmed","error","unknown"].contains(state) else{return}
            self.connectionState = state;self.lease = ProductStatusLease();self.localize()
        }
        expiry = Timer.scheduledTimer(withTimeInterval:0.5,repeats:true){[weak self]_ in
            guard let self else{return}
            if self.lease?.expired() == true {self.connectionState = "unknown";self.lease = nil;self.localize()}
        }
        observer = NotificationCenter.default.addObserver(forName:Localization.changed,object:nil,queue:.main){[weak self]_ in self?.localize()}
    }
    required init?(coder:NSCoder){fatalError("init(coder:) has not been implemented")}
    deinit { expiry?.invalidate(); if let observer { NotificationCenter.default.removeObserver(observer) };if let statusObserver { NotificationCenter.default.removeObserver(statusObserver) } }
    func localize() {
        for index in buttons.indices {
            let version = index == 4 ? Bundle.main.object(forInfoDictionaryKey:"CFBundleShortVersionString") as? String : nil
            let state = index == 4 ? connectionState : "unknown"
            buttons[index].stateText = state
            let status = L(state == "confirmed" ? "family.collectorConfirmed" : state == "error" ? "family.collectorError" : "family.unknown")
            let text = names[index] + " · " + status + " · " + (version.map {L("family.version", ["version":$0])} ?? L("family.versionUnknown"))
            buttons[index].toolTip = text; buttons[index].setAccessibilityLabel(text); buttons[index].needsDisplay = true
        }
        setAccessibilityLabel(L("family.products"))
    }

    @objc private func openProduct(_ button:NSButton) {
        guard ids.indices.contains(button.tag) else { return }
        onOpen?(ids[button.tag])
    }
}

private final class ProductIconButton: NSButton {
    var onFocus: ((String) -> Void)?
    var original: NSImage?
    var crop = NSRect.zero
    var stateText = "unknown"
    override var acceptsFirstResponder: Bool { true }
    override func becomeFirstResponder() -> Bool {
        let accepted = super.becomeFirstResponder()
        if accepted { onFocus?(toolTip ?? ""); needsDisplay = true }
        return accepted
    }
    override func resignFirstResponder() -> Bool {
        let accepted = super.resignFirstResponder(); needsDisplay = true; return accepted
    }
    override func keyDown(with event:NSEvent) {
        if event.keyCode == 36 || event.keyCode == 49 { performClick(nil) } else { super.keyDown(with:event) }
    }
    override func draw(_ dirtyRect:NSRect) {
        let frame = NSRect(x:3,y:3,width:38,height:38)
        NSColor.clear.setStroke()
        let border = NSBezierPath(rect:frame.insetBy(dx:0.5,dy:0.5))
        if stateText == "confirmed" {
            NSGraphicsContext.saveGraphicsState()
            let accent = NSColor(srgbRed:59/255,green:120/255,blue:252/255,alpha:1)
            accent.withAlphaComponent(0.35).setStroke(); let shadow = NSShadow();shadow.shadowColor = accent.withAlphaComponent(0.10);shadow.shadowBlurRadius = 4;shadow.set();border.stroke()
            NSGraphicsContext.restoreGraphicsState()
        } else {
            if stateText == "error" { NSColor.systemRed.setStroke() } else { border.setLineDash([1,2],count:2,phase:0) }
            border.stroke()
        }
        if let original, crop.width > 0, crop.height > 0 {
            let scale = 32 / max(crop.width,crop.height)
            let target = NSRect(x:frame.midX-crop.width*scale/2,y:frame.midY-crop.height*scale/2,width:crop.width*scale,height:crop.height*scale)
            let source = NSRect(x:crop.minX,y:256-crop.maxY,width:crop.width,height:crop.height)
            original.draw(in:target,from:source,operation:.sourceOver,fraction:1,respectFlipped:true,hints:nil)
        }
        if window?.firstResponder === self {
            NSColor.labelColor.setStroke();let focus = NSBezierPath(rect:bounds.insetBy(dx:1,dy:1));focus.lineWidth = 2;focus.stroke()
        }
        if isHighlighted { NSColor(calibratedWhite:1,alpha:0.12).setFill(); bounds.fill() }
    }
}

// Consume the pinned shared manifest, rather than maintaining a second set of crop rectangles.
struct ProductHeaderAssetManifest: Decodable {
    struct Asset: Decodable {
        let appId: String
        let file: String
        let sha256: String
        let viewport: [Double]
    }
    let version: String
    let files: [Asset]
    static func load() -> ProductHeaderAssetManifest? {
        guard let url = productHeaderResourceURL("networkpunkt-appbar-assets", extension: "json"),
              let data = try? Data(contentsOf:url) else { return nil }
        return try? JSONDecoder().decode(Self.self, from:data)
    }
}

func productHeaderResourceURL(_ name: String, extension ext: String?) -> URL? {
    // Packaged apps must resolve their own resources, never a historical checkout fallback.
    if Bundle.main.bundleURL.pathExtension == "app" {
        return Bundle.main.url(forResource:name, withExtension:ext, subdirectory:"ProductHeader")
    }
    return Bundle.module.url(forResource:name, withExtension:ext, subdirectory:"ProductHeader")
}
