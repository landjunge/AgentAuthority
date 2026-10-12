import AppKit
import AuthorityCore
import QuartzCore

final class GraphCanvas:NSView {
    var document=GraphDocument(source:"")
    var displayNodes:[GraphNode]=[],displayEdges:[GraphEdge]=[]
    var layout=GraphLayout.make(nodes:[],edges:[])
    var selected:String?;var onSelect:((String)->Void)?;var onFocus:((String)->Void)?
    var onExpand:((String)->Void)?;var onChange:(()->Void)?
    var scale:CGFloat=1{didSet{updateWarningPulses()}};var offset=NSPoint.zero{didSet{updateWarningPulses()}}
    var pulseEnabled=UserDefaults.standard.object(forKey:"warningPulseEnabled") as? Bool ?? true{didSet{updateWarningPulses()}}
    // Diagnostics can force reduced motion on, but can never bypass the system setting.
    var forceReduceMotion=false{didSet{updateWarningPulses()}}
    var reduceMotion:Bool{forceReduceMotion || NSWorkspace.shared.accessibilityDisplayShouldReduceMotion}
    private var motionObserver:NSObjectProtocol?
    private var visibilityObservers:[NSObjectProtocol]=[]
    private var warningOutcomes:[String:WarningOutcome]=[:]
    private var pulseViews:[String:WarningPulseView]=[:]
    var activePulseCount:Int{pulseViews.count}
    func warningOutcome(_ id:String)->WarningOutcome{warningOutcomes[id] ?? .notAssessable}
    var compact=true
    private var dragPoint:NSPoint?;private var originalOffset=NSPoint.zero
    private var pressed:String?
    private var buckets:[String:[String]]=[:]
    private var nodeByID:[String:GraphNode]=[:]
    private var chainStatus:[String:ProofStatus]=[:]
    private var tracking:NSTrackingArea?
    var visibleCount=0
    private(set) var agentOverview=false
    private var gridColumns=5
    let card=NSSize(width:138,height:48)
    override var isFlipped:Bool{true}
    override var wantsDefaultClipping:Bool{true}
    override var acceptsFirstResponder:Bool{true}
    override init(frame:NSRect){super.init(frame:frame);clipsToBounds=true;setAccessibilityLabel(L("graph.title"));setAccessibilityRole(.group)
        motionObserver=NSWorkspace.shared.notificationCenter.addObserver(forName:NSWorkspace.accessibilityDisplayOptionsDidChangeNotification,object:nil,queue:.main){[weak self]_ in self?.updateWarningPulses()}
        for name in [NSWindow.didChangeOcclusionStateNotification,NSWindow.didMiniaturizeNotification,NSWindow.didDeminiaturizeNotification] {
            visibilityObservers.append(NotificationCenter.default.addObserver(forName:name,object:nil,queue:.main){[weak self] note in guard let self,note.object as? NSWindow === self.window else{return};self.updateWarningPulses()})
        }
    }
    deinit{visibilityObservers.forEach{NotificationCenter.default.removeObserver($0)};if let motionObserver{NSWorkspace.shared.notificationCenter.removeObserver(motionObserver)}}
    override func viewDidMoveToWindow(){super.viewDidMoveToWindow();updateWarningPulses()}
    override func setFrameSize(_ newSize:NSSize){super.setFrameSize(newSize);updateWarningPulses()}
    required init?(coder:NSCoder){fatalError()}
    func setGraph(nodes:[GraphNode],edges:[GraphEdge],fit:Bool=true,agentOverview:Bool=false){
        self.agentOverview=agentOverview
        let assessments=UIWarningDemo.assessments(for:document)
        warningOutcomes=Dictionary(uniqueKeysWithValues:nodes.map{node -> (String,WarningOutcome) in
            if node.kind == .cluster {
                let members=document.nodes.filter{$0.group==node.group && $0.kind == .agent}
                let findings=members.compactMap{assessments[$0.id]?.outcome}.compactMap{outcome -> WarningSeverity? in if case .finding(let severity)=outcome{return severity};return nil}
                let highest=findings.max{WarningSeverity.allCases.firstIndex(of:$0)! < WarningSeverity.allCases.firstIndex(of:$1)!}
                return (node.id,highest.map(WarningOutcome.finding) ?? .notAssessable)
            }
            return (node.id,assessments[node.id]?.outcome ?? .notAssessable)
        })
        chainStatus=document.chainStatuses()
        displayNodes=nodes;displayEdges=edges;nodeByID=Dictionary(uniqueKeysWithValues:nodes.map{($0.id,$0)})
        layout=agentOverview ? GraphLayout.agents(nodes,columns:gridColumns):GraphLayout.make(nodes:nodes,edges:edges);buckets=[:]
        for (id,p) in layout.positions {buckets[bucket(p.x,p.y),default:[]].append(id)}
        if fit{fitGraph()}else{needsDisplay=true};updateAccessibility();updateWarningPulses();onChange?()
    }
    func useColumns(_ count:Int,fit:Bool=true){guard agentOverview,count != gridColumns else{return};gridColumns=count;layout=GraphLayout.agents(displayNodes,columns:count);buckets=[:];for (id,p) in layout.positions{buckets[bucket(p.x,p.y),default:[]].append(id)};if fit{fitGraph()};needsDisplay=true;updateWarningPulses()}
    private func bucket(_ x:Double,_ y:Double)->String{"\(Int(floor(x/172))):\(Int(floor(y/70)))"}
    private func frame(_ id:String)->NSRect {guard let p=layout.positions[id]else{return .zero};return NSRect(x:p.x,y:p.y,width:card.width,height:card.height)}
    func fitGraph(){guard bounds.width>0,bounds.height>0 else{return};let w=CGFloat(layout.width),h=CGFloat(layout.height);scale=min(1.15,max(0.15,min((bounds.width-40)/w,(bounds.height-55)/h)));offset=NSPoint(x:max(CGFloat(12),(bounds.width-w*scale)/CGFloat(2)),y:20);needsDisplay=true;onChange?()}
    func zoom(_ multiplier:CGFloat){traceUIEvent("zoom",["multiplier":Double(multiplier),"zoom_before":Double(scale)]);let next=min(3,max(0.15,scale*multiplier));let center=NSPoint(x:bounds.midX,y:bounds.midY);offset=NSPoint(x:center.x-(center.x-offset.x)*next/scale,y:center.y-(center.y-offset.y)*next/scale);scale=next;needsDisplay=true;updateAccessibility();onChange?()}
    func select(_ id:String){selected=id;needsDisplay=true;onSelect?(id);updateAccessibility()}
    func center(_ id:String){guard let p=layout.positions[id]else{return};scale=max(0.85,scale);offset=NSPoint(x:bounds.midX-(p.x+Double(card.width/2))*scale,y:bounds.midY-(p.y+Double(card.height/2))*scale);needsDisplay=true;onChange?()}
    private func localPoint(_ p:NSPoint)->NSPoint{NSPoint(x:(p.x-offset.x)/scale,y:(p.y-offset.y)/scale)}
    private func hit(_ p:NSPoint)->String? {let q=localPoint(p)
        for dx in [-1,0,1] {for dy in [-1,0,1] {for id in buckets[bucket(Double(q.x)+Double(dx)*172,Double(q.y)+Double(dy)*70),default:[]] where frame(id).contains(q){return id}}}
        return nil
    }
    var emptyMessage:String{L(document.nodes.isEmpty ? "graph.sourceEmpty":"graph.filteredEmpty")}
    override func draw(_ dirtyRect:NSRect){
        Palette.background.setFill();dirtyRect.intersection(bounds).fill()
        guard !displayNodes.isEmpty else {drawText(emptyMessage,in:bounds.insetBy(dx:24,dy:24),font:.systemFont(ofSize:13),color:Palette.muted);return}
        NSGraphicsContext.saveGraphicsState()
        let transform=NSAffineTransform();transform.translateX(by:offset.x,yBy:offset.y);transform.scale(by:scale);transform.concat()
        let visible=NSRect(x:-offset.x/scale,y:-offset.y/scale,width:bounds.width/scale,height:bounds.height/scale).insetBy(dx:-180,dy:-80)
        // Fixed hierarchical geometry. No timer, force simulation, shader or full-frame effect.
        for e in displayEdges {let a=frame(e.from),b=frame(e.to);guard !a.isEmpty && !b.isEmpty else{continue}
            let union=a.union(b);guard union.intersects(visible)else{continue}
            let from=NSPoint(x:a.maxX,y:a.midY),to=NSPoint(x:b.minX,y:b.midY)
            let path=NSBezierPath();path.move(to:from);path.curve(to:to,controlPoint1:NSPoint(x:(from.x+to.x)/2,y:from.y),controlPoint2:NSPoint(x:(from.x+to.x)/2,y:to.y))
            let verified=e.status == .verified || e.status == .observed
            (verified ? Palette.green:Palette.muted).withAlphaComponent(0.55).setStroke();path.lineWidth=selected==e.from||selected==e.to ? 1.8:1
            if !verified{path.setLineDash([4,4],count:2,phase:0)};path.stroke()
            let arrow=NSBezierPath();arrow.move(to:NSPoint(x:to.x-5,y:to.y-3));arrow.line(to:to);arrow.line(to:NSPoint(x:to.x-5,y:to.y+3));arrow.stroke()
            if scale>1.05 && (selected==e.from || selected==e.to) && abs(to.x-from.x)>55 {drawText(L("relation."+e.relation),in:NSRect(x:min(from.x,to.x),y:min(from.y,to.y)-15,width:abs(to.x-from.x),height:13),font:.systemFont(ofSize:9),color:Palette.muted)}
        }
        visibleCount=0
        for n in displayNodes {let r=frame(n.id);guard r.intersects(visible)else{continue};visibleCount+=1
            let status=n.kind == .agent ? chainStatus[n.id] ?? n.status:n.status
            let path=NSBezierPath(roundedRect:r,xRadius:6,yRadius:6)
            (n.id==selected ? Palette.accent.withAlphaComponent(0.14):Palette.surface).setFill();path.fill()
            (n.id==selected ? Palette.accent:Palette.border).setStroke();path.lineWidth=n.id==selected ? 1.5:1;path.stroke()
            Palette.status(status).setFill();NSBezierPath(ovalIn:NSRect(x:r.minX+9,y:r.minY+11,width:5,height:5)).fill()
            drawText(n.title,in:NSRect(x:r.minX+20,y:r.minY+7,width:card.width-27,height:17),font:.systemFont(ofSize:12,weight:.medium),color:.labelColor)
            if scale>=0.65 {drawText(L("statusShort."+status.rawValue),in:NSRect(x:r.minX+10,y:r.minY+23,width:card.width-18,height:11),font:.systemFont(ofSize:10),color:Palette.status(status))}
            let warning=warningOutcomes[n.id] ?? .notAssessable
            drawText(warning.text,in:NSRect(x:r.minX+9,y:r.minY+35,width:card.width-16,height:12),font:.systemFont(ofSize:8.5,weight:.medium),color:Palette.warningOutcome(warning))
        }
        NSGraphicsContext.restoreGraphicsState()
        drawText(L("graph.count",["visible":String(visibleCount),"total":String(document.nodes.count)]),in:NSRect(x:14,y:bounds.height-23,width:bounds.width-140,height:16),font:.systemFont(ofSize:10),color:Palette.muted)
        // Minimap keeps geometry only, with the actual viewport rectangle.
        let mini=NSRect(x:bounds.width-116,y:bounds.height-70,width:100,height:50)
        Palette.surface.setFill();NSBezierPath(roundedRect:mini,xRadius:4,yRadius:4).fill();Palette.border.setStroke();NSBezierPath(roundedRect:mini,xRadius:4,yRadius:4).stroke()
        let ratio=min((mini.width-8)/max(1,layout.width),(mini.height-8)/max(1,layout.height))
        Palette.muted.setFill();for n in displayNodes {let r=frame(n.id);NSRect(x:mini.minX+4+r.minX*ratio,y:mini.minY+4+r.minY*ratio,width:max(2,r.width*ratio),height:max(1,r.height*ratio)).fill()}
        let port=NSRect(x:mini.minX+4+(-offset.x/scale)*ratio,y:mini.minY+4+(-offset.y/scale)*ratio,width:bounds.width/scale*ratio,height:bounds.height/scale*ratio).intersection(mini)
        Palette.accent.setStroke();NSBezierPath(rect:port).stroke()
    }
    func updateWarningPulses(){
        guard Thread.isMainThread else{return}
        var visible:[String:NSRect]=[:]
        if window?.isVisible == true && window?.isMiniaturized != true && window?.occlusionState.contains(.visible) == true && !isHiddenOrHasHiddenAncestor {
            for (id,outcome) in warningOutcomes {
                let r=frame(id),actual=NSRect(x:r.minX*scale+offset.x,y:r.minY*scale+offset.y,width:r.width*scale,height:r.height*scale)
                if outcome.shouldPulse(enabled:pulseEnabled,reduceMotion:reduceMotion,visible:actual.intersects(visibleRect)) {visible[id]=actual}
            }
        }
        for id in Array(pulseViews.keys) where visible[id]==nil {pulseViews.removeValue(forKey:id)?.removeFromSuperview()}
        for (id,r) in visible {
            if let pulse=pulseViews[id]{pulse.frame=r;continue}
            let outcome=warningOutcomes[id]!,pulse=WarningPulseView(frame:r)
            pulse.configure(outcome);addSubview(pulse);pulseViews[id]=pulse
        }
    }
    private func drawText(_ value:String,in rect:NSRect,font:NSFont,color:NSColor){let p=NSMutableParagraphStyle();p.lineBreakMode = .byTruncatingTail;(value as NSString).draw(in:rect,withAttributes:[.font:font,.foregroundColor:color,.paragraphStyle:p])}
    override func mouseDown(with event:NSEvent){window?.makeFirstResponder(self);let p=convert(event.locationInWindow,from:nil)
        if NSRect(x:bounds.width-116,y:bounds.height-70,width:100,height:50).contains(p){fitGraph();return}
        pressed=hit(p);if let id=pressed{select(id);if event.clickCount==2{if nodeByID[id]?.kind == .cluster{onExpand?(id)}else{onFocus?(id)}}}else{dragPoint=p;originalOffset=offset}
    }
    override func mouseDragged(with event:NSEvent){guard let start=dragPoint else{return};let p=convert(event.locationInWindow,from:nil);offset=NSPoint(x:originalOffset.x+p.x-start.x,y:originalOffset.y+p.y-start.y);needsDisplay=true;onChange?()}
    override func mouseUp(with event:NSEvent){dragPoint=nil;pressed=nil;updateAccessibility()}
    override func scrollWheel(with event:NSEvent){if event.modifierFlags.contains(.command)||event.modifierFlags.contains(.control){zoom(event.scrollingDeltaY>0 ? 1.06:0.94)}else{offset.x-=event.scrollingDeltaX;offset.y-=event.scrollingDeltaY;needsDisplay=true};onChange?()}
    override func magnify(with event:NSEvent){zoom(max(0.5,1+event.magnification))}
    override func keyDown(with event:NSEvent){switch event.charactersIgnoringModifiers {
        case "+","=":zoom(1.15);case "-":zoom(1/1.15);case "0":fitGraph()
        case "\r"," ":if let id=selected{select(id)}
        default:let ids=displayNodes.map(\.id);guard !ids.isEmpty else{return};let index=ids.firstIndex(of:selected ?? "") ?? 0
            if [123,124,125,126].contains(event.keyCode){let next=(index+([123,126].contains(event.keyCode) ? ids.count-1:1))%ids.count;select(ids[next]);center(ids[next])}else{super.keyDown(with:event)}
        }
    }
    override func updateTrackingAreas(){super.updateTrackingAreas();if let tracking{removeTrackingArea(tracking)};tracking=NSTrackingArea(rect:bounds,options:[.mouseMoved,.activeInKeyWindow,.inVisibleRect],owner:self,userInfo:nil);addTrackingArea(tracking!)}
    override func mouseMoved(with event:NSEvent){let id=hit(convert(event.locationInWindow,from:nil));toolTip=id.flatMap{nodeByID[$0]}.map{$0.title+"\n"+$0.kind.label+" · "+$0.status.label+"\n"+L("inspector.integrity")+": "+(chainStatus[$0.id] ?? .unknown).label+"\n"+L("warning.title")+": "+(warningOutcomes[$0.id] ?? .notAssessable).text+"\n"+$0.facts.map{L($0.labelKey)+": "+$0.text}.joined(separator:"\n")}}
    override func menu(for event:NSEvent)->NSMenu? {guard let id=hit(convert(event.locationInWindow,from:nil))else{return nil};select(id);let m=NSMenu()
        for (key,sel) in [("button.focus",#selector(focusMenu)),("button.copy",#selector(copyMenu))]{let item=NSMenuItem(title:L(key),action:sel,keyEquivalent:"");item.target=self;m.addItem(item)}
        if nodeByID[id]?.kind == .cluster{let item=NSMenuItem(title:L("graph.openCluster"),action:#selector(expandMenu),keyEquivalent:"");item.target=self;m.addItem(item)};return m
    }
    @objc private func focusMenu(){if let selected{onFocus?(selected)}}
    @objc private func copyMenu(){if let selected{NSPasteboard.general.clearContents();NSPasteboard.general.setString(selected,forType:.string)}}
    @objc private func expandMenu(){if let selected{onExpand?(selected)}}
    func updateAccessibility(){
        var children:[NSAccessibilityElement]=[]
        // Virtual elements mirror visible semantic nodes, never an NSView per graph node.
        for n in displayNodes {
            let r=frame(n.id);let actual=NSRect(x:r.minX*scale+offset.x,y:r.minY*scale+offset.y,width:r.width*scale,height:r.height*scale)
            guard actual.intersects(bounds)else{continue}
            let screen=window?.convertToScreen(convert(actual,to:nil)) ?? actual
            let status=n.kind == .agent ? chainStatus[n.id] ?? n.status:n.status
            let element=GraphAccessibleNode(owner:self,id:n.id,role:.button,frame:screen,label:n.title+", "+n.kind.label+", "+status.label+", "+(warningOutcomes[n.id] ?? .notAssessable).text)
            children.append(element)
        }
        setAccessibilityChildren(children)
    }
}
private final class GraphAccessibleNode:NSAccessibilityElement {
    weak var owner:GraphCanvas?;let id:String
    init(owner:GraphCanvas,id:String,role:NSAccessibility.Role,frame:NSRect,label:String){self.owner=owner;self.id=id;super.init();setAccessibilityRole(role);setAccessibilityFrame(frame);setAccessibilityLabel(label);setAccessibilityParent(owner)}
    override func accessibilityPerformPress()->Bool{owner?.select(id);return true}
}

/// Hit testing stays with the canvas. Only this small border layer animates.
private final class WarningPulseView:NSView {
    override var isFlipped:Bool{true}
    override func hitTest(_ point:NSPoint)->NSView?{nil}
    func configure(_ outcome:WarningOutcome){
        wantsLayer=true;setAccessibilityElement(false)
        guard let layer else{return}
        layer.cornerRadius=6;layer.borderWidth=2;layer.borderColor=Palette.warningOutcome(outcome).cgColor
        let animation=CABasicAnimation(keyPath:"opacity")
        animation.fromValue=outcome == .finding(.critical) ? 0.45:0.3;animation.toValue=1
        animation.duration=outcome == .finding(.critical) ? 1.8:2.8
        animation.autoreverses=true;animation.repeatCount = .infinity;animation.timingFunction=CAMediaTimingFunction(name:.easeInEaseOut)
        layer.add(animation,forKey:"warningPulse")
    }
}
