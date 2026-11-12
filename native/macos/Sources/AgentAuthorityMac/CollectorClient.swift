import Foundation
import AuthorityCore
import NativeSupport

final class CollectorClient {
    private var closed=false
    private let team=Bundle.main.object(forInfoDictionaryKey:"AAExpectedTeam") as? String ?? ""
    func close(){closed=true}
    func send(_ request:[String:Any],completion:@escaping(Result<[String:Any],Error>)->Void){
        guard !closed,team.range(of:"^[A-Z0-9]{10}$",options:.regularExpression) != nil else{completion(.failure(BridgeError.failed));return}
        guard let data=try? JSONSerialization.data(withJSONObject:request),let text=String(data:data,encoding:.utf8)else{completion(.failure(BridgeError.failed));return}
        let service=team+".de.agentauthority.observer.collector.xpc"
        let requirement="anchor apple generic and identifier \"de.agentauthority.observer.collector\" and certificate leaf[subject.OU] = \"\(team)\""
        aa_rpc_request(service,requirement,text){ [weak self] raw in
            guard let raw else{return};let data=Data(String(cString:raw).utf8)
            let result:Result<[String:Any],Error>
            if let object=(try? JSONSerialization.jsonObject(with:data)) as? [String:Any],object["error"]==nil{result = .success(object)}else{result = .failure(BridgeError.failed)}
            DispatchQueue.main.async{guard self?.closed==false else{return};completion(result)}
        }
    }
    func status(_ completion:@escaping(Result<[String:Any],Error>)->Void){
        send(["command":"status"]){result in
            // This authenticated collector status is UI metadata, not complete activity coverage.
            let state:String
            switch result {case .success(let status):state = status["es_result"] as? Int == 0 ? "confirmed" : "error"
            case .failure:state = "unknown"}
            NotificationCenter.default.post(name:Notification.Name("AgentAuthorityCollectorStatus"),object:nil,userInfo:["state":state])
            completion(result)
        }
    }
    func begin(dev:UInt64,inode:UInt64,_ completion:@escaping(Result<[String:Any],Error>)->Void){send(["command":"scope","dev":dev,"inode":inode],completion:completion)}
    func events(_ completion:@escaping(Result<[String:Any],Error>)->Void){send(["command":"events"],completion:completion)}
    func end(_ completion:@escaping(Result<[String:Any],Error>)->Void){send(["command":"end"],completion:completion)}
}

enum WriterControls {
    /// Six real controls, enabled only after a qualified, independent ES source.
    static func run(collector:CollectorClient,completion:@escaping(Result<[String:Any],Error>)->Void){
        collector.status{ result in guard case .success(let status)=result,status["es_result"] as? Int == 0 else{completion(.failure(BridgeError.failed));return}
            let folder=FileManager.default.temporaryDirectory.appendingPathComponent("AgentAuthority-"+UUID().uuidString,isDirectory:true)
            do{try FileManager.default.createDirectory(at:folder,withIntermediateDirectories:false,attributes:[.posixPermissions:0o700])}catch{completion(.failure(error));return}
            let target=folder.appendingPathComponent("target"),other=folder.appendingPathComponent("other")
            guard FileManager.default.createFile(atPath:target.path,contents:Data(),attributes:[.posixPermissions:0o600]),FileManager.default.createFile(atPath:other.path,contents:Data(),attributes:[.posixPermissions:0o600])else{try? FileManager.default.removeItem(at:folder);completion(.failure(BridgeError.failed));return}
            let fd=open(target.path,O_RDONLY|O_NOFOLLOW),otherFD=open(other.path,O_RDONLY|O_NOFOLLOW)
            var st=stat();guard fd>=0,otherFD>=0,fstat(fd,&st)==0 else{if fd>=0{Darwin.close(fd)};if otherFD>=0{Darwin.close(otherFD)};try? FileManager.default.removeItem(at:folder);completion(.failure(BridgeError.failed));return}
            collector.begin(dev:UInt64(st.st_dev),inode:st.st_ino){ started in
                guard case .success = started,let exe=Bundle.main.url(forAuxiliaryExecutable:"AAWriter")else{Darwin.close(fd);Darwin.close(otherFD);try? FileManager.default.removeItem(at:folder);completion(.failure(BridgeError.failed));return}
                let cases=[("A","write",target.path),("B","idle",target.path),("C","write",other.path),("child","child",target.path),("forged","forged",target.path),("sequential-1","write",target.path),("sequential-2","write",target.path)]
                var results:[[String:Any]]=[]
                func step(_ index:Int){
                    if index>=cases.count{DispatchQueue.main.asyncAfter(deadline:.now()+0.5){collector.events{events in
                        collector.end{_ in Darwin.close(fd);Darwin.close(otherFD);try? FileManager.default.removeItem(at:folder)}
                        guard case .success(let observed)=events else{completion(.failure(BridgeError.failed));return}
                        let writes=(observed["events"] as? [[String:Any]] ?? []).filter{$0["event"] as? String == "write"}
                        let lossKnown=observed["sequence_available"] as? Bool == true,losses=observed["sequence_gaps"] as? Int ?? -1,localLoss=observed["buffer_dropped"] as? Int ?? -1
                        let allEvents=observed["events"] as? [[String:Any]] ?? []
                        var casesOutput:[[String:Any]]=[]
                        for row in results{let actual=row["writer_pid"] as? Int ?? -1,label=row["case"] as? String ?? "",expected=label != "B"&&label != "C"
                            func sameInstance(_ e:[String:Any])->Bool{e["pid"] as? Int==actual && (e["pid_version"] as? Int)==(row["pid_version"] as? Int) && (e["start_sec"] as? Int)==(row["start_sec"] as? Int) && (e["start_usec"] as? Int)==(row["start_usec"] as? Int)}
                            let matches=writes.filter(sameInstance),lifecycle=allEvents.filter{["exec","fork","exit"].contains($0["event"] as? String ?? "") && sameInstance($0)}
                            let qualified=lossKnown&&losses==0&&localLoss==0&&actual>0 && observed["sequence_invalid"] as? Int == 0 && observed["scope_active"] as? Bool == true && row["audit_status"] as? Int == 0 && (row["bsd_bytes"] as? Int ?? 0)>0 && !lifecycle.isEmpty
                            casesOutput.append(["case":label,"actual_writer_pid":actual,"matching_events":matches.count,"lifecycle_events":lifecycle.count,"expected_target_write":expected,"attribution":qualified && (expected ? matches.count==1:matches.isEmpty) ? "BELEGT_IM_TESTSCOPE":"UNBEKANNT"])
                        }
                        completion(.success(["schema":"agent-authority-macos-writer-controls-v1","cases":casesOutput,"collector":observed,"reference":results,"provider_identity":"UNBEKANNT","durable_effect":"UNBEKANNT","forged_pid_claim":999999,"claim_used_for_attribution":false]))
                    }};return}
                    let row=cases[index];runTool(executable:exe,arguments:[row.1,row.2],timeout:3){ result in
                        guard case .success(let data)=result,var record=(try? JSONSerialization.jsonObject(with:data)) as? [String:Any]else{collector.end{_ in Darwin.close(fd);Darwin.close(otherFD);try? FileManager.default.removeItem(at:folder)};completion(.failure(BridgeError.failed));return}
                        record["case"]=row.0;results.append(record);step(index+1)
                    }
                }
                step(0)
            }
        }
    }
}
