import AppKit
import AuthorityCore

final class LayoutView:SurfaceView {
    var arrange:((NSRect)->Void)?
    override func layout(){super.layout();arrange?(bounds)}
}
final class AppState {
    var document=DemoData.make()
    var selected="agent-001"
    var chainAnchor="agent-001"
    var page="graph"
    var graphMode=2
    var filter=0
    var query=""
    var expandedGroups:Set<String>=[]
    var inputURL:URL?
    var sourceID="local-run"
    var onChange:(()->Void)?
    func select(_ id:String){selected=id;onChange?()}
}
final class SidebarController:NSViewController {
    let state:AppState;var navigate:((String)->Void)?
    private var buttons:[NSButton]=[]
    init(_ state:AppState){self.state=state;super.init(nibName:nil,bundle:nil)}
    required init?(coder:NSCoder){fatalError()}
    override func loadView(){let root=LayoutView();root.color=Palette.surface;view=root;reload()}
    func reload(){guard isViewLoaded else{return};view.subviews.forEach{$0.removeFromSuperview()};buttons=[]
        let title=label("app.name",size:18,weight:.semibold);view.addSubview(title)
        let subtitle=label("app.tagline",size:10,color:Palette.muted);view.addSubview(subtitle)
        let keys=["overview","graph","agents","delegations","actions","evidence","findings"]
        let symbols=["square.grid.2x2","point.3.connected.trianglepath.dotted","person.crop.circle","link","cpu","doc.text.magnifyingglass","exclamationmark.triangle"]
        for (i,key) in keys.enumerated(){let b=button("nav."+key,target:self,action:#selector(press(_:)),symbol:symbols[i]);b.identifier=NSUserInterfaceItemIdentifier(key);b.bezelStyle = .recessed;b.isBordered=false;b.alignment = .left;b.font = .systemFont(ofSize:12);b.wantsLayer=true;b.layer?.cornerRadius=5;buttons.append(b);view.addSubview(b)}
        let scope=label("nav.scope",size:10,color:Palette.muted);view.addSubview(scope)
        let source=wrapping(state.document.isDemo ? L("mode.demo"):state.document.source,size:11);view.addSubview(source)
        let host=button("nav.host",target:self,action:#selector(hostPressed),symbol:"desktopcomputer");host.isBordered=false;host.alignment = .left;view.addSubview(host)
        let settings=button("nav.settings",target:self,action:#selector(settingsPressed),symbol:"gearshape");settings.isBordered=false;settings.alignment = .left;view.addSubview(settings)
        (view as? LayoutView)?.arrange={ [weak self] r in
            title.frame=NSRect(x:16,y:21,width:r.width-28,height:25);subtitle.frame=NSRect(x:16,y:49,width:r.width-28,height:18)
            for (i,b) in self?.buttons.enumerated() ?? [].enumerated(){b.frame=NSRect(x:10,y:88+CGFloat(i)*34,width:r.width-20,height:29)}
            scope.frame=NSRect(x:16,y:349,width:r.width-26,height:16);source.frame=NSRect(x:16,y:371,width:r.width-30,height:55)
            host.frame=NSRect(x:10,y:max(446,r.height-84),width:r.width-20,height:30);settings.frame=NSRect(x:10,y:max(480,r.height-46),width:r.width-20,height:30)
        };updateSelection();view.needsLayout=true
    }
    func updateSelection(){for b in buttons{let selected=b.identifier?.rawValue==state.page;b.contentTintColor=selected ? Palette.accent:Palette.muted;b.layer?.backgroundColor=(selected ? Palette.accent.withAlphaComponent(0.12):.clear).cgColor}}
    @objc private func press(_ sender:NSButton){navigate?(sender.identifier?.rawValue ?? "graph")}
    @objc private func hostPressed(){navigate?("host")}
    @objc private func settingsPressed(){navigate?("settings")}
}

final class MetricView:SurfaceView {
    let title=label("metric.agents",size:11,color:Palette.muted),value=NSTextField(labelWithString:"—"),detail=NSTextField(labelWithString:"")
    override init(frame:NSRect){super.init(frame:frame);rounded=7;value.font = .systemFont(ofSize:25,weight:.medium);detail.font = .systemFont(ofSize:10);detail.textColor=Palette.muted;detail.lineBreakMode = .byTruncatingTail;[title,value,detail].forEach{addSubview($0)}}
    required init?(coder:NSCoder){fatalError()}
    override func layout(){super.layout();title.frame=NSRect(x:12,y:9,width:bounds.width-24,height:16);value.frame=NSRect(x:12,y:28,width:bounds.width-24,height:29);detail.frame=NSRect(x:12,y:61,width:bounds.width-24,height:16)}
    func set(_ key:String,_ number:String,_ caption:String){title.stringValue=L(key);value.stringValue=number;detail.stringValue=caption;toolTip=caption}
}

final class MainPanelController:NSViewController,NSTableViewDataSource,NSTableViewDelegate,NSSearchFieldDelegate {
    let state:AppState;let canvas=GraphCanvas(frame:.zero)
    var select:((String)->Void)?;var openSource:(()->Void)?;var openReport:(()->Void)?;var export:(()->Void)?
    var refresh:(()->Void)?;var cancel:(()->Void)?
    private var metrics:[MetricView]=[]
    private var rows:[GraphNode]=[]
    private var tableChainStatus:[String:ProofStatus]=[:]
    private var table=NSTableView(),scroll=NSScrollView(),search=NSSearchField(),mode=NSSegmentedControl(),filter=NSPopUpButton(),zoomLabel=NSTextField(labelWithString:"")
    private var heading: NSTextField!,scope: NSTextField!,coverage:NSTextField!,activity:NSTextField!
    private var fitAfterLayout=true
    private var selectedChange=false
    var busy=false{didSet{updateContent()}}
    init(_ state:AppState){self.state=state;super.init(nibName:nil,bundle:nil)}
    required init?(coder:NSCoder){fatalError()}
    override func loadView(){let root=LayoutView();root.color=Palette.background;view=root;build()}
    func build(){guard isViewLoaded else{return};let oldScale=canvas.scale,oldOffset=canvas.offset
        view.subviews.forEach{$0.removeFromSuperview()};metrics=[]
        heading=label("graph.title",size:23,weight:.semibold);scope=label("mode.sample",size:9,color:Palette.muted)
        coverage=label("app.observer",size:10,color:Palette.muted);activity=label("activity.title",size:12,weight:.medium)
        [heading,scope,coverage,activity].forEach{view.addSubview($0!)}
        for _ in 0..<4{let metric=MetricView();metrics.append(metric);view.addSubview(metric)}
        let open=button("button.open",target:self,action:#selector(openPressed),symbol:"folder"),reload=button("button.refresh",target:self,action:#selector(refreshPressed),symbol:"arrow.clockwise"),save=button("button.export",target:self,action:#selector(exportPressed),symbol:"square.and.arrow.up")
        mode=NSSegmentedControl(labels:[L("graph.chain"),L("graph.agents"),L("graph.clusters")],trackingMode:.selectOne,target:self,action:#selector(modeChanged));mode.controlSize = .small;mode.selectedSegment=state.graphMode
        filter=NSPopUpButton();filter.addItems(withTitles:[L("graph.all"),L("graph.missing"),L("graph.observed")]);filter.controlSize = .small;filter.selectItem(at:state.filter);filter.target=self;filter.action=#selector(filterChanged)
        search=NSSearchField();search.placeholderString=L("graph.search");search.stringValue=state.query;search.delegate=self;search.controlSize = .small
        let minus=button("button.zoomOut",target:self,action:#selector(zoomOut),symbol:"minus"),plus=button("button.zoomIn",target:self,action:#selector(zoomIn),symbol:"plus"),fit=button("button.fit",target:self,action:#selector(fitPressed))
        minus.title="";plus.title="";zoomLabel.font = .systemFont(ofSize:10);zoomLabel.textColor=Palette.muted
        let stop=button("button.cancel",target:self,action:#selector(cancelPressed));stop.isHidden = !busy
        for v in [open,reload,save,mode,filter,search,canvas,minus,plus,fit,zoomLabel,stop] as [NSView]{view.addSubview(v)}
        table=NSTableView();table.headerView=NSTableHeaderView();table.rowHeight=24;table.style = .inset;table.usesAlternatingRowBackgroundColors=false;table.backgroundColor=Palette.surface
        for (id,key,width) in [("kind","activity.kind",95.0),("name","activity.name",220.0),("status","activity.status",165.0),("id","field.instance",135.0),("evidence","activity.evidence",135.0)] {
            let c=NSTableColumn(identifier:NSUserInterfaceItemIdentifier(id));c.title=L(key);c.width=width;c.minWidth=65;c.resizingMask = .autoresizingMask;table.addTableColumn(c)
        }
        table.dataSource=self;table.delegate=self;table.columnAutoresizingStyle = .uniformColumnAutoresizingStyle;table.setAccessibilityLabel(L("activity.title"))
        scroll=NSScrollView();scroll.documentView=table;scroll.hasVerticalScroller=true;scroll.autohidesScrollers=true;scroll.scrollerStyle = .overlay;scroll.borderType = .noBorder;view.addSubview(scroll)
        canvas.onSelect={ [weak self] id in self?.select?(id) }
        canvas.onFocus={ [weak self] id in self?.state.selected=id;self?.state.chainAnchor=id;self?.state.graphMode=0;self?.mode.selectedSegment=0;self?.updateGraph(fit:true) }
        canvas.onExpand={ [weak self] id in self?.state.expandedGroups.insert(id.replacingOccurrences(of:"cluster:",with:""));self?.updateGraph(fit:true) }
        canvas.onChange={ [weak self] in self?.zoomLabel.stringValue="\(Int((self?.canvas.scale ?? 1)*100)) %" }
        (view as? LayoutView)?.arrange={ [weak self] r in guard let self else{return};let w=r.width-32
            self.heading.frame=NSRect(x:16,y:16,width:w-298,height:29);self.scope.frame=NSRect(x:16,y:48,width:w-298,height:16)
            open.frame=NSRect(x:r.width-282,y:20,width:142,height:25);reload.frame=NSRect(x:r.width-133,y:20,width:117,height:25)
            for (i,m) in self.metrics.enumerated(){m.frame=NSRect(x:16+CGFloat(i)*(w+10)/4,y:77,width:(w-30)/4,height:86)}
            self.coverage.frame=NSRect(x:16,y:171,width:w-180,height:17);save.frame=NSRect(x:r.width-188,y:168,width:172,height:24)
            self.mode.frame=NSRect(x:16,y:199,width:228,height:25);self.filter.frame=NSRect(x:252,y:199,width:155,height:25);self.search.frame=NSRect(x:max(414,r.width-287),y:199,width:min(271,max(140,r.width-430)),height:25)
            let available=max(180,r.height-408)
            if self.canvas.agentOverview{self.canvas.useColumns(max(4,min(10,Int(w/164))))}
            let fitScale=min(1.15,max(0.15,(w-40)/self.canvas.layout.width))
            let preferred=max(225,self.canvas.layout.height*fitScale+50)
            let graphHeight=min(available,preferred)
            self.canvas.frame=NSRect(x:16,y:232,width:w,height:graphHeight)
            let footer=232+graphHeight+5
            self.zoomLabel.frame=NSRect(x:r.width-174,y:footer+4,width:46,height:18);minus.frame=NSRect(x:r.width-206,y:footer,width:27,height:24);plus.frame=NSRect(x:r.width-126,y:footer,width:27,height:24);fit.frame=NSRect(x:r.width-93,y:footer,width:77,height:24)
            stop.frame=NSRect(x:16,y:footer,width:120,height:24)
            self.activity.frame=NSRect(x:16,y:footer+35,width:w,height:20)
            self.scroll.frame=NSRect(x:16,y:footer+60,width:w,height:max(62,r.height-footer-72))
            if self.fitAfterLayout{self.canvas.fitGraph();self.fitAfterLayout=false};self.canvas.updateAccessibility()
        }
        updateContent();canvas.scale=oldScale;canvas.offset=oldOffset;view.needsLayout=true
    }
    func updateContent(){guard isViewLoaded else{return};let d=state.document
        tableChainStatus=d.chainStatuses()
        heading.stringValue=L("nav."+state.page)
        scope.stringValue=d.isDemo ? L("mode.sample"):(d.reportJSON != nil ? L("mode.product"):L("mode.live"))
        let agents=d.nodes.filter{$0.kind == .agent},delegations=d.edges.filter{$0.relation=="delegates"},actions=d.nodes.filter{$0.kind == .action}
        if d.isDemo {
            let statuses=d.chainStatuses(),good=actions.filter{statuses[$0.id] == .verified}.count
            metrics[0].set("metric.agents",String(agents.count),L("metric.sampleAgents"))
            metrics[1].set("metric.delegations",String(delegations.count),L("metric.demo"))
            metrics[2].set("metric.chains",String(good),L("metric.sampleChains",["good":String(good),"missing":String(actions.count-good)]))
            metrics[3].set("metric.actions",String(actions.count),L("metric.demo"))
        }else if d.reportJSON != nil {
            metrics[0].set("metric.reported",String(d.totalEntries ?? d.nodes.filter{$0.kind == .entry}.count),L("status.reported"))
            metrics[1].set("metric.tasks",String(d.reportedTaskCount ?? d.nodes.filter{$0.kind == .task}.count),L("basis.task"))
            metrics[2].set("metric.warnings",String(d.reportedWarningCount ?? d.warnings.count),L("metric.warnings"))
            metrics[3].set("metric.coverage",d.completeRead == true ? "✓":"△",L(d.completeRead == true ? "metric.complete":"metric.incomplete"))
        }else{
            metrics[0].set("metric.agents","—",L("metric.unavailable"));metrics[1].set("metric.delegations","—",L("metric.unavailable"));metrics[2].set("metric.chains","—",L("metric.unavailable"));metrics[3].set("metric.actions",String(actions.count),L("metric.kernelOnly"))
        }
        coverage.stringValue=busy ? L("source.loading"):(d.omitted>0 ? L("graph.hidden",["count":String(d.omitted)]):L("app.observer"))
        rows=d.nodes.filter{n in switch state.page{case "agents":return n.kind == .agent || n.kind == .identity;case "delegations":return d.edges.contains{$0.to==n.id&&$0.relation=="delegates"};case "evidence":return !n.evidence.isEmpty;case "findings":return [.incomplete,.unknown,.contradictory].contains(n.status);default:return [.action,.entry,.process].contains(n.kind)}}
        table.reloadData();updateGraph(fit:false)
    }
    func updateGraph(fit:Bool){let d=state.document;var nodes=d.nodes,edges=d.edges
        if state.graphMode==0 {let anchor=d.nodes.contains{$0.id==state.chainAnchor} ? state.chainAnchor:state.selected;let ids=d.trace(anchor);nodes=nodes.filter{ids.contains($0.id)};edges=edges.filter{ids.contains($0.from)&&ids.contains($0.to)}}
        else if d.isDemo && state.graphMode==1 {if d.nodes.filter({$0.kind == .agent}).count>80{let result=clustered(d);nodes=result.0;edges=result.1}else{nodes=nodes.filter{[.agent,.identity,.authority].contains($0.kind)};let ids=Set(nodes.map(\.id));edges=edges.filter{ids.contains($0.from)&&ids.contains($0.to)}}}
        else if d.isDemo && state.graphMode==2 {
            let result=clustered(d);nodes=result.0;edges=result.1
        }
        if state.filter != 0 {nodes=nodes.filter{state.filter==1 ? [.unknown,.incomplete,.contradictory,.reported].contains($0.status):[.observed,.verified].contains($0.status)}}
        if !state.query.isEmpty {let q=state.query.lowercased();nodes=nodes.filter{($0.title+" "+$0.id+" "+$0.facts.map(\.value).joined(separator:" ")+" "+$0.evidence.joined(separator:" ")).lowercased().contains(q)}}
        let ids=Set(nodes.map(\.id));edges=edges.filter{ids.contains($0.from)&&ids.contains($0.to)}
        canvas.document=d;canvas.selected=state.selected;canvas.setGraph(nodes:nodes,edges:edges,fit:fit,agentOverview:d.isDemo && state.graphMode==1 && !nodes.contains{$0.kind == .cluster});if fit{fitAfterLayout=true};view.needsLayout=true
    }
    private func clustered(_ d:GraphDocument)->([GraphNode],[GraphEdge]) {
        var nodes=d.nodes.filter{($0.group=="root")||state.expandedGroups.contains($0.group) && $0.kind == .agent}
        let agents=d.nodes.filter{$0.kind == .agent&&$0.group != "root"};let groups=Dictionary(grouping:agents,by:\.group),statuses=d.chainStatuses()
        var map:[String:String]=[:]
        for (group,members) in groups {if state.expandedGroups.contains(group){for n in members{map[n.id]=n.id};continue}
            let id="cluster:"+group;for n in members{map[n.id]=id}
            let missing=members.filter{statuses[$0.id] != .verified}.count
            nodes.append(GraphNode(id:id,kind:.cluster,name:L("graph.clusterCount",["count":String(members.count)]),status:missing>0 ? .incomplete:.verified,group:group,facts:[Fact("metric.agents",String(members.count)),Fact("metric.chains",String(missing))]))
        }
        let ids=Set(nodes.map(\.id));var edges:[GraphEdge]=[],seen:Set<String>=[]
        for e in d.edges {let from=map[e.from] ?? e.from,to=map[e.to] ?? e.to;guard from != to,ids.contains(from),ids.contains(to)else{continue}
            let pair=from+":"+to;if seen.insert(pair).inserted{edges.append(GraphEdge(from,to,e.relation,e.status,evidence:e.evidence))}
            else if let i=edges.firstIndex(where:{$0.from==from&&$0.to==to}){edges[i].evidence+=e.evidence;if e.status != .verified{edges[i].status=e.status}}
        }
        return(nodes.sorted{$0.id<$1.id},edges)
    }
    func focusSearch(){view.window?.makeFirstResponder(search)}
    func selectedUpdated(){canvas.selected=state.selected;canvas.needsDisplay=true;canvas.updateAccessibility()}
    func numberOfRows(in tableView:NSTableView)->Int{rows.count}
    func tableView(_ tableView:NSTableView,viewFor column:NSTableColumn?,row:Int)->NSView?{guard rows.indices.contains(row)else{return nil};let n=rows[row],cell=NSTextField(labelWithString:"");cell.font = .systemFont(ofSize:11);cell.lineBreakMode = .byTruncatingTail
        switch column?.identifier.rawValue{case "kind":cell.stringValue=n.kind.label;case "name":cell.stringValue=n.title;case "status":let status=n.kind == .agent ? tableChainStatus[n.id] ?? n.status:n.status;cell.stringValue=status.label;cell.textColor=Palette.status(status);case "id":cell.stringValue=n.id;case "evidence":cell.stringValue=n.evidence.joined(separator:", ");default:break};cell.toolTip=cell.stringValue;return cell}
    func tableViewSelectionDidChange(_ notification:Notification){let row=table.selectedRow;if rows.indices.contains(row){select?(rows[row].id)}}
    func controlTextDidChange(_ obj:Notification){state.query=search.stringValue;updateGraph(fit:true)}
    @objc func fitPressed(){canvas.fitGraph()}
    @objc private func zoomIn(){canvas.zoom(1.15)}
    @objc private func zoomOut(){canvas.zoom(1/1.15)}
    @objc private func modeChanged(){state.graphMode=mode.selectedSegment;updateGraph(fit:true)}
    @objc private func filterChanged(){state.filter=filter.indexOfSelectedItem;updateGraph(fit:true)}
    @objc private func openPressed(){openSource?()}
    @objc private func refreshPressed(){refresh?()}
    @objc private func exportPressed(){export?()}
    @objc private func cancelPressed(){cancel?()}
}

final class InspectorController:NSViewController {
    let state:AppState;var select:((String)->Void)?
    private let scroll=NSScrollView();private var raw=false
    init(_ state:AppState){self.state=state;super.init(nibName:nil,bundle:nil)}
    required init?(coder:NSCoder){fatalError()}
    override func loadView(){let root=LayoutView();root.color=Palette.surface;view=root;scroll.hasVerticalScroller=true;scroll.autohidesScrollers=true;scroll.scrollerStyle = .overlay;scroll.drawsBackground=false;view.addSubview(scroll);root.arrange={[weak self] r in self?.scroll.frame=r;self?.layoutDocument(width:r.width)};reload()}
    private var doc=LayoutView()
    private var layoutItems:[(NSView,CGFloat)]=[]
    private func add(_ v:NSView,_ h:CGFloat){doc.addSubview(v);layoutItems.append((v,h))}
    func reload(){guard isViewLoaded else{return};doc=LayoutView();layoutItems=[];doc.color=Palette.surface
        guard let node=state.document.nodes.first(where:{$0.id==state.selected}) else{
            if state.selected.hasPrefix("cluster:"){add(label("kind.cluster",size:18,weight:.semibold),32);let group=state.selected.replacingOccurrences(of:"cluster:",with:"");let members=state.document.nodes.filter{$0.kind == .agent&&$0.group==group};let ids=Set(members.map(\.id));let internalCount=state.document.edges.filter{$0.relation=="delegates"&&ids.contains($0.from)&&ids.contains($0.to)}.count;let externalCount=state.document.edges.filter{$0.relation=="delegates"&&(ids.contains($0.from) != ids.contains($0.to))}.count
                add(wrapping(L("graph.clusterCount",["count":String(members.count)])),32);add(wrapping(L("field.internalDelegations")+": \(internalCount)"),32);add(wrapping(L("field.externalRelationships")+": \(externalCount)"),32);add(wrapping(L("graph.openCluster")),30);add(wrapping(members.map(\.title).joined(separator:", ")),100);add(wrapping(L("boundary.sample")),65)
            }else{add(wrapping(L("inspector.empty")),60)}
            scroll.documentView=doc;layoutDocument(width:view.bounds.width);return
        }
        add(label("inspector.title",size:10,color:Palette.muted),22)
        let kind=NSTextField(labelWithString:node.kind.label.uppercased());kind.font = .systemFont(ofSize:10);kind.textColor=Palette.muted;add(kind,20)
        let name=NSTextField(labelWithString:node.title);name.font = .systemFont(ofSize:21,weight:.medium);name.lineBreakMode = .byTruncatingTail;name.toolTip=node.title;add(name,30)
        let verdict=node.kind == .agent ? state.document.chainStatuses()[node.id] ?? node.status:node.status
        let status=NSTextField(labelWithString:verdict.label);status.font = .systemFont(ofSize:11);status.textColor=Palette.status(verdict);add(status,23)
        let tabs=NSSegmentedControl(labels:[L("inspector.chain"),L("inspector.raw")],trackingMode:.selectOne,target:self,action:#selector(tabChanged));tabs.selectedSegment=raw ? 1:0;tabs.controlSize = .small;add(tabs,32)
        if raw {
            let text=NSTextView();text.isEditable=false;text.isSelectable=true;text.font = .monospacedSystemFont(ofSize:11,weight:.regular);text.backgroundColor=Palette.background
            let encoder=JSONEncoder();encoder.outputFormatting=[.prettyPrinted,.sortedKeys,.withoutEscapingSlashes]
            text.string=(try? encoder.encode(node)).flatMap{String(data:$0,encoding:.utf8)} ?? "{}"
            text.textContainer?.widthTracksTextView=true;add(text,CGFloat(max(350,text.string.split(separator:"\n").count*16)));add(wrapping(L("boundary.sample")),50)
        }else{
            let d=state.document;add(wrapping(L(d.isDemo ? "inspector.sampleExplanation":d.reportJSON != nil ? "inspector.productExplanation":"inspector.liveExplanation"),size:11),62)
            add(label("inspector.selected",size:10,color:Palette.muted),22)
            for fact in node.facts {let v=wrapping(L(fact.labelKey)+": "+fact.text,size:11);v.toolTip=fact.text;add(v,fact.labelKey=="field.sha256" ? 50:32)}
            if !node.evidence.isEmpty{let v=wrapping(L("field.evidence")+": "+node.evidence.joined(separator:", "),size:11);add(v,32)}
            add(label("inspector.origin",size:10,color:Palette.muted),26)
            let trace=d.trace(state.chainAnchor).contains(node.id) ? d.trace(state.chainAnchor):d.trace(node.id),ordered=GraphLayout.make(nodes:d.nodes.filter{trace.contains($0.id)},edges:d.edges.filter{trace.contains($0.from)&&trace.contains($0.to)})
            let chain=d.nodes.filter{trace.contains($0.id)}.sorted{let a=ordered.positions[$0.id]!,b=ordered.positions[$1.id]!;return a.x==b.x ? a.y<b.y:a.x<b.x}
            for item in chain {let b=NSButton(title:item.title+"  ·  "+item.kind.label,target:self,action:#selector(chainPressed(_:)));b.identifier=NSUserInterfaceItemIdentifier(item.id);b.isBordered=false;b.alignment = .left;b.font = .systemFont(ofSize:11);b.contentTintColor=Palette.status(item.status);b.lineBreakMode = .byTruncatingTail;b.toolTip=item.status.label+"\n"+item.id;add(b,25)}
            add(label("inspector.integrity",size:12,weight:.medium),28)
            let qualified=d.isDemo && d.chainStatuses()[state.chainAnchor] == .verified
            for key in ["inspector.signatures","inspector.binding","inspector.loss"]{add(wrapping(L(key)+": "+L(qualified ? "demo.synthetic":"status.unknown"),size:11),38)}
            add(label("inspector.boundary",size:11,weight:.medium),25)
            add(wrapping(L(d.isDemo ? "boundary.sample":d.reportJSON != nil ? "boundary.product":"boundary.live"),size:11),65)
            if node.kind == .action{add(wrapping(L("boundary.durable"),size:11),35)}
        }
        scroll.documentView=doc;layoutDocument(width:view.bounds.width)
    }
    private func layoutDocument(width:CGFloat){guard width>0 else{return};var y:CGFloat=16;for (v,h) in layoutItems{v.frame=NSRect(x:16,y:y,width:max(10,width-32),height:h);y+=h+3};doc.frame=NSRect(x:0,y:0,width:width,height:max(y,view.bounds.height))}
    @objc private func tabChanged(_ sender:NSSegmentedControl){raw=sender.selectedSegment==1;reload()}
    @objc private func chainPressed(_ sender:NSButton){if let id=sender.identifier?.rawValue{select?(id)}}
}

final class MainSplitController:NSSplitViewController {
    let state:AppState;let sidebar:SidebarController;let main:MainPanelController;let inspector:InspectorController
    var navigate:((String)->Void)?
    init(_ state:AppState){self.state=state;sidebar=SidebarController(state);main=MainPanelController(state);inspector=InspectorController(state);super.init(nibName:nil,bundle:nil)}
    required init?(coder:NSCoder){fatalError()}
    override func viewDidLoad(){super.viewDidLoad();let s=NSSplitViewItem(sidebarWithViewController:sidebar);s.minimumThickness=176;s.maximumThickness=220;s.preferredThicknessFraction=0.11;s.canCollapse=true
        let m=NSSplitViewItem(viewController:main);m.minimumThickness=670
        let i=NSSplitViewItem(viewController:inspector);i.minimumThickness=292;i.maximumThickness=370;i.canCollapse=true;i.preferredThicknessFraction=0.18
        addSplitViewItem(s);addSplitViewItem(m);addSplitViewItem(i);sidebar.navigate={ [weak self] key in self?.navigate?(key) }
        main.select={ [weak self] id in self?.select(id) };inspector.select={ [weak self] id in self?.select(id) }
    }
    func select(_ id:String){if !state.document.trace(state.chainAnchor).contains(id){state.chainAnchor=id};state.selected=id;main.selectedUpdated();if state.graphMode==0{main.updateGraph(fit:false)};inspector.reload()}
    func refresh(){sidebar.reload();main.updateContent();inspector.reload()}
    func localize(){sidebar.reload();main.build();inspector.reload()}
    func toggleInspector(){splitViewItems[2].isCollapsed.toggle()}
}
