import AppKit
import AuthorityCore

enum Palette {
    static func adaptive(_ dark:String,_ light:String)->NSColor {NSColor(name:nil){ appearance in
        hex(appearance.bestMatch(from:[.darkAqua,.aqua]) == .darkAqua ? dark:light)
    }}
    static func hex(_ s:String)->NSColor {let v=UInt64(s,radix:16) ?? 0;return NSColor(srgbRed:Double((v>>16)&255)/255,green:Double((v>>8)&255)/255,blue:Double(v&255)/255,alpha:1)}
    // NetzwerkPunkt Bedienbasis 0.1 roles; native adaptive Light surfaces retained.
    static let background=adaptive("121316","f5f6f8"),surface=adaptive("1a1c20","ffffff"),raised=adaptive("25282e","eceef2")
    static let border=adaptive("353940","d8dce4"),accent=adaptive("edf0f4","172539"),muted=adaptive("afb6c1","5b6370")
    static let decoration = border.withAlphaComponent(0.35)
    static let wordmark = adaptive("ffffff", "17191f")
    static let brand = hex("3b78fc")
    static let green=adaptive("7bdaa7","246943"),amber=adaptive("e4be70","805f15"),risk=adaptive("f49b9b","963737")
    // Additional warning hues are native system colors, alongside existing ThreadDesk tokens.
    // Proof colors and their meaning are deliberately unchanged.
    static func warning(_ severity:WarningSeverity)->NSColor {
        switch severity {case .information:return .systemBlue;case .attention:return amber
        case .warning:return .systemOrange;case .critical:return risk}
    }
    static func warningOutcome(_ outcome:WarningOutcome)->NSColor {
        if case .finding(let severity)=outcome{return warning(severity)}
        return muted
    }
    static func status(_ value:ProofStatus)->NSColor {switch value{case .verified,.observed:return green;case .incomplete:return amber;case .contradictory:return risk;case .reported,.unknown:return muted}}
}
func label(_ key:String,size:CGFloat=12,weight:NSFont.Weight = .regular,color:NSColor = .labelColor)->NSTextField {
    let view=NSTextField(labelWithString:L(key));view.font = .systemFont(ofSize:size,weight:weight);view.textColor=color
    view.lineBreakMode = .byTruncatingTail;view.setContentCompressionResistancePriority(.defaultLow,for:.horizontal);return view
}
func wrapping(_ text:String,size:CGFloat=12,color:NSColor=Palette.muted)->NSTextField {
    let v=NSTextField(wrappingLabelWithString:text);v.font = .systemFont(ofSize:size);v.textColor=color;v.lineBreakMode = .byWordWrapping;return v
}
func button(_ key:String,target:AnyObject?,action:Selector,symbol:String?=nil)->NSButton {
    let b=NSButton(title:L(key),target:target,action:action);b.bezelStyle = .rounded;b.controlSize = .small
    if let symbol {b.image=NSImage(systemSymbolName:symbol,accessibilityDescription:L(key));b.imagePosition = .imageLeading}
    b.toolTip=L(key);return b
}
class SurfaceView:NSView {
    override init(frame:NSRect){super.init(frame:frame);clipsToBounds=true}
    required init?(coder:NSCoder){super.init(coder:coder);clipsToBounds=true}
    var color:NSColor=Palette.surface {didSet{needsDisplay=true}}
    var rounded:CGFloat=0
    override var isFlipped:Bool{true}
    override var wantsDefaultClipping:Bool{true}
    override func draw(_ dirtyRect:NSRect){color.setFill();NSBezierPath(roundedRect:bounds,xRadius:rounded,yRadius:rounded).fill();if rounded>0{Palette.decoration.setStroke();let p=NSBezierPath(roundedRect:bounds.insetBy(dx:0.5,dy:0.5),xRadius:rounded,yRadius:rounded);p.lineWidth=1;p.stroke()}}
}
