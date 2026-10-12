import AppKit
import ApplicationServices
import Carbon
import Security
import SystemExtensions
import AuthorityCore

final class PermissionHost:NSObject,OSSystemExtensionRequestDelegate {
    static let extensionID="de.agentauthority.observer.collector"
    var onUpdate:(()->Void)?
    var statuses:[String:String]=[:]
    var evidence:[String:Any]=["schema":"agent-authority-testhost-v1","writer_attribution":"UNBEKANNT","provider_identity":"UNBEKANNT"]
    var collector:CollectorClient?
    var onEvents:((GraphDocument)->Void)?
    func check(){statuses["ax"]=AXIsProcessTrusted() ? "status.ready":"status.denied";statuses["screen"]=CGPreflightScreenCaptureAccess() ? "status.ready":"status.denied"
        statuses["es"]=hasEntitlement("com.apple.developer.system-extension.install") ? "status.notChecked":"status.needsSigning"
        statuses["fda"]="status.notChecked";onUpdate?()
    }
    func hasEntitlement(_ key:String)->Bool{var code:SecCode?;guard SecCodeCopySelf([], &code)==errSecSuccess,let code else{return false};var staticCode:SecStaticCode?
        guard SecCodeCopyStaticCode(code,[],&staticCode)==errSecSuccess,let staticCode else{return false};var info:CFDictionary?
        guard SecCodeCopySigningInformation(staticCode,SecCSFlags(rawValue:kSecCSSigningInformation),&info)==errSecSuccess,let dict=info as? [String:Any],let entitlements=dict[kSecCodeInfoEntitlementsDict as String] as? [String:Any]else{return false};return entitlements[key] as? Bool == true}
    func requestAX(){let opts=[kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String:true] as CFDictionary;statuses["ax"]=AXIsProcessTrustedWithOptions(opts) ? "status.ready":"status.denied";onUpdate?()}
    func requestScreen(){statuses["screen"]=CGRequestScreenCaptureAccess() ? "status.ready":"status.denied";onUpdate?()}
    func openPrivacy(_ anchor:String){let modern:Bool;if #available(macOS 13,*){modern=true}else{modern=false};let prefix=modern ? "x-apple.systempreferences:com.apple.settings.PrivacySecurity.extension?":"x-apple.systempreferences:com.apple.preference.security?";if let url=URL(string:prefix+anchor){NSWorkspace.shared.open(url)}}
    func requestAutomation(){let p=NSOpenPanel();p.canChooseDirectories=false;p.canChooseFiles=true;p.allowedContentTypes=[.application];p.title=L("host.automationTarget");guard p.runModal() == .OK,let url=p.url,let id=Bundle(url:url)?.bundleIdentifier else{return}
        var target=AEAddressDesc();let bytes=Array(id.utf8)
        let created=bytes.withUnsafeBytes{AECreateDesc(DescType(typeApplicationBundleID),$0.baseAddress,bytes.count,&target)}
        guard created==noErr else{statuses["automation"]="status.denied";onUpdate?();return};defer{AEDisposeDesc(&target)}
        let result=AEDeterminePermissionToAutomateTarget(&target,AEEventClass(typeWildCard),AEEventID(typeWildCard),true)
        statuses["automation"]=result==noErr ? "status.ready":"status.denied";evidence["automation"]=["target":id,"os_status":result];onUpdate?()
    }
    func activate(){guard hasEntitlement("com.apple.developer.system-extension.install") else{statuses["es"]="status.needsSigning";onUpdate?();return}
        let request=OSSystemExtensionRequest.activationRequest(forExtensionWithIdentifier:Self.extensionID,queue:.main);request.delegate=self;OSSystemExtensionManager.shared.submitRequest(request)
    }
    func request(_ request:OSSystemExtensionRequest,actionForReplacingExtension existing:OSSystemExtensionProperties,withExtension ext:OSSystemExtensionProperties)->OSSystemExtensionRequest.ReplacementAction{.replace}
    func requestNeedsUserApproval(_ request:OSSystemExtensionRequest){statuses["es"]="host.extensionWaiting";onUpdate?()}
    func request(_ request:OSSystemExtensionRequest,didFinishWithResult result:OSSystemExtensionRequest.Result){statuses["es"]=result == .willCompleteAfterReboot ? "host.extensionReboot":"host.extensionDone";onUpdate?()}
    func request(_ request:OSSystemExtensionRequest,didFailWithError error:Error){statuses["es"]="host.extensionError";evidence["activation_error"]=(error as NSError).code;onUpdate?()}
    func connect(){let client=CollectorClient();collector=client
        client.status{[weak self] result in switch result{case .success(let status):self?.evidence["collector"]=status
                let code=status["es_result"] as? Int ?? -1
                self?.statuses["fda"]=code==0 ? "status.ready":code==4 ? "status.denied":"status.notChecked"
                switch code{case 0:self?.statuses["es"]="host.collectorReady";case 3:self?.statuses["es"]="status.needsApple";case 4:self?.statuses["es"]="host.collectorUnavailable";case 5:self?.statuses["es"]="host.privilege";default:self?.statuses["es"]="host.collectorError"}
            case .failure:self?.statuses["es"]="host.collectorUnavailable"};self?.onUpdate?()}
    }
    func runProbe(){statuses["probe"]="status.busy";onUpdate?()
        guard let exe=Bundle.main.url(forAuxiliaryExecutable:"AAProcessProbe")else{statuses["probe"]="error.unsupported";onUpdate?();return}
        runTool(executable:exe,arguments:[],timeout:5){[weak self] result in
            switch result{case .success(let data):self?.evidence["process_probe"]=(try? JSONSerialization.jsonObject(with:data)) ?? NSNull();self?.statuses["probe"]="host.probeResult"
            case .failure:self?.statuses["probe"]="source.failed"};self?.onUpdate?()
        }
    }
    func runWriters(){guard let collector else{statuses["writer"]="host.writerBlocked";onUpdate?();return}
        statuses["writer"]="status.busy";onUpdate?()
        WriterControls.run(collector:collector){[weak self] result in
            switch result{case .success(let record):self?.evidence["writer_controls"]=record;self?.statuses["writer"]="host.writerDone";if let events=record["collector"] as? [String:Any]{self?.onEvents?(NativeProjection.make(events))}
                case .failure:self?.statuses["writer"]="host.writerBlocked"};self?.onUpdate?()
        }
    }
    func export(){let p=NSSavePanel();p.title=L("host.saved");p.nameFieldStringValue="AgentAuthority-Testhost.json";guard p.runModal() == .OK,let url=p.url else{return};do{let data=try JSONSerialization.data(withJSONObject:evidence,options:[.prettyPrinted,.sortedKeys]);try data.write(to:url,options:.atomic)}catch{showError("export.error")}}
}

func runTool(executable:URL,arguments:[String],timeout:Double,completion:@escaping(Result<Data,Error>)->Void){
    DispatchQueue.global(qos:.userInitiated).async {
        let p=Process(),out=Pipe();p.executableURL=executable;p.arguments=arguments;p.standardOutput=out;p.standardError=FileHandle.nullDevice;p.environment=["PATH":"/usr/bin:/bin","HOME":NSHomeDirectory()]
        let deadline=DispatchWorkItem{if p.isRunning{p.terminate()}}
        do{try p.run();DispatchQueue.global().asyncAfter(deadline:.now()+timeout,execute:deadline);let data=out.fileHandleForReading.readDataToEndOfFile();p.waitUntilExit();deadline.cancel();guard p.terminationStatus==0,data.count<=1024*1024 else{throw BridgeError.failed};DispatchQueue.main.async{completion(.success(data))}}
        catch{deadline.cancel();DispatchQueue.main.async{completion(.failure(error))}}
    }
}
func showError(_ key:String){let a=NSAlert();a.messageText=L("error.title");a.informativeText=L(key);a.addButton(withTitle:L("button.close"));a.runModal()}

final class HostController:NSViewController {
    let host:PermissionHost
    init(_ host:PermissionHost){self.host=host;super.init(nibName:nil,bundle:nil)}
    required init?(coder:NSCoder){fatalError()}
    override func loadView(){view=LayoutView();reload()}
    func reload(){guard isViewLoaded else{return};view.subviews.forEach{$0.removeFromSuperview()};let root=view as! LayoutView
        let title=label("host.title",size:21,weight:.semibold),intro=wrapping(L("host.intro"),size:12);root.addSubview(title);root.addSubview(intro)
        var rows:[(NSTextField,NSTextField,NSTextField,NSButton)]=[]
        let definitions:[(String,String,String)]=[("files","host.filesDetail","button.open"),("ax","host.axDetail","button.request"),("screen","host.screenDetail","button.request"),("automation","host.automationDetail","host.automationTarget"),("fda","host.fdaDetail","button.system"),("es","host.esDetail","button.activate"),("probe","host.probeDetail","button.run"),("writer","host.writerDetail","button.run")]
        for (id,detail,key) in definitions {
            let h=label("host."+id,size:12,weight:.medium),body=wrapping(L(detail),size:11),status=wrapping(L(host.statuses[id] ?? "status.notChecked"),size:10,color:Palette.amber),b=button(key,target:self,action:#selector(action(_:)));b.identifier=NSUserInterfaceItemIdentifier(id)
            [h,body,status,b].forEach{root.addSubview($0)};rows.append((h,body,status,b))
        }
        let check=button("button.check",target:self,action:#selector(checkPressed)),connect=button("button.connect",target:self,action:#selector(connectPressed)),save=button("host.saved",target:self,action:#selector(savePressed)),request=button("host.entitlement",target:self,action:#selector(entitlementPressed)),note=wrapping(L("host.boundaries"),size:11)
        [check,connect,save,request,note].forEach{root.addSubview($0)}
        root.arrange={r in title.frame=NSRect(x:22,y:17,width:r.width-44,height:30);intro.frame=NSRect(x:22,y:54,width:r.width-44,height:45)
            let rowHeight=min(85,max(68,(r.height-196)/8))
            for (i,row) in rows.enumerated(){let y=110+CGFloat(i)*rowHeight;row.0.frame=NSRect(x:22,y:y,width:220,height:18);row.1.frame=NSRect(x:22,y:y+22,width:r.width-240,height:44);row.2.frame=NSRect(x:r.width-210,y:y,width:186,height:38);row.3.frame=NSRect(x:r.width-210,y:y+41,width:187,height:25)}
            let y=110+CGFloat(rows.count)*rowHeight+4;check.frame=NSRect(x:22,y:y,width:90,height:26);connect.frame=NSRect(x:120,y:y,width:171,height:26);save.frame=NSRect(x:300,y:y,width:190,height:26);request.frame=NSRect(x:500,y:y,width:210,height:26);note.frame=NSRect(x:22,y:y+38,width:r.width-44,height:43)
        };view.needsLayout=true
    }
    @objc private func action(_ b:NSButton){switch b.identifier?.rawValue{case "files":let p=NSOpenPanel();p.canChooseDirectories=true;p.canChooseFiles=false;p.title=L("source.title");if p.runModal() == .OK{host.statuses["files"]="status.selected";host.onUpdate?()}
        case "ax":host.requestAX();case "screen":host.requestScreen();case "automation":host.requestAutomation();case "fda":host.openPrivacy("Privacy_AllFiles");case "es":host.activate();case "probe":host.runProbe();case "writer":host.runWriters();default:break}}
    @objc private func checkPressed(){host.check()}
    @objc private func connectPressed(){host.connect()}
    @objc private func savePressed(){host.export()}
    @objc private func entitlementPressed(){NSWorkspace.shared.open(URL(string:"https://developer.apple.com/system-extensions/")!)}
}
