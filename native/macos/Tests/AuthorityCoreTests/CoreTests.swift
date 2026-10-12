import XCTest
@testable import AuthorityCore

final class CoreTests:XCTestCase {
    func testLanguagesCompleteAndPlaceholdersMatch(){
        let localization=Localization()
        XCTAssertGreaterThan(localization.catalog.count,200)
        let regex=try! NSRegularExpression(pattern:"\\{[A-Za-z0-9_]+\\}")
        func fields(_ s:String)->Set<String>{Set(regex.matches(in:s,range:NSRange(s.startIndex...,in:s)).compactMap{Range($0.range,in:s).map{String(s[$0])}})}
        for (key,pair) in localization.catalog {XCTAssertEqual(Set(pair.keys),["de","en"],key);XCTAssertFalse(pair["de"]!.isEmpty,key);XCTAssertFalse(pair["en"]!.isEmpty,key);XCTAssertEqual(fields(pair["de"]!),fields(pair["en"]!),key);XCTAssertFalse(pair.values.contains{$0.contains(String(UnicodeScalar(0xfffd)!))},key)}
    }
    func testLanguagePriorityAndSystemAdaptation(){
        XCTAssertEqual(Localization.resolve(explicit:"de-DE",saved:"en",environment:[:],preferred:["en"]),"de")
        XCTAssertEqual(Localization.resolve(explicit:nil,saved:"en",environment:["LANG":"de_DE"],preferred:["de"]),"en")
        XCTAssertEqual(Localization.resolve(explicit:nil,saved:"system",environment:["LC_ALL":"C","LANG":"en_US.UTF-8"],preferred:["de"]),"en")
        XCTAssertEqual(Localization.resolve(explicit:nil,saved:nil,environment:[:],preferred:["fr-FR","en-GB"]),"en")
        XCTAssertEqual(Localization.resolve(explicit:nil,saved:nil,environment:[:],preferred:["fr"]),"de")
    }
    func testDemoRemainsExplicitAndScales()throws{
        for count in [50,100,1000]{let d=DemoData.make(agents:count);try d.validate();XCTAssertTrue(d.isDemo);XCTAssertEqual(d.nodes.filter{$0.kind == .agent}.count,count);XCTAssertTrue(d.nodes.contains{$0.status == .incomplete});XCTAssertTrue(d.nodes.contains{$0.kind == .process})}
    }
    func testTraceIncludesProofAndDoesNotIncludeUnrelatedBranches(){
        let d=DemoData.make();let trace=d.trace("action-13")
        for id in ["root","identity-root","authority-root","agent-013","process-13","action-13"]{XCTAssertTrue(trace.contains(id),id)}
        XCTAssertFalse(trace.contains("action-49"));XCTAssertFalse(trace.contains("agent-049"))
    }
    func testLayoutStableAndFiniteWithCycle(){
        var d=DemoData.make(agents:1000);let first=GraphLayout.make(nodes:d.nodes,edges:d.edges)
        XCTAssertEqual(first.positions,GraphLayout.make(nodes:d.nodes.reversed(),edges:d.edges.reversed()).positions)
        d.edges.append(GraphEdge("agent-005","root","delegates",.contradictory))
        let cyclic=GraphLayout.make(nodes:d.nodes,edges:d.edges);XCTAssertEqual(cyclic.positions.count,d.nodes.count);XCTAssertTrue(cyclic.width.isFinite);XCTAssertTrue(cyclic.height.isFinite)
    }
    func testRejectsBrokenReferencesAndDuplicateIDs(){
        var d=DemoData.make();d.nodes.append(d.nodes[0]);XCTAssertThrowsError(try d.validate());d=DemoData.make();d.edges.append(GraphEdge("absent","root","delegates",.unknown));XCTAssertThrowsError(try d.validate())
    }
    func testProductMeldungenNeverBecomeIdentityOrEffects()throws{
        let report:[String:Any]=["schema_version":"agent-authority-observation-report-v1","role":"observer_only","source":["source_id":"local","entries_read":1,"complete_observed_read":true],"recent_entries":[["entry_id":"event-1","ordinal":1,"reported_kind":"result","reported_actor_type":"claimed-agent","file_sha256":String(repeating:"a",count:64)]],"tasks":[["task_alias":"A1","evidence":[["entry_id":"event-1"]]]],"display":["entries_omitted":100],"warnings":[]]
        let d=try ReportProjection.decode(JSONSerialization.data(withJSONObject:report));XCTAssertFalse(d.isDemo);XCTAssertEqual(d.omitted,100);XCTAssertTrue(d.nodes.allSatisfy{$0.status == .reported});XCTAssertFalse(d.nodes.contains{[.agent,.process,.authority,.action].contains($0.kind)});XCTAssertTrue(d.nodes[0].facts.contains{$0.labelKey=="field.identity"&&$0.value=="status.unknown"});XCTAssertTrue(d.nodes[0].facts.contains{$0.labelKey=="field.effect"&&$0.value=="status.unknown"})
    }
    func testUnknownSchemasAndOversizedInputRejected(){
        XCTAssertThrowsError(try ReportProjection.decode(Data("{}".utf8)))
        XCTAssertThrowsError(try ReportProjection.decode(Data(repeating:0,count:8*1024*1024+1)))
    }
    func testStructuralWarningsHaveInspectableReferences()throws{
        let raw:[String:Any]=["schema_version":"agent-authority-observation-report-v1","role":"observer_only","source":["source_id":"local"],"recent_entries":[["entry_id":"event-1","ordinal":1,"reported_kind":"result","reported_actor_type":"local","file_sha256":String(repeating:"a",count:64)]],"tasks":[],"summary":["structural_warning_count":3,"tasks_with_reported_association":8],"warnings":[["code":"ordinal_collision","evidence":[["entry_id":"event-1"]]]]]
        let d=try ReportProjection.decode(JSONSerialization.data(withJSONObject:raw));XCTAssertEqual(d.reportedTaskCount,8);XCTAssertEqual(d.reportedWarningCount,3);XCTAssertTrue(d.nodes.contains{$0.kind == .evidence&&$0.status == .incomplete});XCTAssertTrue(d.edges.contains{$0.from=="warning-0"&&$0.to=="event-1"})
    }
    func testCompactAgentOverviewPreservesAllNodesAndEdges(){
        let d=DemoData.make(agents:50),nodes=d.nodes.filter{[.agent,.authority,.identity].contains($0.kind)}
        let layout=GraphLayout.agents(nodes);XCTAssertEqual(layout.positions.count,nodes.count);XCTAssertLessThan(layout.width,1000);XCTAssertLessThan(layout.height,800)
        let ids=Set(nodes.map(\.id));XCTAssertEqual(d.edges.filter{$0.relation=="delegates"&&ids.contains($0.from)&&ids.contains($0.to)}.count,49)
    }
    func testVerifiedLocalIdentityDoesNotRepairMissingParentAuthority(){
        let d=DemoData.make();XCTAssertEqual(d.nodes.first{$0.id=="agent-027"}?.status,.verified)
        XCTAssertEqual(d.chainStatuses()["agent-027"],.incomplete);XCTAssertEqual(d.chainStatuses()["action-27"],.incomplete)
        XCTAssertEqual(d.chainStatuses()["agent-035"],.unknown)
    }
    func testKernelEventsNeverAuthenticateLogicalAgent(){
        let record:[String:Any]=["events":[["event":"write","pid":123,"pid_version":2,"boot_sec":50,"dev":1,"inode":5,"version":4,"global_sequence":9]],"sequence_available":false,"sequence_gaps":2,"buffer_dropped":1]
        let d=NativeProjection.make(record);XCTAssertFalse(d.isDemo);XCTAssertEqual(d.nodes.count,2);XCTAssertTrue(d.nodes.allSatisfy{$0.status == .observed});XCTAssertFalse(d.nodes.contains{$0.kind == .agent});XCTAssertEqual(Set(d.warnings),["sequence_unavailable","sequence_gaps","buffer_dropped"])
        XCTAssertTrue(d.nodes[0].facts.contains{$0.labelKey=="field.authority"&&$0.value=="status.unknown"})
        XCTAssertTrue(d.nodes[1].facts.contains{$0.labelKey=="field.loss"&&$0.value=="status.unknown"&&$0.valueKey})
    }
}
