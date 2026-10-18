import Foundation
import CoreFoundation

public enum NodeKind: String, Codable, CaseIterable {
    case agent, identity, authority, delegation, process, action, evidence, task, entry, cluster
    public var label: String { L("kind." + rawValue) }
    public var symbol: String {
        switch self {
        case .agent: return "person.crop.circle"
        case .identity: return "person.text.rectangle"
        case .authority: return "checkmark.shield"
        case .delegation: return "link"
        case .process: return "cpu"
        case .action: return "doc.badge.gearshape"
        case .evidence: return "doc.text.magnifyingglass"
        case .task: return "list.bullet.rectangle"
        case .entry: return "doc.text"
        case .cluster: return "square.stack.3d.up"
        }
    }
}
public enum ProofStatus: String, Codable, CaseIterable {
    case reported, observed, verified, incomplete, contradictory, unknown
    public var label: String { L("status." + rawValue) }
}
public struct Fact: Codable, Equatable {
    public var labelKey: String
    public var value: String
    public var valueKey: Bool = false
    public init(_ label: String, _ value: String, localized: Bool = false) { labelKey=label; self.value=value; valueKey=localized }
    public var text: String { valueKey ? L(value) : value }
}
public struct GraphNode: Codable, Equatable, Identifiable {
    public var id: String
    public var kind: NodeKind
    public var name: String
    public var nameKey: Bool = false
    public var status: ProofStatus
    public var group: String
    public var facts: [Fact]
    public var evidence: [String]
    public var title: String { nameKey ? L(name) : name }
    public init(id: String, kind: NodeKind, name: String, localized: Bool = false, status: ProofStatus,
                group: String = "", facts: [Fact] = [], evidence: [String] = []) {
        self.id=id; self.kind=kind; self.name=name; nameKey=localized; self.status=status; self.group=group; self.facts=facts; self.evidence=evidence
    }
}
public struct GraphEdge: Codable, Equatable {
    public var from: String; public var to: String; public var relation: String; public var status: ProofStatus; public var evidence: [String]
    public init(_ from: String, _ to: String, _ relation: String, _ status: ProofStatus, evidence: [String] = []) {
        self.from=from; self.to=to; self.relation=relation; self.status=status; self.evidence=evidence
    }
}
public struct GraphDocument: Codable {
    public var schema = "agent-authority-ui-graph-v1"
    public var source: String
    public var isDemo: Bool
    public var nodes: [GraphNode]
    public var edges: [GraphEdge]
    public var reportJSON: String?
    public var reportSource: Bool?
    public var isReportSource: Bool { reportSource == true || reportJSON != nil }
    public var completeRead: Bool?
    public var totalEntries: Int?
    public var reportedTaskCount: Int?
    public var reportedWarningCount: Int?
    public var omitted: Int = 0
    public var warnings: [String] = []
    public init(source: String, demo: Bool = false, nodes: [GraphNode] = [], edges: [GraphEdge] = []) {
        self.source=source; isDemo=demo; self.nodes=nodes; self.edges=edges
    }
    public func validate() throws {
        guard schema == "agent-authority-ui-graph-v1", nodes.count <= 10_000, edges.count <= 30_000 else { throw ModelError.bounds }
        let ids = Set(nodes.map(\.id))
        guard ids.count == nodes.count, nodes.allSatisfy({ !$0.id.isEmpty && $0.id.count<=128 && $0.name.count<=300 && $0.facts.count<=32 && $0.evidence.count<=64 }),
              edges.allSatisfy({ ids.contains($0.from) && ids.contains($0.to) && $0.evidence.count<=64 }) else { throw ModelError.references }
    }
    /// Connected chain, bounded by the graph contract. Does not create evidence.
    public func neighborhood(_ id: String) -> Set<String> {
        var visited: Set<String> = [id], queue = [id], cursor = 0
        var neighbors: [String: [String]] = [:]
        for e in edges { neighbors[e.from, default: []].append(e.to); neighbors[e.to, default: []].append(e.from) }
        while cursor < queue.count { let next=queue[cursor]; cursor+=1
            for n in neighbors[next,default:[]] where !visited.contains(n) { visited.insert(n); queue.append(n) }
        }
        return visited
    }
    public func trace(_ id:String) -> Set<String> {
        var result:Set<String>=[id],queue=[id],cursor=0
        var parents:[String:[String]]=[:],children:[String:[String]]=[:]
        let kinds=Dictionary(uniqueKeysWithValues:nodes.map{($0.id,$0.kind)})
        for e in edges{parents[e.to,default:[]].append(e.from);children[e.from,default:[]].append(e.to)}
        while cursor<queue.count{let current=queue[cursor];cursor+=1;for p in parents[current,default:[]] where !result.contains(p){result.insert(p);queue.append(p)}}
        queue=[id];cursor=0
        while cursor<queue.count{let current=queue[cursor];cursor+=1
            for n in children[current,default:[]] where !result.contains(n) && kinds[n] != .agent {result.insert(n);queue.append(n)}
        }
        return result
    }
    /// Chain quality includes every parent and relationship, not just a local identity.
    public func chainStatuses()->[String:ProofStatus] {
        guard isDemo else{return Dictionary(uniqueKeysWithValues:nodes.map{($0.id,.unknown)})}
        let rank:[ProofStatus:Int]=[.verified:0,.observed:0,.reported:1,.unknown:2,.incomplete:3,.contradictory:4]
        func worse(_ a:ProofStatus,_ b:ProofStatus)->ProofStatus{(rank[a] ?? 4)>=(rank[b] ?? 4) ? a:b}
        var results=Dictionary(uniqueKeysWithValues:nodes.map{($0.id,$0.status == .observed ? .verified:$0.status)})
        var incoming=Dictionary(uniqueKeysWithValues:nodes.map{($0.id,0)}),outgoing:[String:[GraphEdge]]=[:]
        for e in edges{incoming[e.to,default:0]+=1;outgoing[e.from,default:[]].append(e)}
        var queue=nodes.map(\.id).filter{incoming[$0]==0},cursor=0,visited:Set<String>=[]
        while cursor<queue.count{let id=queue[cursor];cursor+=1;visited.insert(id)
            for e in outgoing[id,default:[]]{results[e.to]=worse(worse(results[e.to] ?? .unknown,results[id] ?? .unknown),e.status == .observed ? .verified:e.status);incoming[e.to,default:0]-=1;if incoming[e.to]==0{queue.append(e.to)}}
        }
        for n in nodes where !visited.contains(n.id){results[n.id] = .contradictory}
        return results
    }
}
public enum ModelError: Error { case bounds, references, schema, invalidReport, inputTooLarge }

public enum DemoData {
    public static func make(agents: Int = 50) -> GraphDocument {
        let count = min(max(agents, 2), 1000)
        var doc=GraphDocument(source:"AA-SAMPLE",demo:true)
        doc.nodes.append(GraphNode(id:"root",kind:.agent,name:"demo.coordinator",localized:true,status:.verified,group:"root",facts:[Fact("field.identity","AA-ROOT"),Fact("field.anchor","demo.testCA",localized:true)]))
        doc.nodes.append(GraphNode(id:"identity-root",kind:.identity,name:"demo.testCA",localized:true,status:.verified,group:"root",facts:[Fact("field.anchor","demo.controller",localized:true)]))
        doc.nodes.append(GraphNode(id:"authority-root",kind:.authority,name:"demo.authority",localized:true,status:.verified,group:"root",facts:[Fact("field.issuer","demo.controller",localized:true),Fact("field.scope","demo.scope",localized:true)]))
        doc.edges += [GraphEdge("identity-root","root","identity",.verified),GraphEdge("authority-root","root","authority",.verified)]
        for i in 1..<count {
            let id=String(format:"agent-%03d",i), branch="branch-\((i-1)/10)", status: ProofStatus = i%13==0 ? .incomplete : (i%17==0 ? .unknown : .verified)
            let parent=i<=5 ? "root" : String(format:"agent-%03d",(i-1)/2)
            let pid=8000+i
            doc.nodes.append(GraphNode(id:id,kind:.agent,name:String(format:"AA-%03d",i),status:status,group:branch,
                facts:[Fact("field.identity",id),Fact("field.anchor","demo.testCA",localized:true),Fact("field.authority","authority-root"),Fact("field.provider","status.unknown",localized:true)],evidence:["E-\(i)-ID"]))
            doc.edges.append(GraphEdge(parent,id,"delegates",status,evidence:["E-\(i)-D"]))
            let process=GraphNode(id:"process-\(i)",kind:.process,name:"python3.12",status:status == .verified ? .observed : .unknown,group:branch,
                facts:[Fact("field.pid",String(pid)),Fact("field.instance","SAMPLE-\(i)"),Fact("field.start","demo.synthetic",localized:true)],evidence:["E-\(i)-P"])
            let action=GraphNode(id:"action-\(i)",kind:.action,name:"demo.write",localized:true,status:status == .verified ? .observed : .reported,group:branch,
                facts:[Fact("field.object","SAMPLE-OBJ-\(i)"),Fact("field.effect","boundary.durable",localized:true)],evidence:["E-\(i)-W"])
            doc.nodes += [process,action]
            doc.edges += [GraphEdge(id,process.id,"bound",status),GraphEdge(process.id,action.id,"caused",status)]
        }
        return doc
    }
}

public enum ReportProjection {
    public static func decode(_ data: Data) throws -> GraphDocument {
        guard data.count<=8*1024*1024 else { throw ModelError.inputTooLarge }
        guard let envelope=try JSONSerialization.jsonObject(with:data) as? [String:Any] else {throw ModelError.invalidReport}
        var raw=envelope
        var workflowEvents:[[String:Any]]=[]
        if envelope["schema_version"] as? String == "agent-authority-workflow-report-v1" {
            guard envelope["role"] as? String == "observer_only", let base=envelope["observation_report"] as? [String:Any],
                  let events=envelope["events"] as? [[String:Any]],events.count<=100 else {throw ModelError.invalidReport}
            raw=base;workflowEvents=events
            var warnings=raw["warnings"] as? [[String:Any]] ?? []
            for warning in envelope["warnings"] as? [[String:Any]] ?? [] {
                guard let code=warning["code"] as? String,code.hasPrefix("workflow_"),code.count<=80 else {continue}
                var projected:[String:Any]=["code":code,"evidence":[]]
                if let entry=warning["entry_id"] as? String {projected["evidence"]=[["entry_id":entry]]}
                warnings.append(projected)
            }
            raw["warnings"]=warnings
            var summary=raw["summary"] as? [String:Any] ?? [:]
            summary["structural_warning_count"]=warnings.count;raw["summary"]=summary
        }
        guard raw["schema_version"] as? String == "agent-authority-observation-report-v1",raw["role"] as? String == "observer_only",
              let source=raw["source"] as? [String:Any],let entries=raw["recent_entries"] as? [[String:Any]] else {throw ModelError.invalidReport}
        var doc=GraphDocument(source:source["source_id"] as? String ?? "json-directory")
        doc.completeRead=source["complete_observed_read"] as? Bool
        doc.totalEntries=source["entries_read"] as? Int
        doc.reportedTaskCount=(raw["summary"] as? [String:Any])?["tasks_with_reported_association"] as? Int
        doc.reportedWarningCount=(raw["summary"] as? [String:Any])?["structural_warning_count"] as? Int
        doc.omitted=(raw["display"] as? [String:Any])?["entries_omitted"] as? Int ?? 0
        doc.warnings=(raw["warnings"] as? [[String:Any]] ?? []).compactMap { $0["code"] as? String }
        // Workflow imports export the existing minimized GraphDocument, never arbitrary original extras.
        doc.reportSource=true
        doc.reportJSON=envelope["schema_version"] as? String == "agent-authority-workflow-report-v1" ? nil:String(data:data,encoding:.utf8)
        var refs: Set<String> = []
        for entry in entries {
            guard let id=entry["entry_id"] as? String, let ordinal=entry["ordinal"] as? Int, let kind=entry["reported_kind"] as? String,
                  let actor=entry["reported_actor_type"] as? String, let hash=entry["file_sha256"] as? String,
                  ordinal>=0, id.range(of:"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$",options:.regularExpression) != nil,
                  hash.range(of:"^[0-9a-f]{64}$",options:.regularExpression) != nil,
                  !actor.isEmpty,actor.count<=80, ["note","task","claimed","progress","result","decision","problem","question","system","plan","handoff"].contains(kind) else { throw ModelError.invalidReport }
            refs.insert(id)
            doc.nodes.append(GraphNode(id:id,kind:.entry,name:"entry."+kind,localized:true,status:.reported,
                facts:[Fact("field.actor",actor),Fact("field.ordinal",String(ordinal)),Fact("field.sha256",hash),Fact("field.identity","status.unknown",localized:true),Fact("field.effect","status.unknown",localized:true)],evidence:[id]))
        }
        for event in workflowEvents {
            guard let id=event["entry_id"] as? String,let index=doc.nodes.firstIndex(where:{$0.id==id}),
                  let binding=event["binding"] as? [String:Any] else {continue}
            let allowed:Set<String>=["project_id","workflow_id","thread_id","handoff_id","handoff_revision","source_revision","source_ref","source_hash","request_hash","task_id","original_task_id","bridge_task_id","run_id","attempt_id","parent_task_id","subtask_id","return_id","recipient_id","session_id","principal_ref","operator_scope","actor_claim","task_revision","artifact_ref","dispatch_seq","barrier_seq","reserved_microusd","spent_microusd","available_microusd","cost_kind","stop_state","reported_status"]
            let priority=["project_id","workflow_id","original_task_id","bridge_task_id","task_id","handoff_id","handoff_revision","source_revision","source_ref","source_hash","run_id","attempt_id","session_id","principal_ref","operator_scope","request_hash"]
            let present=binding.keys.filter{allowed.contains($0)}
            let selected=priority.filter{present.contains($0)}+present.filter{!priority.contains($0)}.sorted()
            for key in selected.prefix(24) {
                if let value=binding[key] as? String,value.count<=256 {doc.nodes[index].facts.append(Fact("workflow."+key,value))}
                else if let value=binding[key] as? NSNumber,CFGetTypeID(value) != CFBooleanGetTypeID(),["i","q","s","l","I","Q","S","L"].contains(String(cString:value.objCType)),value.int64Value>=0 {
                    doc.nodes[index].facts.append(Fact("workflow."+key,value.stringValue))
                }
            }
            if selected.count>24 {doc.nodes[index].facts.append(Fact("workflow.omitted_fields",String(selected.count-24)))}
            doc.nodes[index].facts.append(Fact("workflow.basis","workflow.claimsOnly",localized:true))
            // Never promote a producer's actor/model/status or hash to verified proof.
            doc.nodes[index].status = .reported
        }
        for task in raw["tasks"] as? [[String:Any]] ?? [] {
            guard let alias=task["task_alias"] as? String else { continue }
            let nodeID="task-"+alias
            doc.nodes.append(GraphNode(id:nodeID,kind:.task,name:alias,status:.reported,group:nodeID,
                facts:[Fact("field.basis","basis.task",localized:true),Fact("field.identity","status.unknown",localized:true)]))
            for ref in task["evidence"] as? [[String:Any]] ?? [] {
                if let id=ref["entry_id"] as? String, refs.contains(id) { doc.edges.append(GraphEdge(nodeID,id,"reportedTask",.reported,evidence:[id])) }
            }
        }
        for (index,warning) in (raw["warnings"] as? [[String:Any]] ?? []).enumerated(){
            guard let code=warning["code"] as? String else{continue}
            let id="warning-\(index)",evidence=(warning["evidence"] as? [[String:Any]] ?? []).compactMap{$0["entry_id"] as? String}
            let key="diagnostic."+code
            let warningStatus:ProofStatus=["workflow_duplicate_conflict","workflow_ordinal_conflict"].contains(code) ? .contradictory:.incomplete
            doc.nodes.append(GraphNode(id:id,kind:.evidence,name:key,localized:Localization.shared.catalog[key] != nil,status:warningStatus,facts:[Fact("field.diagnostic",code)],evidence:evidence))
            for ref in evidence where refs.contains(ref){doc.edges.append(GraphEdge(id,ref,"evidence",.incomplete,evidence:[ref]))}
        }
        try doc.validate()
        return doc
    }
}

public struct LayoutPoint: Equatable { public var x: Double; public var y: Double }
public struct GraphLayout {
    public var positions: [String:LayoutPoint]
    public var width: Double; public var height: Double
    /// Small agent overview: branch columns, compact rows; original delegation edges retained.
    public static func agents(_ nodes:[GraphNode],columns:Int=5)->GraphLayout {
        let agentNodes=nodes.filter{$0.kind == .agent && $0.group != "root"}.sorted{$0.id<$1.id}
        var positions:[String:LayoutPoint]=[:]
        let columns=max(3,columns)
        for (index,node) in agentNodes.enumerated(){positions[node.id]=LayoutPoint(x:24+Double(index%columns)*158,y:120+Double(index/columns)*60)}
        for (index,n) in nodes.filter({$0.group=="root"}).sorted(by:{$0.id<$1.id}).enumerated(){positions[n.id]=LayoutPoint(x:24+Double(index)*158,y:24)}
        return GraphLayout(positions:positions,width:Double(columns)*158+48,height:Double((agentNodes.count+columns-1)/columns)*60+150)
    }
    /// Kahn ordering with a finite cyclic fallback. Stable IDs avoid runtime jitter.
    public static func make(nodes: [GraphNode], edges: [GraphEdge], compact: Bool = true) -> GraphLayout {
        let ids=Set(nodes.map(\.id));var indegree=Dictionary(uniqueKeysWithValues:ids.map{($0,0)})
        var outgoing:[String:[String]]=[:],depth:[String:Int]=[:]
        for e in edges where ids.contains(e.from)&&ids.contains(e.to) { outgoing[e.from,default:[]].append(e.to); indegree[e.to,default:0]+=1 }
        var queue=ids.filter{indegree[$0]==0}.sorted(), cursor=0
        for id in queue { depth[id]=0 }
        while cursor<queue.count { let id=queue[cursor];cursor+=1
            for n in outgoing[id,default:[]].sorted() { depth[n]=max(depth[n] ?? 0,(depth[id] ?? 0)+1);indegree[n,default:0]-=1;if indegree[n]==0 {queue.append(n)} }
        }
        // Cycles remain selectable rather than disappearing or causing infinite layout.
        for id in ids where depth[id]==nil { depth[id]=0 }
        var layers:[Int:[String]]=[:]
        for id in ids { layers[depth[id] ?? 0,default:[]].append(id) }
        var positions:[String:LayoutPoint]=[:], rows=1
        let dx=compact ? 172.0:220.0,dy=compact ? 70.0:96.0
        for (level,members) in layers { rows=max(rows,members.count)
            for (row,id) in members.sorted().enumerated() { positions[id]=LayoutPoint(x:24+Double(level)*dx,y:28+Double(row)*dy) }
        }
        return GraphLayout(positions:positions,width:Double((layers.keys.max() ?? 0)+1)*dx+48,height:Double(rows)*dy+56)
    }
}
