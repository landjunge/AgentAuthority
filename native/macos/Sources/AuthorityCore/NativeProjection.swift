import Foundation

public enum NativeProjection {
    /// Projection of minimized events received from the signed native ES collector.
    /// Observed process attribution never manufactures a logical agent identity.
    public static func make(_ record:[String:Any])->GraphDocument {
        var doc=GraphDocument(source:"macOS-ES-test")
        let events=record["events"] as? [[String:Any]] ?? []
        var instances:Set<String>=[]
        for (index,event) in events.enumerated() where event["event"] as? String == "write" {
            guard let pid=event["pid"] as? Int,let version=event["pid_version"] as? Int,let boot=event["boot_sec"] as? Int else{continue}
            let instance="p-\(boot)-\(pid)-\(version)",id="event-\(index)"
            if instances.insert(instance).inserted {
                doc.nodes.append(GraphNode(id:instance,kind:.process,name:"PID \(pid)",status:.observed,
                    facts:[Fact("field.pid",String(pid)),Fact("field.instance",instance),Fact("field.start","\(event["start_sec"] ?? "?").\(event["start_usec"] ?? "?")"),Fact("field.uid","\(event["uid"] ?? "?")"),Fact("field.signing",event["signing_id"] as? String ?? ""),Fact("field.identity","status.unknown",localized:true),Fact("field.authority","status.unknown",localized:true)],evidence:[id]))
            }
            doc.nodes.append(GraphNode(id:id,kind:.action,name:"demo.write",localized:true,status:.observed,
                facts:[Fact("field.object","\(event["dev"] ?? "?"):\(event["inode"] ?? "?")"),Fact("field.version","\(event["version"] ?? "?")"),Fact("field.sequence","\(event["global_sequence"] ?? "?")"),Fact("field.loss",record["sequence_available"] as? Bool == true ? "\(record["sequence_gaps"] ?? "?")":"status.unknown",localized:record["sequence_available"] as? Bool != true),Fact("field.effect","boundary.durable",localized:true)],evidence:[id]))
            doc.edges.append(GraphEdge(instance,id,"eventProcess",.observed,evidence:[id]))
        }
        if record["sequence_available"] as? Bool != true{doc.warnings.append("sequence_unavailable")}
        if record["sequence_gaps"] as? Int ?? 0 > 0{doc.warnings.append("sequence_gaps")}
        if record["buffer_dropped"] as? Int ?? 0 > 0{doc.warnings.append("buffer_dropped")}
        doc.completeRead=nil
        return doc
    }
}
