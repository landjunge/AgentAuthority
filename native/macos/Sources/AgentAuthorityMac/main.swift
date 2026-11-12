import AppKit
import AuthorityCore

private final class AppWindow:NSWindow {
    override func constrainFrameRect(_ frameRect:NSRect,to screen:NSScreen?)->NSRect {
        CommandLine.arguments.contains("--snapshot") && CommandLine.arguments.contains("--size") ? frameRect:super.constrainFrameRect(frameRect,to:screen)
    }
}
final class AppDelegate:NSObject,NSApplicationDelegate,NSToolbarDelegate {
    let state=AppState(),bridge=EngineBridge(),host=PermissionHost()
    var window:NSWindow!,split:MainSplitController!,hostWindow:NSWindow?,settingsWindow:NSWindow?
    let familySwitch = FamilySwitchClient()
    var familyContent:FamilyContentController?
    var observer:NSObjectProtocol?
    func applicationDidFinishLaunching(_ notification:Notification){
        // Only an identical installed executable is a duplicate; historical review bundles stay independent.
        if Bundle.main.bundleURL.pathExtension == "app", Bundle.main.bundleIdentifier == "de.agentauthority.observer",
           let existing = NSRunningApplication.runningApplications(withBundleIdentifier:"de.agentauthority.observer").first(where: {
               $0.processIdentifier != ProcessInfo.processInfo.processIdentifier &&
               $0.executableURL?.resolvingSymlinksInPath() == Bundle.main.executableURL?.resolvingSymlinksInPath()
           }) {
            existing.unhide(); existing.activate(options:[.activateAllWindows,.activateIgnoringOtherApps])
            NSApp.terminate(nil); return
        }
        if let lang=argument("--lang"){Localization.shared.choose(lang,persist:false)}
        if let count=argument("--demo-agents").flatMap(Int.init){state.document=DemoData.make(agents:count)}
        if let path=argument("--report"),let data=try? readBoundedReport(URL(fileURLWithPath:path)),let doc=try? ReportProjection.decode(data){state.document=doc;state.selected=doc.nodes.first?.id ?? "";state.graphMode=0}
        split=MainSplitController(state);window=AppWindow(contentRect:NSRect(x:0,y:0,width:1680,height:960),styleMask:[.titled,.closable,.miniaturizable,.resizable],backing:.buffered,defer:false)
        window.title=windowTitle();window.subtitle=L("app.tagline");window.identifier=NSUserInterfaceItemIdentifier("family.agent-authority.main");familyContent=FamilyContentController(split:split);window.contentViewController=familyContent;window.minSize=NSSize(width:1150,height:730);window.isReleasedWhenClosed=false
        let visible=NSScreen.main?.visibleFrame ?? NSRect(x:0,y:0,width:1800,height:1100)
        let preferred=NSSize(width:min(2300,max(1140,visible.width-70)),height:min(1260,max(700,visible.height-90)))
        window.setContentSize(preferred);window.center();window.tabbingMode = .disallowed
        if let size=argument("--size"){let parts=size.split(separator:"x").compactMap{Double($0)};if parts.count==2,parts[0]>=1140,parts[0]<=2560,parts[1]>=700,parts[1]<=1440{window.setContentSize(NSSize(width:parts[0],height:parts[1]))}}
        let toolbar=NSToolbar(identifier:"AgentAuthorityToolbar");toolbar.delegate=self;toolbar.displayMode = .iconOnly;window.toolbar=toolbar;window.toolbarStyle = .unifiedCompact
        if let size=argument("--size"){let parts=size.split(separator:"x").compactMap{Double($0)};if parts.count==2,parts[0]>=1140,parts[0]<=2560,parts[1]>=700,parts[1]<=1440{window.setContentSize(NSSize(width:parts[0],height:parts[1]))}}
        familyContent?.header.products.onOpen = { [weak self] target in self?.switchFamilyProduct(target) }
        let theme=argument("--theme") ?? UserDefaults.standard.string(forKey:"appearance") ?? "system";setAppearance(theme)
        split.navigate={ [weak self] key in self?.navigate(key) };split.main.openSource={ [weak self] in self?.openSource() };split.main.export={ [weak self] in self?.exportReport() };split.main.refresh={ [weak self] in self?.refreshSource() };split.main.cancel={ [weak self] in self?.bridge.cancel() }
        host.onUpdate={ [weak self] in guard let self else{return};(self.hostWindow?.contentViewController as? HostController)?.reload()
            if let path=self.argument("--probe-json"),let probe=self.host.evidence["process_probe"]{let record:[String:Any]=["app_bundle_id":Bundle.main.bundleIdentifier ?? "","app_pid":ProcessInfo.processInfo.processIdentifier,"probe":probe];if let data=try? JSONSerialization.data(withJSONObject:record,options:[.prettyPrinted,.sortedKeys]){try? data.write(to:URL(fileURLWithPath:path))};NSApp.terminate(nil)}
        }
        host.onEvents={ [weak self] doc in guard let self else{return};self.state.document=doc;self.state.selected=doc.nodes.first?.id ?? "";self.state.graphMode=0;self.state.inputURL=nil;self.split.main.build();self.split.refresh();self.split.main.updateGraph(fit:true) }
        if let path=argument("--normal-state-json"){observeNormalStartup(URL(fileURLWithPath:path))}
        buildMenu();observer=NotificationCenter.default.addObserver(forName:Localization.changed,object:nil,queue:.main){[weak self]_ in self?.localize()}
        window.makeKeyAndOrderFront(nil);NSApp.activate(ignoringOtherApps:true)
        DispatchQueue.main.async{self.window.contentView?.layoutSubtreeIfNeeded();self.split.main.view.needsLayout=true;self.split.main.view.layoutSubtreeIfNeeded();self.split.main.fitPressed()}
        if argument("--probe-json") != nil{host.runProbe()}
        if let directory=argument("--source"){state.inputURL=URL(fileURLWithPath:directory);state.sourceID=argument("--source-id") ?? "local-run";refreshSource()}
        if argument("--snapshot") != nil || argument("--smoke-json") != nil || argument("--bench-json") != nil || argument("--ui-regression-json") != nil {DispatchQueue.main.asyncAfter(deadline:.now()+1.2){self.diagnostics()}}
    }
    func showMainWindow() {
        guard let window else { return }
        NSApp.unhide(nil)
        if window.isMiniaturized { window.deminiaturize(nil) }
        window.makeKeyAndOrderFront(nil); NSApp.activate(ignoringOtherApps:true)
    }
    // Hide preserves AppState, views and collector. Normal Close/Quit behavior is unchanged.
    func hideForFamilySwitch() { NSApp.hide(nil) }
    func applicationShouldHandleReopen(_ sender:NSApplication,hasVisibleWindows flag:Bool)->Bool {
        showMainWindow(); return false
    }
    func switchFamilyProduct(_ target:String) {
        guard window.attachedSheet == nil, NSApp.modalWindow == nil else {
            familyContent?.header.showDetail(L("family.switchUnknown")); return
        }
        familyContent?.header.showDetail(L("family.switching"))
        familySwitch.switchProduct(target) { [weak self] result in
            switch result {
            case .success: self?.familyContent?.header.showDetail(L("family.switched"))
            case .failure(let error):
                let key: String
                switch error {
                case FamilySwitchError.busy: key = "family.switchBusy"
                case FamilySwitchError.unavailable: key = "family.switchUnavailable"
                default: key = "family.switchUnknown"
                }
                self?.familyContent?.header.showDetail(L(key))
            }
        }
    }
    func windowTitle()->String {
        guard let tag=Bundle.main.object(forInfoDictionaryKey:"AAReviewBuildLabel") as? String else{return L("app.name")}
        return L("app.name")+" · "+L("build.review",["label":tag])
    }
    func applicationShouldTerminateAfterLastWindowClosed(_ sender:NSApplication)->Bool{true}
    func applicationWillTerminate(_ notification:Notification){bridge.cancel();host.collector?.close()}
    func argument(_ name:String)->String?{let args=CommandLine.arguments;guard let i=args.firstIndex(of:name),args.indices.contains(i+1)else{return nil};return args[i+1]}
    func localize(){familyContent?.header.localize();window.title=windowTitle();window.subtitle=L("app.tagline");buildMenu();split.localize();(hostWindow?.contentViewController as? HostController)?.reload();if let settingsWindow{settingsWindow.contentViewController=makeSettings()};for item in window.toolbar?.items ?? []{item.label=L(item.itemIdentifier.rawValue)}}
    func buildMenu(){let root=NSMenu();let appMenu=NSMenu(),file=NSMenu(title:L("menu.file")),view=NSMenu(title:L("menu.view")),windows=NSMenu(title:L("menu.window")),help=NSMenu(title:L("menu.help"))
        func add(_ key:String,_ action:Selector,_ shortcut:String,_ menu:NSMenu){let i=NSMenuItem(title:L(key),action:action,keyEquivalent:shortcut);i.target=self;menu.addItem(i)}
        add("menu.about",#selector(about),"",appMenu);add("nav.settings",#selector(settings),",",appMenu);appMenu.addItem(.separator());add("menu.quit",#selector(quit),"q",appMenu)
        add("button.open",#selector(openSource),"o",file);add("button.report",#selector(openReport),"",file);add("button.export",#selector(exportReport),"s",file);add("button.refresh",#selector(refreshSource),"r",file);add("button.cancel",#selector(cancelRead),".",file)
        add("toolbar.sidebar",#selector(toggleSidebar),"",view);add("toolbar.inspector",#selector(toggleInspector),"i",view);add("graph.search",#selector(search),"f",view);add("button.fit",#selector(fit),"0",view);add("mode.demo",#selector(loadDemo),"",view);add("nav.host",#selector(showHost),"",view)
        add("menu.minimize",#selector(minimize),"m",windows);add("menu.shortcuts",#selector(shortcuts),"?",help)
        for (title,submenu) in [(L("app.name"),appMenu),(L("menu.file"),file),(L("menu.view"),view),(L("menu.window"),windows),(L("menu.help"),help)]{let item=NSMenuItem(title:title,action:nil,keyEquivalent:"");item.submenu=submenu;root.addItem(item)}
        NSApp.mainMenu=root;NSApp.windowsMenu=windows;NSApp.helpMenu=help
    }
    func toolbarAllowedItemIdentifiers(_ toolbar:NSToolbar)->[NSToolbarItem.Identifier]{toolbarDefaultItemIdentifiers(toolbar)}
    func toolbarDefaultItemIdentifiers(_ toolbar:NSToolbar)->[NSToolbarItem.Identifier]{[.init("toolbar.sidebar"),.flexibleSpace,.init("nav.host"),.init("nav.settings"),.init("toolbar.inspector")]}
    func toolbar(_ toolbar:NSToolbar,itemForItemIdentifier id:NSToolbarItem.Identifier,willBeInsertedIntoToolbar flag:Bool)->NSToolbarItem?{let item=NSToolbarItem(itemIdentifier:id);item.label=L(id.rawValue);item.toolTip=L(id.rawValue);item.target=self
        switch id.rawValue{case "toolbar.sidebar":item.image=NSImage(systemSymbolName:"sidebar.left",accessibilityDescription:item.label);item.action=#selector(toggleSidebar)
        case "toolbar.inspector":item.image=NSImage(systemSymbolName:"sidebar.right",accessibilityDescription:item.label);item.action=#selector(toggleInspector)
        case "nav.host":item.image=NSImage(systemSymbolName:"desktopcomputer",accessibilityDescription:item.label);item.action=#selector(showHost)
        case "nav.settings":item.image=NSImage(systemSymbolName:"gearshape",accessibilityDescription:item.label);item.action=#selector(settings)
        default:return nil};return item}
    func navigate(_ key:String){if key=="host"{showHost();return};if key=="settings"{settings();return};state.page=key;split.refresh()}
    @objc func openSource(){let panel=NSOpenPanel();panel.title=L("source.title");panel.canChooseDirectories=true;panel.canChooseFiles=false;guard panel.runModal() == .OK,let url=panel.url else{return}
        let alert=NSAlert();alert.messageText=L("source.identifier");alert.informativeText=L("source.identifierHint");let field=NSTextField(string:state.sourceID);field.frame=NSRect(x:0,y:0,width:340,height:24);alert.accessoryView=field;alert.addButton(withTitle:L("source.confirm"));alert.addButton(withTitle:L("button.cancel"));guard alert.runModal() == .alertFirstButtonReturn else{return};state.inputURL=url;state.sourceID=field.stringValue;refreshSource()
    }
    @objc func refreshSource(){guard let url=state.inputURL else{openSource();return};split.main.busy=true
        bridge.inspect(directory:url,sourceID:state.sourceID){[weak self] result in guard let self else{return};self.split.main.busy=false
            switch result{case .success(let doc):self.state.document=doc;self.state.selected=doc.nodes.first?.id ?? "";self.state.query="";self.state.graphMode=0;self.split.main.build();self.split.refresh();self.split.main.updateGraph(fit:true)
            case .failure(let error):let key:String;switch error{case BridgeError.noRuntime:key="source.noRuntime";case BridgeError.cancelled:key="source.cancelled";case BridgeError.limit:key="source.timeout";case ModelError.invalidReport:key="source.invalid";default:key="source.failed"};showError(key)}
        }
    }
    @objc func openReport(){let p=NSOpenPanel();p.canChooseDirectories=false;p.allowedContentTypes=[.json];p.title=L("button.report");guard p.runModal() == .OK,let url=p.url else{return};do{state.document=try ReportProjection.decode(readBoundedReport(url));state.selected=state.document.nodes.first?.id ?? "";state.graphMode=0;state.inputURL=nil;split.main.build();split.refresh();split.main.updateGraph(fit:true)}catch{showError("source.invalid")}}
    @objc func exportReport(){let p=NSSavePanel();p.nameFieldStringValue="AgentAuthority-Evidence.json";p.title=L("export.title");guard p.runModal() == .OK,let url=p.url else{return};do{let data:Data;if let raw=state.document.reportJSON{data=Data(raw.utf8)}else{let encoder=JSONEncoder();encoder.outputFormatting=[.prettyPrinted,.sortedKeys];data=try encoder.encode(state.document)};try data.write(to:url,options:.atomic)}catch{showError("export.error")}}
    @objc func loadDemo(){state.document=DemoData.make();state.selected="agent-001";state.query="";state.filter=0;state.graphMode=2;state.inputURL=nil;state.expandedGroups=[];split.main.build();split.refresh();split.main.updateGraph(fit:true)}
    @objc func cancelRead(){bridge.cancel()}
    @objc func toggleSidebar(){split.splitViewItems[0].isCollapsed.toggle()}
    @objc func toggleInspector(){split.toggleInspector()}
    @objc func search(){split.main.focusSearch()}
    @objc func fit(){split.main.fitPressed()}
    @objc func minimize(){window.miniaturize(nil)}
    @objc func quit(){NSApp.terminate(nil)}
    @objc func about(){let a=NSAlert();a.messageText=L("app.name");a.informativeText=L("app.tagline")+"\n"+L("app.observer");a.addButton(withTitle:L("button.close"));a.runModal()}
    @objc func shortcuts(){let a=NSAlert();a.messageText=L("menu.shortcuts");a.informativeText=L("help.body");a.addButton(withTitle:L("button.close"));a.runModal()}
    @objc func showHost(){if hostWindow==nil{hostWindow=NSWindow(contentRect:NSRect(x:0,y:0,width:830,height:920),styleMask:[.titled,.closable,.resizable],backing:.buffered,defer:false);hostWindow?.isReleasedWhenClosed=false;hostWindow?.minSize=NSSize(width:780,height:850);hostWindow?.contentViewController=HostController(host);hostWindow?.center()};hostWindow?.title=L("host.title");hostWindow?.makeKeyAndOrderFront(nil);host.check()}
    @objc func settings(){if settingsWindow==nil{settingsWindow=NSWindow(contentRect:NSRect(x:0,y:0,width:530,height:315),styleMask:[.titled,.closable],backing:.buffered,defer:false);settingsWindow?.isReleasedWhenClosed=false;settingsWindow?.center()};settingsWindow?.title=L("settings.title");settingsWindow?.contentViewController=makeSettings();settingsWindow?.makeKeyAndOrderFront(nil)}
    func makeSettings()->NSViewController{let c=NSViewController();let root=LayoutView();c.view=root
        let language=label("settings.language"),appearance=label("settings.appearance"),runtime=label("settings.runtime"),note=wrapping(L("settings.note"))
        let lang=NSPopUpButton();lang.addItems(withTitles:[L("settings.system"),L("settings.de"),L("settings.en")]);lang.selectItem(at:["system","de","en"].firstIndex(of:Localization.shared.preference) ?? 0);lang.target=self;lang.action=#selector(languageChanged(_:))
        let theme=NSPopUpButton();theme.addItems(withTitles:[L("settings.systemTheme"),L("settings.dark"),L("settings.light")]);theme.selectItem(at:["system","dark","light"].firstIndex(of:UserDefaults.standard.string(forKey:"appearance") ?? "system") ?? 0);theme.target=self;theme.action=#selector(themeChanged(_:))
        let choose=button("settings.choosePython",target:self,action:#selector(choosePython));let path=wrapping(bridge.interpreter?.path ?? L("source.noRuntime"),size:10)
        [language,appearance,runtime,note,lang,theme,choose,path].forEach{root.addSubview($0)}
        root.arrange={r in language.frame=NSRect(x:22,y:27,width:170,height:24);lang.frame=NSRect(x:205,y:24,width:300,height:28);appearance.frame=NSRect(x:22,y:74,width:170,height:24);theme.frame=NSRect(x:205,y:70,width:300,height:28);runtime.frame=NSRect(x:22,y:121,width:200,height:24);choose.frame=NSRect(x:237,y:118,width:267,height:28);path.frame=NSRect(x:22,y:155,width:r.width-44,height:50);note.frame=NSRect(x:22,y:227,width:r.width-44,height:65)};return c
    }
    @objc func languageChanged(_ b:NSPopUpButton){Localization.shared.choose(["system","de","en"][b.indexOfSelectedItem])}
    @objc func themeChanged(_ b:NSPopUpButton){let theme=["system","dark","light"][b.indexOfSelectedItem];UserDefaults.standard.set(theme,forKey:"appearance");setAppearance(theme)}
    func setAppearance(_ theme:String){NSApp.appearance=theme=="dark" ? NSAppearance(named:.darkAqua):theme=="light" ? NSAppearance(named:.aqua):nil;split?.refresh()}
    @objc func choosePython(){let p=NSOpenPanel();p.canChooseDirectories=false;p.canChooseFiles=true;p.title=L("settings.choosePython");guard p.runModal() == .OK,let url=p.url,FileManager.default.isExecutableFile(atPath:url.path)else{return};UserDefaults.standard.set(url.path,forKey:"pythonPath");settingsWindow?.contentViewController=makeSettings()}
    func diagnostics(){
        if let path=argument("--ui-regression-json") {
            let result=runUIRegression()
            if let data=try? JSONSerialization.data(withJSONObject:result,options:[.prettyPrinted,.sortedKeys]){try? data.write(to:URL(fileURLWithPath:path))}
        }
        if let json=argument("--smoke-json"){
            let count=state.document.nodes.filter{$0.kind == .agent}.count
            var checks:[String:Any]=["native":true,"agents":count,"window_content_width":window.contentView!.bounds.width,"graph_nodes":split.main.canvas.displayNodes.count,"language":Localization.shared.language,"mode":"clustered"]
            state.selected="agent-013";state.graphMode=0;split.main.updateGraph(fit:true);split.select(state.selected)
            checks["chain_focus"]=split.main.canvas.displayNodes.contains{$0.id=="agent-013"};checks["chain_contains_process"]=split.main.canvas.displayNodes.contains{$0.id=="process-13"}
            split.main.canvas.zoom(1.15);checks["zoom_finite"]=split.main.canvas.scale.isFinite
            for page in ["overview","agents","delegations","actions","evidence","findings","graph"]{navigate(page)}
            state.graphMode=2;state.selected="agent-001";split.main.updateGraph(fit:true);split.select(state.selected)
            checks["permission_requests_executed"]=false
            checks["screen"]=NSScreen.main.map{["width":$0.frame.width,"height":$0.frame.height,"backing_scale":$0.backingScaleFactor]} ?? [:]
            checks["main_frame"]=NSStringFromRect(split.main.view.frame)
            checks["main_children"]=split.main.view.subviews.map{["class":String(describing:type(of:$0)),"frame":NSStringFromRect($0.frame)]}
            if let data=try? JSONSerialization.data(withJSONObject:checks,options:[.prettyPrinted,.sortedKeys]){try? data.write(to:URL(fileURLWithPath:json))}
        }
        window.contentView?.layoutSubtreeIfNeeded()
        split.main.view.needsLayout=true;split.main.view.layoutSubtreeIfNeeded()
        if let mode=argument("--graph-mode").flatMap(Int.init),[0,1,2].contains(mode){state.graphMode=mode;split.main.build();split.main.updateGraph(fit:true);window.contentView?.layoutSubtreeIfNeeded()}
        if let selected=argument("--select"){split.select(selected)}
        if CommandLine.arguments.contains("--reduce-motion"){split.main.canvas.forceReduceMotion=true}
        if let benchmark=argument("--bench-json"),let rep=split.main.canvas.bitmapImageRepForCachingDisplay(in:split.main.canvas.bounds){
            var times:[Double]=[]
            for _ in 0..<12{let start=DispatchTime.now().uptimeNanoseconds;split.main.canvas.cacheDisplay(in:split.main.canvas.bounds,to:rep);times.append(Double(DispatchTime.now().uptimeNanoseconds-start)/1_000_000)}
            let sorted=times.sorted(),record:[String:Any]=["method":"native AppKit own-view bitmap rendering; not a GPU frame-time measurement","iterations":times.count,"median_ms":sorted[sorted.count/2],"maximum_ms":sorted.last!,"nodes":split.main.canvas.displayNodes.count,"edges":split.main.canvas.displayEdges.count,"logical_width":split.main.canvas.bounds.width,"logical_height":split.main.canvas.bounds.height,"backing_scale":window.backingScaleFactor,"permanent_render_timer":false]
            if let data=try? JSONSerialization.data(withJSONObject:record,options:[.prettyPrinted,.sortedKeys]){try? data.write(to:URL(fileURLWithPath:benchmark))}
        }
        if let snapshot=argument("--snapshot"),let view=window.contentView,let rep=view.bitmapImageRepForCachingDisplay(in:view.bounds){view.cacheDisplay(in:view.bounds,to:rep);if let data=rep.representation(using:.png,properties:[:]){try? data.write(to:URL(fileURLWithPath:snapshot))}}
        NSApp.terminate(nil)
    }
}
let application=NSApplication.shared
let delegate=AppDelegate()
application.setActivationPolicy(.regular)
application.delegate=delegate
application.run()
