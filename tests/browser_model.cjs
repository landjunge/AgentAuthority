/* Targeted checks for the native-to-browser graph port. No npm packages.
 * Run: node tests/browser_model.cjs [--python /path/to/python3]
 * Python is invoked directly with fixed arguments, never through a shell. */
"use strict";
const assert = require("node:assert/strict");
const {execFileSync} = require("node:child_process");
const {resolve} = require("node:path");
const {readFileSync} = require("node:fs");
const model = require("../agent_authority/browser_static/app.js");
const project = resolve(__dirname, "..");
const args = process.argv.slice(2);
if (args.length && !(args.length === 2 && args[0] === "--python")) throw new Error("Usage: node tests/browser_model.cjs [--python /path/to/python3]");
const python = args[1] || "python3";
const payload = JSON.parse(execFileSync(python, ["-B", "-c", [
  "import json",
  "from agent_authority.browser_model import demo_graph, trace, chain_statuses",
  "g = demo_graph()",
  "print(json.dumps({'graph': g, 'trace': sorted(trace(g, 'action-13')), 'statuses': chain_statuses(g)}))"
].join("\n")], {cwd: project, encoding: "utf8", timeout: 10000, maxBuffer: 2 * 1024 * 1024}));
const d = payload.graph;
let checks = 0;
function check(name, fn) { fn(); checks++; process.stdout.write("PASS " + name + "\n"); }
check("trace agrees with native-derived Python projection", () => assert.deepEqual([...model.trace(d, "action-13")].sort(), payload.trace));
check("all chain statuses agree with Python projection", () => assert.deepEqual(Object.fromEntries(model.chainStatuses(d)), payload.statuses));
check("verified local identity preserves incomplete parent", () => assert.equal(model.chainStatuses(d).get("agent-027"), "incomplete"));
check("trace excludes unrelated agent branch", () => assert.equal(model.trace(d, "action-13").has("action-49"), false));
const layout = model.graphLayout(d.nodes, d.edges), reversed = model.graphLayout([...d.nodes].reverse(), [...d.edges].reverse());
check("layout is stable under input reordering", () => assert.deepEqual([...layout.positions].sort(), [...reversed.positions].sort()));
const cyclic = {...d, edges: [...d.edges, {from: "agent-005", to: "root", relation: "delegates", status: "contradictory", evidence: []}]};
check("cycle retains every selectable node", () => assert.equal(model.graphLayout(cyclic.nodes, cyclic.edges).positions.size, d.nodes.length));
check("cyclic chain is contradictory", () => assert.equal(model.chainStatuses(cyclic).get("root"), "contradictory"));
const groups = model.clustered(d, new Set());
check("50-agent demo forms five branches", () => assert.equal(groups.nodes.filter(n => n.kind === "cluster").length, 5));
check("groups preserve external relationships", () => assert(groups.edges.some(e => e.from === "root" && e.to.startsWith("cluster:"))));
check("aggregation removes group self-edges", () => assert(groups.edges.every(e => e.from !== e.to)));
const expanded = model.clustered(d, new Set(["branch-0"]));
check("expanded group exposes original agent", () => assert(expanded.nodes.some(n => n.id === "agent-001")));
check("expanded group removes its aggregate node", () => assert.equal(expanded.nodes.some(n => n.id === "cluster:branch-0"), false));
const state = {mode: 1, filter: 1, query: "", expandedGroups: new Set(), chainAnchor: "root", selection: "root"};
check("missing-proof filter uses inherited status", () => assert(model.visibleGraph(d, state).nodes.some(n => n.id === "agent-027")));
state.filter = 2;
check("proved filter excludes incomplete parent chain", () => assert.equal(model.visibleGraph(d, state).nodes.some(n => n.id === "agent-027"), false));
check("critical warning does not change proof filter", () => assert(model.visibleGraph(d, state).nodes.some(n => n.id === "agent-003")));
check("explicit critical demo case", () => assert.equal(model.warningAssessment(d, "agent-003").outcome, "critical"));
check("missing required data is not assessable", () => assert.equal(model.warningAssessment(d, "agent-004").outcome, "notAssessable"));
check("clear exists only after explicit synthetic check", () => assert.equal(model.warningAssessment(d, "agent-005").outcome, "checkedClear"));
const real = {...d, isDemo: false};
check("real source has unknown logical chain quality", () => assert([...model.chainStatuses(real).values()].every(value => value === "unknown")));
check("real data never inherits synthetic warning", () => assert.equal(model.warningAssessment(real, "agent-003").outcome, "notAssessable"));
check("real warning severity remains unknown", () => assert.equal(model.warningAssessment(real, "agent-003").severity, null));
check("empty source stays empty", () => assert.equal(model.visibleGraph({...real, nodes: [], edges: []}, {...state, mode: 0}).nodes.length, 0));
check("search includes evidence references", () => assert.deepEqual(model.visibleGraph(d, {...state, filter: 0, query: "E-13-ID"}).nodes.map(n => n.id), ["agent-013"]));
check("native agent and delegation page mapping", () => { assert.equal(model.rowsForPage(d, "agents").length, 51); assert.equal(model.rowsForPage(d, "delegations").length, 49); });
check("neutral raw text and export preserve ordinals above JS safe integer", () => {
  const exact = '{"schema_version":"agent-authority-observation-report-v1","recent_entries":[{"ordinal":9007199254740993}]}';
  const roundedObject = JSON.parse(exact);
  assert.equal(roundedObject.recent_entries[0].ordinal, 9007199254740992);
  assert.equal(model.reportText({reportJSON: exact}, roundedObject, null), exact);
});
check("private raw text and export retain the separate contract schema", () => {
  const privateReport = {schema: "aa-report-v1", issuedAtMs: 9007199254740991, classification: "UNBEKANNT"};
  assert.deepEqual(JSON.parse(model.reportText({reportJSON: '{"schema_version":"agent-authority-observation-report-v1"}'}, null, privateReport)), privateReport);
});

const history = new model.NavigationHistory(100);
function snapshot(index) { return {page: "graph", mode: index % 3, chainAnchor: "agent-" + index, selection: "selected-" + index, filter: index % 3, query: "Änderung " + index, expandedGroups: ["branch-0", "branch-2"], zoom: 0.731234567 + index / 1000, panX: -203.125 + index, panY: 77.875 - index, raw: Boolean(index % 2), rowPage: 0}; }
history.reset(snapshot(0));
check("viewport save alone does not add back entry", () => { history.save({...snapshot(0), zoom: 2, panX: -999}); assert.equal(history.canGoBack, false); assert.equal(history.entries.length, 1); });
for (let i = 1; i <= 120; i++) history.record(snapshot(i));
check("history bounds retained snapshots and preserves browser indices", () => { assert.equal(history.entries.length, 100); assert.equal(history.index, 120); assert.equal(history.base, 21); assert.deepEqual(history.at(119), snapshot(119)); });
check("back restores every field without adding an entry", () => { assert.deepEqual(history.back(), snapshot(119)); assert.equal(history.index, 119); assert.equal(history.entries.length, 100); });
check("forward entry remains addressable", () => assert.deepEqual(history.restore(120), snapshot(120)));
check("restored group arrays cannot mutate stored snapshots", () => { const saved = history.at(119); saved.expandedGroups.push("mutated"); assert.deepEqual(history.at(119).expandedGroups, ["branch-0", "branch-2"]); });
check("new navigation after back discards forward snapshots", () => { history.restore(118); history.record(snapshot(999)); assert.deepEqual(history.at(119), snapshot(999)); assert.equal(history.at(120), null); });
check("source reset invalidates old navigation", () => { history.reset(snapshot(0)); assert.equal(history.canGoBack, false); assert.equal(history.at(119), null); assert.equal(history.back(), null); });

const catalog = JSON.parse(readFileSync(resolve(project, "agent_authority/browser_static/strings.json"), "utf8"));
check("DE/EN catalog keys and replacement fields match", () => {
  for (const [key, pair] of Object.entries(catalog)) {
    assert.deepEqual(Object.keys(pair).sort(), ["de", "en"], key); assert(pair.de && pair.en, key);
    assert.deepEqual([...new Set(pair.de.match(/\{\w+\}/g) || [])].sort(), [...new Set(pair.en.match(/\{\w+\}/g) || [])].sort(), key);
  }
});
process.stdout.write(`PASS ${checks} targeted browser-model checks\n`);
