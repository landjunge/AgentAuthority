import Foundation
import XCTest
@testable import AuthorityCore

final class WorkflowProjectionTests:XCTestCase {
    func wrapper(binding:[String:Any]=[:])->[String:Any] {
        ["schema_version":"agent-authority-workflow-report-v1","role":"observer_only",
         "source_authenticated":true,"identity":"VERIFIED",
         "observation_report":["schema_version":"agent-authority-observation-report-v1","role":"observer_only",
           "source":["source_id":"test-source","complete_observed_read":false],
           "recent_entries":[["entry_id":"wf-event","ordinal":1,"reported_kind":"result","reported_actor_type":"claimed-model","file_sha256":String(repeating:"a",count:64)]],
           "tasks":[],"warnings":[]],
         "events":[["entry_id":"wf-event","binding":binding]],
         "warnings":[["code":"workflow_sequence_gap","entry_id":"wf-event"]]]
    }
    func testWorkflowWrapperPreservesUnknownIdentityAndSeparateIDs()throws {
        let raw=wrapper(binding:["original_task_id":"thread:task","bridge_task_id":"kb-task-1","run_id":"run-1","handoff_revision":1,"source_revision":7,"token":"PRIVATE_TOKEN"])
        let d=try ReportProjection.decode(JSONSerialization.data(withJSONObject:raw))
        XCTAssertFalse(d.isDemo);XCTAssertEqual(d.completeRead,false)
        let entry=try XCTUnwrap(d.nodes.first{$0.id=="wf-event"})
        XCTAssertEqual(entry.status,.reported)
        XCTAssertTrue(entry.facts.contains{$0.labelKey=="workflow.original_task_id"&&$0.value=="thread:task"})
        XCTAssertTrue(entry.facts.contains{$0.labelKey=="workflow.bridge_task_id"&&$0.value=="kb-task-1"})
        XCTAssertFalse(entry.facts.contains{$0.value=="PRIVATE_TOKEN"})
        XCTAssertNil(d.reportJSON)
        XCTAssertTrue(d.isReportSource)
        XCTAssertFalse(String(data:try JSONEncoder().encode(d),encoding:.utf8)!.contains("PRIVATE_TOKEN"))
        XCTAssertTrue(entry.facts.contains{$0.labelKey=="field.identity"&&$0.value=="status.unknown"})
        XCTAssertTrue(d.warnings.contains("workflow_sequence_gap"))
        XCTAssertFalse(d.nodes.contains{$0.kind == .authority})
    }
    func testManyBindingsPreserveImportantSeparateRevisionsWithinGraphLimit()throws {
        let keys=["project_id","workflow_id","thread_id","handoff_id","handoff_revision","source_revision","source_ref","source_hash","request_hash","task_id","original_task_id","bridge_task_id","run_id","attempt_id","parent_task_id","subtask_id","return_id","recipient_id","session_id","principal_ref","operator_scope","actor_claim","task_revision","artifact_ref","dispatch_seq","barrier_seq","reserved_microusd","spent_microusd","available_microusd","cost_kind","stop_state","reported_status"]
        var binding:[String:Any]=Dictionary(uniqueKeysWithValues:keys.map{($0,"reference")})
        binding["handoff_revision"]=1;binding["source_revision"]=7
        let d=try ReportProjection.decode(JSONSerialization.data(withJSONObject:wrapper(binding:binding)))
        XCTAssertLessThanOrEqual(d.nodes[0].facts.count,32)
        XCTAssertTrue(d.nodes[0].facts.contains{$0.labelKey=="workflow.source_revision"&&$0.value=="7"})
        XCTAssertTrue(d.nodes[0].facts.contains{$0.labelKey=="workflow.handoff_revision"&&$0.value=="1"})
        XCTAssertTrue(d.nodes[0].facts.contains{$0.labelKey=="workflow.omitted_fields"})
    }
    func testWrapperLimitsFactsAndNeverTreatsBoolAsRevision()throws {
        let raw=wrapper(binding:["handoff_revision":true,"source_revision":7,"task_revision":1.5,"project_id":"project-1"])
        let d=try ReportProjection.decode(JSONSerialization.data(withJSONObject:raw))
        XCTAssertFalse(d.nodes[0].facts.contains{$0.labelKey=="workflow.handoff_revision"})
        XCTAssertFalse(d.nodes[0].facts.contains{$0.labelKey=="workflow.task_revision"})
        var nested=wrapper();nested["observation_report"]=wrapper()
        XCTAssertThrowsError(try ReportProjection.decode(JSONSerialization.data(withJSONObject:nested)))
        var large=wrapper();large["events"]=Array(repeating:["entry_id":"wf-event","binding":[:]],count:101)
        XCTAssertThrowsError(try ReportProjection.decode(JSONSerialization.data(withJSONObject:large)))
    }
}
