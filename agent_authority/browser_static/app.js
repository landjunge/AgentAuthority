/* Native AuthorityCore graph semantics, ported without a graph/runtime dependency.
 * The exported pure functions are also used by targeted model checks. */
(function (global) {
  "use strict";
  const STATUS_RANK = {verified: 0, observed: 0, reported: 1, unknown: 2, incomplete: 3, contradictory: 4};
  const DEMO_IDS = ["root", "agent-001", "agent-002", "agent-003", "agent-004", "agent-005"];
  const SEVERITIES = ["information", "attention", "warning", "critical"];
  function trace(document, anchor) {
    const result = new Set([anchor]), parents = new Map(), children = new Map();
    const kinds = new Map(document.nodes.map(n => [n.id, n.kind]));
    for (const e of document.edges) {
      if (!parents.has(e.to)) parents.set(e.to, []);
      if (!children.has(e.from)) children.set(e.from, []);
      parents.get(e.to).push(e.from); children.get(e.from).push(e.to);
    }
    let queue = [anchor];
    for (let i = 0; i < queue.length; i++) for (const id of parents.get(queue[i]) || []) {
      if (!result.has(id)) { result.add(id); queue.push(id); }
    }
    queue = [anchor];
    for (let i = 0; i < queue.length; i++) for (const id of children.get(queue[i]) || []) {
      if (!result.has(id) && kinds.get(id) !== "agent") { result.add(id); queue.push(id); }
    }
    return result;
  }
  function chainStatuses(document) {
    const result = new Map(document.nodes.map(n => [n.id, document.isDemo ? (n.status === "observed" ? "verified" : n.status) : "unknown"]));
    if (!document.isDemo) return result;
    const incoming = new Map(document.nodes.map(n => [n.id, 0])), outgoing = new Map(), visited = new Set();
    const worse = (a, b) => (STATUS_RANK[a] ?? 4) >= (STATUS_RANK[b] ?? 4) ? a : b;
    for (const e of document.edges) {
      incoming.set(e.to, (incoming.get(e.to) || 0) + 1);
      if (!outgoing.has(e.from)) outgoing.set(e.from, []);
      outgoing.get(e.from).push(e);
    }
    const queue = document.nodes.filter(n => incoming.get(n.id) === 0).map(n => n.id);
    for (let i = 0; i < queue.length; i++) {
      const id = queue[i]; visited.add(id);
      for (const e of outgoing.get(id) || []) {
        result.set(e.to, worse(worse(result.get(e.to) || "unknown", result.get(id) || "unknown"), e.status === "observed" ? "verified" : e.status));
        incoming.set(e.to, incoming.get(e.to) - 1);
        if (incoming.get(e.to) === 0) queue.push(e.to);
      }
    }
    for (const n of document.nodes) if (!visited.has(n.id)) result.set(n.id, "contradictory");
    return result;
  }
  function graphLayout(nodes, edges, agentOverview = false, columns = 5) {
    const positions = new Map();
    if (agentOverview) {
      columns = Math.max(3, columns);
      const agents = nodes.filter(n => n.kind === "agent" && n.group !== "root").sort((a, b) => a.id.localeCompare(b.id, "en"));
      agents.forEach((n, i) => positions.set(n.id, {x: 24 + (i % columns) * 158, y: 120 + Math.floor(i / columns) * 60}));
      nodes.filter(n => n.group === "root").sort((a, b) => a.id.localeCompare(b.id, "en")).forEach((n, i) => positions.set(n.id, {x: 24 + i * 158, y: 24}));
      return {positions, width: columns * 158 + 48, height: Math.ceil(agents.length / columns) * 60 + 150};
    }
    const ids = new Set(nodes.map(n => n.id)), incoming = new Map([...ids].map(id => [id, 0])), outgoing = new Map(), depth = new Map();
    for (const e of edges) if (ids.has(e.from) && ids.has(e.to)) {
      if (!outgoing.has(e.from)) outgoing.set(e.from, []);
      outgoing.get(e.from).push(e.to); incoming.set(e.to, incoming.get(e.to) + 1);
    }
    const queue = [...ids].filter(id => incoming.get(id) === 0).sort();
    queue.forEach(id => depth.set(id, 0));
    for (let i = 0; i < queue.length; i++) for (const next of (outgoing.get(queue[i]) || []).slice().sort()) {
      depth.set(next, Math.max(depth.get(next) || 0, depth.get(queue[i]) + 1));
      incoming.set(next, incoming.get(next) - 1);
      if (incoming.get(next) === 0) queue.push(next);
    }
    const layers = new Map();
    for (const id of ids) {
      const level = depth.get(id) || 0;
      if (!layers.has(level)) layers.set(level, []);
      layers.get(level).push(id);
    }
    let rows = 1;
    for (const [level, members] of layers) {
      rows = Math.max(rows, members.length);
      members.sort().forEach((id, row) => positions.set(id, {x: 24 + level * 172, y: 28 + row * 70}));
    }
    return {positions, width: (Math.max(0, ...layers.keys()) + 1) * 172 + 48, height: rows * 70 + 56};
  }
  function clustered(document, expandedGroups, translate = (key, values) => `${values.count} agents`) {
    const statuses = chainStatuses(document), groups = new Map(), mapping = new Map();
    const nodes = document.nodes.filter(n => n.group === "root" || (expandedGroups.has(n.group) && n.kind === "agent"));
    for (const n of document.nodes.filter(n => n.kind === "agent" && n.group !== "root")) {
      if (!groups.has(n.group)) groups.set(n.group, []);
      groups.get(n.group).push(n);
    }
    for (const [group, members] of groups) {
      if (expandedGroups.has(group)) { members.forEach(n => mapping.set(n.id, n.id)); continue; }
      const id = "cluster:" + group, missing = members.filter(n => statuses.get(n.id) !== "verified").length;
      members.forEach(n => mapping.set(n.id, id));
      nodes.push({id, kind: "cluster", name: translate("graph.clusterCount", {count: members.length}), nameKey: false, status: missing ? "incomplete" : "verified", group,
        facts: [{labelKey: "metric.agents", value: String(members.length)}, {labelKey: "metric.chains", value: String(missing)}], evidence: []});
    }
    const ids = new Set(nodes.map(n => n.id)), edges = [], pairs = new Map();
    for (const e of document.edges) {
      const from = mapping.get(e.from) || e.from, to = mapping.get(e.to) || e.to;
      if (from === to || !ids.has(from) || !ids.has(to)) continue;
      const pair = JSON.stringify([from, to]);
      if (!pairs.has(pair)) { pairs.set(pair, edges.length); edges.push({...e, from, to, evidence: [...(e.evidence || [])]}); }
      else { const current = edges[pairs.get(pair)]; current.evidence.push(...(e.evidence || [])); if (e.status !== "verified") current.status = e.status; }
    }
    nodes.sort((a, b) => a.id < b.id ? -1 : a.id > b.id ? 1 : 0);
    return {nodes, edges};
  }
  function warningAssessment(document, id) {
    const index = document.isDemo ? DEMO_IDS.indexOf(id) : -1;
    if (index < 0) return {outcome: "notAssessable", severity: null, isSynthetic: false, checkPerformed: false, dataState: "notEvaluated", reasonKey: "warning.uncheckedReason", sourceKey: "warning.noCheck", timestamp: null, relationship: null, evidence: []};
    return {outcome: index === 4 ? "notAssessable" : index === 5 ? "checkedClear" : SEVERITIES[index], severity: SEVERITIES[index] || null,
      isSynthetic: true, checkPerformed: index !== 4, dataState: index === 4 ? "missing" : "current", reasonKey: "warning.demoReason." + index,
      sourceKey: "warning.syntheticSource", timestamp: "2026-10-12T12:00:00Z", relationship: index === 2 ? "root → agent-002" : null, evidence: index === 2 ? ["UI-DEMO-002"] : []};
  }
  function visibleGraph(document, state, translate = (key, values) => `${values.count} agents`, nodeTitle = n => n.name) {
    let nodes = [...document.nodes], edges = [...document.edges];
    if (state.mode === 0 && nodes.length) {
      const anchor = nodes.some(n => n.id === state.chainAnchor) ? state.chainAnchor : state.selection;
      const ids = trace(document, anchor); nodes = nodes.filter(n => ids.has(n.id)); edges = edges.filter(e => ids.has(e.from) && ids.has(e.to));
    } else if (document.isDemo && state.mode === 1) {
      if (nodes.filter(n => n.kind === "agent").length > 80) ({nodes, edges} = clustered(document, state.expandedGroups, translate));
      else nodes = nodes.filter(n => ["agent", "identity", "authority"].includes(n.kind));
    } else if (document.isDemo && state.mode === 2) ({nodes, edges} = clustered(document, state.expandedGroups, translate));
    if (state.filter) {
      const statuses = chainStatuses(document);
      nodes = nodes.filter(n => {
        const status = n.kind === "agent" ? statuses.get(n.id) || n.status : n.status;
        return state.filter === 1 ? ["unknown", "incomplete", "contradictory", "reported"].includes(status) : ["observed", "verified"].includes(status);
      });
    }
    const query = state.query.trim().toLocaleLowerCase();
    if (query) nodes = nodes.filter(n => [nodeTitle(n), n.id, ...(n.facts || []).map(f => f.value), ...(n.evidence || [])].join(" ").toLocaleLowerCase().includes(query));
    const ids = new Set(nodes.map(n => n.id)); edges = edges.filter(e => ids.has(e.from) && ids.has(e.to));
    return {nodes, edges, agentOverview: document.isDemo && state.mode === 1 && !nodes.some(n => n.kind === "cluster")};
  }
  function rowsForPage(document, page) {
    const delegated = new Set(document.edges.filter(e => e.relation === "delegates").map(e => e.to));
    return document.nodes.filter(n => page === "agents" ? ["agent", "identity"].includes(n.kind) : page === "delegations" ? delegated.has(n.id) : page === "evidence" ? (n.evidence || []).length > 0 : page === "findings" ? ["incomplete", "unknown", "contradictory"].includes(n.status) : ["action", "entry", "process"].includes(n.kind));
  }
  function reportText(graph, report, privateReport) {
    if (privateReport) return JSON.stringify(privateReport, null, 2);
    if (typeof graph?.reportJSON === "string") return graph.reportJSON;
    if (report) return JSON.stringify(report, null, 2);
    return graph?.isDemo ? JSON.stringify(graph, null, 2) : null;
  }
  function helpCenterContextGraph(context) {
    // Source relationships only. Help Center account IDs are never interpreted
    // as verified agents, delegated authority or a shared authenticated subject.
    if (context?.schema !== "hilfezentrum.authority-context.v1" || context.case?.synthetic !== true || context.handoff?.data_transferred !== false) throw new Error("invalid_synthetic_context");
    const fact = (labelKey, value, valueKey = false) => ({labelKey, value: String(value), valueKey});
    const node = (id, kind, name, status, facts) => ({id, kind, name, nameKey: true, status, group: "", facts, evidence: []});
    const owner = "account:" + context.owner_account_id, participant = "account:" + context.participant_account_id;
    const listing = "listing:" + context.listing.id, assignment = "assignment:" + context.assignment.id, caseId = "case:" + context.case.key;
    const nodes = [
      node(owner, "identity", "hilfezentrum.owner", "unknown", [fact("field.identity", context.owner_account_id), fact("field.basis", "hilfezentrum.accountBoundary", true)]),
      node(participant, "identity", "hilfezentrum.participant", "unknown", [fact("field.identity", context.participant_account_id), fact("field.basis", "hilfezentrum.accountBoundary", true)]),
      node(listing, "task", "hilfezentrum.listing", "reported", [fact("web.reference", context.listing.id), fact("hilfezentrum.state", context.listing.lifecycle.state), fact("field.version", context.listing.lifecycle.revision)]),
      node(assignment, "entry", "hilfezentrum.assignment", "reported", [fact("web.reference", context.assignment.id), fact("hilfezentrum.state", context.assignment.state), fact("field.version", context.assignment.revision), fact("field.start", context.assignment.created_at), fact("hilfezentrum.changed", context.assignment.changed_at)]),
      node(caseId, "entry", "hilfezentrum.case", "reported", [fact("web.reference", context.case.key), fact("hilfezentrum.state", context.case.state), fact("field.version", context.case.revision), fact("field.start", context.case.tracked_since)])
    ];
    const edge = (from, to, relation) => ({from, to, relation, status: "reported", evidence: []});
    return {schema: "agent-authority-ui-graph-v1", source: "hilfezentrum-synthetic", isDemo: false, nodes: [nodes[3], nodes[0], nodes[1], nodes[2], nodes[4]], edges: [
      edge(owner, listing, "context-owner"), edge(listing, assignment, "context-assignment"), edge(participant, assignment, "context-participant"), edge(assignment, caseId, "context-case")
    ], omitted: 0, warnings: [], reportJSON: JSON.stringify(context, null, 2)};
  }
  class NavigationHistory {
    constructor(limit = 100) { this.limit = limit; this.entries = []; this.base = 0; this.index = 0; }
    copy(value) { return value ? {...value, expandedGroups: [...(value.expandedGroups || [])]} : null; }
    reset(value) { this.entries = value ? [this.copy(value)] : []; this.base = 0; this.index = 0; }
    get canGoBack() { return this.index > this.base; }
    at(index) { return this.copy(this.entries[index - this.base]); }
    save(value) { if (this.entries.length) this.entries[this.index - this.base] = this.copy(value); }
    record(value) {
      this.entries.splice(this.index - this.base + 1); this.entries.push(this.copy(value)); this.index++;
      if (this.entries.length > this.limit) { this.entries.shift(); this.base++; }
    }
    restore(index) { const value = this.at(index); if (value) this.index = index; return value; }
    back() { return this.canGoBack ? this.restore(this.index - 1) : null; }
  }
  const model = {trace, chainStatuses, graphLayout, clustered, warningAssessment, visibleGraph, rowsForPage, reportText, helpCenterContextGraph, NavigationHistory};
  if (typeof module === "object" && module.exports) module.exports = model;
  global.AuthorityBrowserModel = model;
  if (typeof document === "undefined") return;

  const $ = id => document.getElementById(id);
  const appBase = new URL("./", window.location.href);
  const helpCenterDemoLanguage = /^#hilfezentrum-demo-(de|en)$/.exec(window.location.hash)?.[1];
  let helpCenterDemoPending = Boolean(helpCenterDemoLanguage);
  const SVG_NS = "http://www.w3.org/2000/svg";
  const EMPTY_GRAPH = () => ({schema: "agent-authority-ui-graph-v1", source: "", isDemo: false, nodes: [], edges: [], warnings: [], omitted: 0});
  const state = {page: "overview", mode: 0, chainAnchor: "", selection: "", filter: 0, query: "", expandedGroups: new Set(), zoom: 1, panX: 0, panY: 0,
    graph: EMPTY_GRAPH(), report: null, privateReport: null, metadata: {}, reportId: "", reports: [], session: null, status: null, raw: false, rowPage: 0, busy: 0, importing: false, inspectorOpen: true};
  let catalog = {}, preference = "system", language = "de", graph = {nodes: [], edges: []}, layout = graphLayout([], []), navigationEpoch = "", loadGeneration = 0;
  let currentMessage = {key: "", variant: "", values: {}};
  const navigation = new NavigationHistory(100);
  const svgElements = new Map(), edgeElements = [], graphStatuses = new Map();
  function readPreference(key, fallback) { try { return localStorage.getItem("agent-authority." + key) || fallback; } catch (_) { return fallback; } }
  function savePreference(key, value) { try { localStorage.setItem("agent-authority." + key, value); } catch (_) { /* Private storage may be disabled. */ } }
  function resolveLanguage(value) {
    if (["de", "en"].includes(value)) return value;
    for (const lang of navigator.languages || [navigator.language]) { const base = String(lang).toLowerCase().split(/[-_]/)[0]; if (["de", "en"].includes(base)) return base; }
    return "de";
  }
  function L(key, values = {}) {
    let value = catalog[key]?.[language] || catalog[key]?.de || key;
    for (const [name, replacement] of Object.entries(values)) value = value.split("{" + name + "}").join(String(replacement));
    return value;
  }
  function nodeTitle(node) { return node.nameKey ? L(node.name) : String(node.name); }
  function factText(fact) { return fact.valueKey ? L(fact.value) : String(fact.value); }
  function element(tag, className, content) {
    const el = document.createElement(tag); if (className) el.className = className; if (content !== undefined) el.textContent = String(content); return el;
  }
  function svgElement(tag, attributes = {}, content) {
    const el = document.createElementNS(SVG_NS, tag); for (const [key, value] of Object.entries(attributes)) el.setAttribute(key, String(value)); if (content !== undefined) el.textContent = String(content); return el;
  }
  function button(text, callback, className) { const el = element("button", className, text); el.type = "button"; el.addEventListener("click", callback); return el; }
  function translateStatic() {
    document.documentElement.lang = language;
    for (const el of document.querySelectorAll("[data-i18n]")) el.textContent = L(el.dataset.i18n);
    for (const el of document.querySelectorAll("[data-i18n-placeholder]")) el.placeholder = L(el.dataset.i18nPlaceholder);
    for (const el of document.querySelectorAll("[data-i18n-title]")) { el.title = L(el.dataset.i18nTitle); el.setAttribute("aria-label", L(el.dataset.i18nTitle)); }
    for (const el of document.querySelectorAll("[data-i18n-label]")) el.setAttribute("aria-label", L(el.dataset.i18nLabel));
    $("language").value = preference; $("login-language").value = language;
    $("modes").setAttribute("aria-label", L("web.graphView")); $("graph-area").setAttribute("aria-label", L("graph.title"));
    $("report-controls").setAttribute("aria-label", L("web.report"));
    for (const link of document.querySelectorAll(".help-center-return")) link.href = "https://ki-hilfezentrum.netzwerkpunkt.de/" + (language === "en" ? "en.html" : "") + "#agent-authority";
  }
  function renderAccountLabel() { $("account-label").textContent = state.session ? `${L(state.session.user?.synthetic ? "web.syntheticAccount" : "web.account")} · ${state.session.user?.id || ""}` : ""; }
  function chooseLanguage(value) { preference = value; language = resolveLanguage(value); savePreference("language", value); translateStatic(); renderReports(); renderScopes(); render(); renderAccountLabel(); message(currentMessage.key, currentMessage.variant, currentMessage.values); }
  function message(key, variant = "", values = {}) { currentMessage = {key, variant, values}; const target = $("global-message"); target.className = "message " + variant; target.textContent = L(key, values); target.hidden = !key; if (key) $("announcer").textContent = target.textContent; }
  class APIError extends Error { constructor(status, code) { super(code || "request_failed"); this.status = status; this.code = code; } }
  async function api(path, options = {}) {
    const headers = new Headers(options.headers || {}); headers.set("Accept", "application/json");
    if (options.body !== undefined && !(options.body instanceof Blob)) { headers.set("Content-Type", "application/json"); options.body = JSON.stringify(options.body); }
    if (options.method && options.method !== "GET" && path !== "/api/login" && state.session?.csrfToken) headers.set("X-CSRF-Token", state.session.csrfToken);
    const response = await fetch(new URL(path.replace(/^\//, ""), appBase), {...options, headers, credentials: "same-origin", cache: "no-store"});
    let payload = {}; try { payload = await response.json(); } catch (_) { /* Non-JSON proxy errors are not rendered as HTML. */ }
    if (!response.ok) { if (response.status === 401 && path !== "/api/login") showLogin(); throw new APIError(response.status, typeof payload.error === "string" ? payload.error : payload.error?.code || payload.code); }
    return payload;
  }
  function errorKey(error) {
    if (error.status === 404 && error.code === "NOT_FOUND") return "web.contextNotAvailable";
    if (error.status === 401) return "web.sessionExpired";
    if (error.status === 403) return "web.accessDenied";
    if (error.status === 413) return "web.tooLarge";
    if (error.status === 429) return "web.rateLimited";
    if ([400, 409, 422].includes(error.status)) return "source.invalid";
    return "web.requestFailed";
  }
  function setBusy(delta) { state.busy = Math.max(0, state.busy + delta); document.body.classList.toggle("busy", state.busy > 0); $("main").setAttribute("aria-busy", String(state.busy > 0)); }
  function showLogin() {
    loadGeneration++;
    state.session = null; state.reports = []; state.graph = EMPTY_GRAPH(); state.report = null; state.privateReport = null; state.reportId = ""; state.metadata = {}; state.status = null;
    $("application").hidden = true; $("login-screen").hidden = false; $("activity-rows").replaceChildren(); $("inspector-content").replaceChildren(); $("graph-nodes").replaceChildren(); $("graph-edges").replaceChildren();
    $("report-select").replaceChildren(); $("import-file").value = ""; $("scope-list").replaceChildren();
    if ($("import-dialog").open) $("import-dialog").close();
    navigation.reset(null); navigationEpoch = "";
    currentMessage = {key: "", variant: "", values: {}};
    graph = {nodes: [], edges: []}; layout = graphLayout([], []); svgElements.clear(); edgeElements.length = 0; graphStatuses.clear();
    $("scope-description").textContent = ""; $("scope-job").textContent = ""; $("account-label").textContent = ""; $("service-details").replaceChildren(); $("metrics").replaceChildren(); $("source-boundary").textContent = ""; $("global-message").hidden = true;
  }
  async function enterSession(session) {
    state.session = session; $("login-message").hidden = true; $("password").value = "";
    $("login-screen").hidden = true; $("application").hidden = false;
    renderAccountLabel();
    resetNavigation(); renderScopes(); render();
    await refreshReports(false);
    try { state.status = await api("/api/status"); renderService(); } catch (error) { if (state.session) message(errorKey(error), "error"); }
    if (helpCenterDemoPending && state.session) { helpCenterDemoPending = false; await loadHelpCenterDemo(); }
  }
  function snapshot() { return {page: state.page, mode: state.mode, chainAnchor: state.chainAnchor, selection: state.selection, filter: state.filter, query: state.query, expandedGroups: [...state.expandedGroups], zoom: state.zoom, panX: state.panX, panY: state.panY, raw: state.raw, rowPage: state.rowPage}; }
  function resetNavigation() { navigationEpoch = String(Date.now()) + Math.random().toString(16).slice(2); navigation.reset(snapshot()); window.history.replaceState({aa: navigationEpoch, index: 0}, "", "#" + state.page); updateBack(); }
  function transition(mutation, fit = false) {
    navigation.save(snapshot()); mutation(); navigation.record(snapshot());
    window.history.pushState({aa: navigationEpoch, index: navigation.index}, "", "#" + state.page);
    render(fit); navigation.save(snapshot()); updateBack();
  }
  function restore(snapshotValue) { for (const key of ["page", "mode", "chainAnchor", "selection", "filter", "query", "zoom", "panX", "panY", "raw", "rowPage"]) state[key] = snapshotValue[key]; state.expandedGroups = new Set(snapshotValue.expandedGroups); render(false); updateBack(); }
  function updateBack() { $("back").disabled = !navigation.canGoBack; }
  function goBack() { if (navigation.canGoBack) { navigation.save(snapshot()); window.history.back(); } }
  window.addEventListener("popstate", event => {
    if (!state.session) return;
    if (event.state?.aa === navigationEpoch && navigation.at(event.state.index)) { navigation.save(snapshot()); restore(navigation.restore(event.state.index)); }
    else { /* A previous source never restores data or a selection into this source. */ resetNavigation(); }
  });
  function scopes() { return (state.session?.scopes || []).map(scope => ({sourceId: scope.sourceId ?? scope.source_id ?? "", jobId: scope.jobId ?? scope.job_id ?? ""})); }
  function renderScopes() {
    $("import-scope").replaceChildren(); $("scope-list").replaceChildren();
    scopes().forEach((scope, index) => {
      const text = `${scope.sourceId} / ${scope.jobId}`; const option = element("option", "", text); option.value = String(index); $("import-scope").append(option);
      $("scope-list").append(element("li", "break", text));
    });
    $("import-open").disabled = !scopes().length;
  }
  function renderReports() {
    const select = $("report-select"), first = element("option", "", L("web.chooseReport")); first.value = ""; select.replaceChildren(first);
    for (const report of state.reports) {
      const status = report.state === "complete" ? L("metric.complete") : report.state === "incomplete" ? L("metric.incomplete") : report.state === "reported-private-verification" ? L("status.reported") : L("status.unknown");
      const title = `${report.title || report.id} · ${report.sourceId || "?"} / ${report.jobId || "?"} · ${status}`;
      const option = element("option", "", title); option.value = report.id; select.append(option);
    }
    select.value = state.reportId;
  }
  async function refreshReports(reloadSelected = true) {
    setBusy(1); const generation = loadGeneration;
    try {
      const payload = await api("/api/reports"); if (generation !== loadGeneration || !state.session) return;
      state.reports = payload.reports || []; if (payload.scopes) state.session.scopes = payload.scopes;
      renderReports(); renderScopes();
      if (reloadSelected && state.reportId) await loadReport(state.reportId);
      else if (!state.graph.nodes.length && !state.report && !state.privateReport) render();
      if (!state.reports.length && !state.graph.isDemo && state.metadata.adapter !== "hilfezentrum-synthetic-context") message("web.noReports");
    } catch (error) { if (state.session) message(errorKey(error), "error"); }
    finally { setBusy(-1); }
  }
  async function loadReport(id) {
    if (!id) return; const generation = ++loadGeneration; setBusy(1); message("");
    try {
      const payload = await api("/api/reports/" + encodeURIComponent(id)); if (generation !== loadGeneration || !state.session) return;
      setDocument(payload.graph, payload.metadata || {}, payload.report || null, payload.privateReport || null, id);
    } catch (error) { if (generation === loadGeneration && state.session) { $("report-select").value = state.reportId; message(errorKey(error), "error"); } }
    finally { setBusy(-1); }
  }
  function setDocument(documentValue, metadata, report, privateReport, id = "") {
    if (!documentValue || !Array.isArray(documentValue.nodes) || !Array.isArray(documentValue.edges)) { message("source.invalid", "error"); return; }
    state.graph = documentValue; state.metadata = metadata; state.report = report; state.privateReport = privateReport; state.reportId = id;
    state.selection = documentValue.nodes[0]?.id || ""; state.chainAnchor = state.selection; state.mode = documentValue.isDemo ? 2 : 0;
    state.query = ""; state.filter = 0; state.expandedGroups = new Set(); state.rowPage = 0; state.raw = false;
    resetNavigation(); renderReports(); render(true); navigation.save(snapshot());
    $("announcer").textContent = documentValue.isDemo ? L("mode.sample") : L("web.reportLoaded");
  }
  function boundaryKey() { return state.metadata.adapter === "hilfezentrum-synthetic-context" ? "web.helpCenterBoundary" : state.graph.isDemo ? "boundary.sample" : state.privateReport ? "web.privateBoundary" : state.report || state.graph.reportJSON ? "boundary.product" : "web.noDataBoundary"; }
  function provenanceText() {
    const provenance = state.metadata.inputProvenance;
    if (!provenance) return "";
    return L(state.metadata.adapter === "observations" ? "web.observationsProvenance" : "web.reportProvenance");
  }
  function renderMetrics() {
    const d = state.graph, metrics = [];
    if (state.metadata.adapter === "hilfezentrum-synthetic-context") {
      metrics.push(["hilfezentrum.accounts", 2, L("hilfezentrum.accountBoundary")], ["hilfezentrum.assignment", 1, L("status.reported")], ["hilfezentrum.case", 1, L("status.reported")], ["web.identityIntegration", "—", L("web.blocked")]);
    } else if (d.isDemo) {
      const statuses = chainStatuses(d), actions = d.nodes.filter(n => n.kind === "action"), good = actions.filter(n => statuses.get(n.id) === "verified").length;
      metrics.push(["metric.agents", d.nodes.filter(n => n.kind === "agent").length, L("metric.sampleAgents")], ["metric.delegations", d.edges.filter(e => e.relation === "delegates").length, L("metric.demo")], ["metric.chains", good, L("metric.sampleChains", {good, missing: actions.length - good})], ["metric.actions", actions.length, L("metric.demo")]);
    } else if (state.report || d.reportJSON) {
      metrics.push(["metric.reported", d.totalEntries ?? d.nodes.filter(n => n.kind === "entry").length, L("status.reported")], ["metric.tasks", d.reportedTaskCount ?? d.nodes.filter(n => n.kind === "task").length, L("basis.task")], ["metric.warnings", d.reportedWarningCount ?? d.warnings?.length ?? 0, L("web.structuralOnly")], ["metric.coverage", d.completeRead === true ? "✓" : "△", L(d.completeRead === true ? "metric.complete" : "metric.incomplete")]);
    } else {
      metrics.push(["metric.agents", "—", L("metric.unavailable")], ["metric.delegations", "—", L("metric.unavailable")], ["metric.chains", "—", L("metric.unavailable")], [state.privateReport ? "web.reportedFindings" : "metric.actions", state.privateReport ? d.nodes.length : "—", L(state.privateReport ? "status.reported" : "metric.unavailable")]);
    }
    $("metrics").replaceChildren(...metrics.map(([title, number, detail]) => {
      const el = element("article", "metric"); el.append(element("h2", "", L(title)), element("span", "value", number), element("p", "detail", detail)); return el;
    }));
    let coverage = L("app.observer");
    if (d.omitted > 0) coverage = L("graph.hidden", {count: d.omitted});
    if (d.completeRead === false) coverage += " · " + L("metric.incomplete");
    if (d.warnings?.length) coverage += " · " + L("web.diagnostics", {count: d.warnings.length});
    $("coverage").textContent = coverage; $("coverage").classList.toggle("incomplete", d.completeRead === false || d.omitted > 0);
    $("source-boundary").textContent = L(boundaryKey()) + (provenanceText() ? " " + L("web.inputProvenance") + ": " + provenanceText() : "") + (state.metadata.syntheticAccount && !d.isDemo && state.metadata.adapter !== "hilfezentrum-synthetic-context" ? " " + L("web.reportClaims") : "");
  }
  function render(fit = false) {
    const utility = ["host", "settings"].includes(state.page);
    $("page-title").textContent = L(state.page === "host" ? "web.service" : "nav." + state.page);
    $("data-mode").textContent = state.metadata.adapter === "hilfezentrum-synthetic-context" ? L("hilfezentrum.syntheticMode") : state.graph.isDemo ? L("mode.sample") : state.privateReport ? L("web.privateMode") : state.report || state.graph.reportJSON ? L("mode.product") : L("web.noReport");
    $("scope-description").textContent = state.graph.isDemo ? L("mode.demo") : state.metadata.sourceId || state.metadata.source_id || state.graph.source || L("source.empty");
    $("scope-job").textContent = state.metadata.jobId || state.metadata.job_id ? L("web.job") + ": " + (state.metadata.jobId || state.metadata.job_id) : "";
    for (const el of document.querySelectorAll("[data-page]")) { const active = el.dataset.page === state.page; el.classList.toggle("active", active); if (active) el.setAttribute("aria-current", "page"); else el.removeAttribute("aria-current"); }
    $("data-workspace").hidden = utility; $("report-controls").hidden = utility; $("service-page").hidden = state.page !== "host"; $("settings-page").hidden = state.page !== "settings";
    $("application").classList.toggle("inspector-hidden", utility || !state.inspectorOpen); $("inspector-toggle").setAttribute("aria-expanded", String(state.inspectorOpen));
    $("search").value = state.query; $("proof-filter").value = String(state.filter);
    for (const el of $("modes").querySelectorAll("button")) { const active = Number(el.dataset.mode) === state.mode; el.classList.toggle("active", active); el.setAttribute("aria-pressed", String(active)); }
    $("export").disabled = !(state.report || state.privateReport || state.graph.isDemo || state.metadata.adapter === "hilfezentrum-synthetic-context");
    $("focus-chain").disabled = !state.selection || state.selection.startsWith("cluster:"); $("copy-reference").disabled = !state.selection;
    $("expand-group").hidden = !state.selection.startsWith("cluster:");
    $("pulse-label").hidden = !state.graph.isDemo;
    $("critical-warning").hidden = !(state.graph.isDemo && state.graph.nodes.some(n => n.id === "agent-003"));
    $("mode-boundary").textContent = !state.graph.isDemo && state.mode !== 0 ? L("web.nonAgentMode") : "";
    renderMetrics(); renderGraph(fit); renderTable(); renderInspector(); renderService(); updateBack();
  }
  function warningForNode(node) {
    if (node.kind !== "cluster") return warningAssessment(state.graph, node.id);
    const members = state.graph.nodes.filter(n => n.kind === "agent" && n.group === node.group), assessments = members.map(n => warningAssessment(state.graph, n.id));
    const findings = assessments.filter(a => SEVERITIES.includes(a.outcome)).sort((a, b) => SEVERITIES.indexOf(b.outcome) - SEVERITIES.indexOf(a.outcome));
    return findings[0] || warningAssessment(state.graph, node.id);
  }
  function warningText(outcome) { const glyph = {information: "ⓘ", attention: "◇", warning: "⚠", critical: "‼", notAssessable: "?", checkedClear: "○"}[outcome] || "?"; return glyph + " " + L("warning." + outcome); }
  function renderGraph(fit = false) {
    graph = visibleGraph(state.graph, state, L, nodeTitle);
    const columns = Math.max(4, Math.min(10, Math.floor(($("graph-area").clientWidth || 650) / 164)));
    layout = graphLayout(graph.nodes, graph.edges, graph.agentOverview, columns);
    const statuses = chainStatuses(state.graph); graphStatuses.clear(); statuses.forEach((v, k) => graphStatuses.set(k, v));
    svgElements.clear(); edgeElements.length = 0; $("graph-nodes").replaceChildren(); $("graph-edges").replaceChildren();
    const edgeFragment = document.createDocumentFragment(), nodeFragment = document.createDocumentFragment();
    for (const e of graph.edges) {
      const a = layout.positions.get(e.from), b = layout.positions.get(e.to); if (!a || !b) continue;
      const x1 = a.x + 138, y1 = a.y + 24, x2 = b.x, y2 = b.y + 24, mid = (x1 + x2) / 2;
      const path = svgElement("path", {d: `M${x1},${y1} C${mid},${y1} ${mid},${y2} ${x2},${y2}`, class: "graph-edge" + (["verified", "observed"].includes(e.status) ? " proved" : "") + ([e.from, e.to].includes(state.selection) ? " selected" : "")});
      const title = svgElement("title", {}, `${L("relation." + e.relation)} · ${L("status." + e.status)}\n${(e.evidence || []).join(", ")}`); path.append(title); edgeFragment.append(path); edgeElements.push({element: path, edge: e});
    }
    for (const n of graph.nodes) {
      const p = layout.positions.get(n.id); if (!p) continue;
      const status = n.kind === "agent" ? statuses.get(n.id) || n.status : n.status, warning = warningForNode(n);
      const label = `${nodeTitle(n)}, ${L("kind." + n.kind)}, ${L("status." + status)}, ${warningText(warning.outcome)}`;
      const el = svgElement("g", {transform: `translate(${p.x},${p.y})`, class: "graph-node" + (n.id === state.selection ? " selected" : ""), "data-node-id": n.id, role: "button", tabindex: n.id === state.selection ? "0" : "-1", "aria-label": label, "aria-pressed": String(n.id === state.selection)});
      el.append(svgElement("title", {}, label + "\n" + n.id + "\n" + (n.facts || []).map(f => `${L(f.labelKey)}: ${factText(f)}`).join("\n")), svgElement("rect", {class: "card", width: 138, height: 48, rx: 6}), svgElement("circle", {cx: 11, cy: 13, r: 2.7, class: "status-" + status}));
      const title = nodeTitle(n); el.append(svgElement("text", {x: 20, y: 17, class: "title"}, title.length > 17 ? title.slice(0, 16) + "…" : title));
      el.append(svgElement("text", {x: 10, y: 30, class: "status-text status-" + status}, L("statusShort." + status)), svgElement("text", {x: 9, y: 42, class: "warning-text warning-" + warning.outcome}, warningText(warning.outcome)));
      if (["warning", "critical"].includes(warning.outcome)) el.append(svgElement("rect", {class: "pulse-border " + warning.outcome, width: 138, height: 48, rx: 6}));
      el.addEventListener("click", () => selectNode(n.id)); el.addEventListener("dblclick", () => n.kind === "cluster" ? expandGroup(n.id) : focusChain(n.id));
      el.addEventListener("keydown", event => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); event.stopPropagation(); n.kind === "cluster" ? expandGroup(n.id) : focusChain(n.id); } });
      svgElements.set(n.id, el); nodeFragment.append(el);
    }
    $("graph-edges").append(edgeFragment); $("graph-nodes").append(nodeFragment);
    $("graph-empty").hidden = graph.nodes.length > 0;
    $("graph-empty").textContent = L(!state.report && !state.privateReport && !state.graph.isDemo ? "web.noReportGraph" : state.graph.nodes.length ? "graph.filteredEmpty" : "graph.sourceEmpty");
    $("minimap").hidden = !graph.nodes.length;
    if (fit) fitGraph(); else updateViewport();
  }
  function graphDimensions() { return {width: $("graph-area").clientWidth || 700, height: Math.max(100, ($("graph-area").clientHeight || 380) - 45)}; }
  function fitGraph() {
    const {width, height} = graphDimensions(); state.zoom = Math.min(1.15, Math.max(0.15, Math.min((width - 40) / layout.width, (height - 35) / layout.height)));
    state.panX = Math.max(12, (width - layout.width * state.zoom) / 2); state.panY = 18; updateViewport();
  }
  function zoom(multiplier, center) {
    const dims = graphDimensions(), origin = center || {x: dims.width / 2, y: dims.height / 2};
    const next = Math.min(3, Math.max(0.15, state.zoom * multiplier));
    state.panX = origin.x - (origin.x - state.panX) * next / state.zoom; state.panY = origin.y - (origin.y - state.panY) * next / state.zoom; state.zoom = next; updateViewport();
  }
  function updateViewport() {
    $("graph-viewport").setAttribute("transform", `translate(${state.panX},${state.panY}) scale(${state.zoom})`);
    $("zoom-label").textContent = Math.round(state.zoom * 100) + " %";
    const {width, height} = graphDimensions(); let count = 0;
    for (const n of graph.nodes) {
      const p = layout.positions.get(n.id); if (!p) continue;
      const visible = p.x * state.zoom + state.panX < width && (p.x + 138) * state.zoom + state.panX > 0 && p.y * state.zoom + state.panY < height && (p.y + 48) * state.zoom + state.panY > 0;
      if (visible) count++;
      const pulse = svgElements.get(n.id)?.querySelector(".pulse-border"); if (pulse) pulse.setAttribute("visibility", !visible || document.hidden ? "hidden" : "visible");
    }
    $("graph-count").textContent = L("graph.count", {visible: count, total: state.graph.nodes.length});
    $("graph-area").classList.toggle("no-pulses", !$("pulse").checked || document.hidden);
    const mini = $("minimap-svg"); mini.replaceChildren(); const ratio = Math.min(112 / Math.max(1, layout.width), 56 / Math.max(1, layout.height));
    for (const n of graph.nodes) { const p = layout.positions.get(n.id); if (p) mini.append(svgElement("rect", {x: 4 + p.x * ratio, y: 4 + p.y * ratio, width: Math.max(2, 138 * ratio), height: Math.max(1, 48 * ratio)})); }
    mini.append(svgElement("rect", {class: "viewport", x: 4 - state.panX / state.zoom * ratio, y: 4 - state.panY / state.zoom * ratio, width: width / state.zoom * ratio, height: height / state.zoom * ratio}));
  }
  function selectNode(id) {
    if (!state.graph.nodes.some(n => n.id === id) && !graph.nodes.some(n => n.id === id)) return;
    const outside = !id.startsWith("cluster:") && !trace(state.graph, state.chainAnchor).has(id);
    if (outside && state.mode === 0) { transition(() => { state.selection = id; state.chainAnchor = id; }); return; }
    state.selection = id; if (outside) state.chainAnchor = id;
    for (const [nodeId, el] of svgElements) { el.classList.toggle("selected", nodeId === id); el.setAttribute("aria-pressed", String(nodeId === id)); el.setAttribute("tabindex", nodeId === id ? "0" : "-1"); }
    for (const {element: el, edge} of edgeElements) el.classList.toggle("selected", [edge.from, edge.to].includes(id));
    $("focus-chain").disabled = id.startsWith("cluster:"); $("copy-reference").disabled = false; $("expand-group").hidden = !id.startsWith("cluster:");
    renderTable(); renderInspector(); $("announcer").textContent = nodeTitle(state.graph.nodes.find(n => n.id === id) || graph.nodes.find(n => n.id === id));
  }
  function focusChain(id = state.selection) {
    if (!state.graph.nodes.some(n => n.id === id)) return;
    if (state.mode === 0 && state.chainAnchor === id) { selectNode(id); return; }
    transition(() => { state.selection = id; state.chainAnchor = id; state.mode = 0; }, true);
  }
  function expandGroup(id = state.selection) {
    if (!id.startsWith("cluster:")) return; const group = id.slice(8); if (state.expandedGroups.has(group)) return;
    transition(() => { state.expandedGroups.add(group); state.selection = state.graph.nodes.find(n => n.kind === "agent" && n.group === group)?.id || ""; }, true);
  }
  function renderTable() {
    const allRows = rowsForPage(state.graph, state.page), statuses = chainStatuses(state.graph), query = state.query.trim().toLocaleLowerCase();
    const rows = allRows.filter(n => {
      const status = n.kind === "agent" ? statuses.get(n.id) || n.status : n.status;
      return (!state.filter || (state.filter === 1 ? ["reported", "unknown", "incomplete", "contradictory"].includes(status) : ["observed", "verified"].includes(status))) && (!query || [nodeTitle(n), n.id, ...(n.facts || []).map(f => f.value), ...(n.evidence || [])].join(" ").toLocaleLowerCase().includes(query));
    });
    const perPage = 50, pages = Math.max(1, Math.ceil(rows.length / perPage)); state.rowPage = Math.min(state.rowPage, pages - 1);
    $("activity-rows").replaceChildren(...rows.slice(state.rowPage * perPage, (state.rowPage + 1) * perPage).map(n => {
      const row = element("tr", n.id === state.selection ? "selected" : ""), status = n.kind === "agent" ? statuses.get(n.id) || n.status : n.status;
      row.append(element("td", "", L("kind." + n.kind))); const name = element("td"); name.append(button(nodeTitle(n), () => selectNode(n.id))); row.append(name, element("td", "status-" + status, L("status." + status)), element("td", "", n.id), element("td", "", (n.evidence || []).join(", "))); return row;
    }));
    $("activity-heading").textContent = L(["agents", "delegations", "evidence", "findings"].includes(state.page) ? "nav." + state.page : "activity.title");
    $("table-count").textContent = L("web.rows", {count: rows.length}); $("table-empty").hidden = rows.length > 0;
    $("table-empty").textContent = L(state.graph.nodes.length ? "web.noPageRows" : "web.noReportGraph");
    $("rows-previous").disabled = state.rowPage === 0; $("rows-next").disabled = state.rowPage + 1 >= pages;
    $("rows-page").textContent = L("web.page", {current: state.rowPage + 1, total: pages});
  }
  function addDefinition(container, items) {
    const dl = element("dl"); for (const [key, value] of items) { dl.append(element("dt", "", L(key)), element("dd", "", value)); } container.append(dl);
  }
  function renderInspector() {
    const target = $("inspector-content"); target.replaceChildren(); const d = state.graph;
    const node = d.nodes.find(n => n.id === state.selection);
    if (!node && state.selection.startsWith("cluster:")) {
      const group = state.selection.slice(8), members = d.nodes.filter(n => n.kind === "agent" && n.group === group), ids = new Set(members.map(n => n.id));
      target.append(element("p", "inspector-kind", L("kind.cluster")), element("h3", "inspector-name", L("graph.clusterCount", {count: members.length})));
      addDefinition(target, [["field.internalDelegations", d.edges.filter(e => e.relation === "delegates" && ids.has(e.from) && ids.has(e.to)).length], ["field.externalRelationships", d.edges.filter(e => e.relation === "delegates" && ids.has(e.from) !== ids.has(e.to)).length]]);
      target.append(button(L("graph.openCluster"), () => expandGroup(), "primary"), element("h3", "", L("web.members")));
      const list = element("div", "chain-list"); members.forEach(n => list.append(button(nodeTitle(n), () => focusChain(n.id)))); target.append(list, element("p", "boundary", L("boundary.sample"))); return;
    }
    if (!node) { target.append(element("p", "muted small", L("inspector.empty"))); return; }
    const verdict = node.kind === "agent" ? chainStatuses(d).get(node.id) || node.status : node.status;
    target.append(element("p", "inspector-kind", L("kind." + node.kind)), element("h3", "inspector-name", nodeTitle(node)), element("p", "inspector-status status-" + verdict, L("status." + verdict)));
    const warning = warningAssessment(d, node.id), warningBox = element("section", "warning-box");
    warningBox.append(element("h3", "", L("warning.title")), element("p", "warning-state warning-" + warning.outcome, (warning.isSynthetic ? L("warning.demoPrefix") + " · " : "") + warningText(warning.outcome)), element("p", "", L(warning.reasonKey)));
    addDefinition(warningBox, [["warning.assessability", L(warning.checkPerformed && warning.dataState === "current" ? "warning.assessed" : "warning.notAssessable")], ["warning.node", node.id], ["warning.relationship", warning.relationship || L("warning.notApplicable")], ["warning.time", warning.timestamp || L("status.unknown")], ["warning.source", L(warning.sourceKey)], ["warning.evidence", warning.evidence.length ? warning.evidence.join(", ") : L("status.unknown")]]);
    warningBox.append(element("p", "muted", L("warning.scope"))); target.append(warningBox);
    const tabs = element("div", "segments tabs"); for (const [raw, key] of [[false, "inspector.chain"], [true, "inspector.raw"]]) { const tab = button(L(key), () => { state.raw = raw; renderInspector(); }, state.raw === raw ? "active" : ""); tab.setAttribute("aria-pressed", String(state.raw === raw)); tabs.append(tab); } target.append(tabs);
    if (state.raw) {
      target.append(element("pre", "", JSON.stringify(node, null, 2)), element("h3", "", L("web.rawSource")));
      const source = state.privateReport || state.report || (state.metadata.adapter === "hilfezentrum-synthetic-context" && state.graph.reportJSON);
      if (source) { const details = element("details"); details.append(element("summary", "", L(state.metadata.adapter === "hilfezentrum-synthetic-context" ? "hilfezentrum.sourceContext" : state.privateReport ? "web.privateReport" : "web.neutralReport")), element("pre", "", reportText(state.graph, state.report, state.privateReport))); target.append(details); }
      if (Object.keys(state.metadata).length) { const details = element("details"); details.append(element("summary", "", L("web.metadata")), element("pre", "", JSON.stringify(state.metadata, null, 2))); target.append(details); }
      target.append(element("p", "boundary", L(boundaryKey()))); return;
    }
    target.append(element("p", "small muted", L(state.metadata.adapter === "hilfezentrum-synthetic-context" ? "web.helpCenterBoundary" : d.isDemo ? "inspector.sampleExplanation" : state.privateReport ? "web.privateExplanation" : "inspector.productExplanation")), element("h3", "", L("inspector.selected")));
    addDefinition(target, [["web.reference", node.id], ...(node.facts || []).map(f => [f.labelKey, factText(f)]), ["field.evidence", (node.evidence || []).join(", ") || L("status.unknown")]]);
    const source = state.metadata.sourceId || state.metadata.source_id || d.source; if (source) addDefinition(target, [["inspector.source", source], ["web.job", state.metadata.jobId || state.metadata.job_id || L("status.unknown")]]);
    if (provenanceText()) addDefinition(target, [["web.inputProvenance", provenanceText()]]);
    target.append(element("h3", "", L("inspector.origin")));
    const anchored = trace(d, state.chainAnchor), ids = anchored.has(node.id) ? anchored : trace(d, node.id), chainNodes = d.nodes.filter(n => ids.has(n.id)), chainEdges = d.edges.filter(e => ids.has(e.from) && ids.has(e.to));
    const ordered = graphLayout(chainNodes, chainEdges); chainNodes.sort((a, b) => { const p = ordered.positions.get(a.id), q = ordered.positions.get(b.id); return p.x - q.x || p.y - q.y; });
    const list = element("div", "chain-list"); for (const item of chainNodes) list.append(button(`${nodeTitle(item)} · ${L("kind." + item.kind)}`, () => selectNode(item.id), item.id === state.selection ? "selected" : "")); target.append(list);
    target.append(element("h3", "", L("web.relationships")));
    const relationships = d.edges.filter(e => e.from === node.id || e.to === node.id);
    for (const edge of relationships) {
      const relation = element("p", "small break", `${edge.from} → ${edge.to} · ${L("relation." + edge.relation)} · ${L("status." + edge.status)}`); target.append(relation);
      if (edge.evidence?.length) target.append(element("p", "small muted break", L("field.evidence") + ": " + edge.evidence.join(", ")));
    }
    if (!relationships.length) target.append(element("p", "small muted", L("web.noRelationships")));
    target.append(element("h3", "", L("inspector.integrity")));
    const qualified = d.isDemo && chainStatuses(d).get(state.chainAnchor) === "verified";
    addDefinition(target, ["inspector.signatures", "inspector.binding", "inspector.loss"].map(key => [key, L(qualified ? "demo.synthetic" : "status.unknown")]));
    target.append(element("h3", "", L("inspector.boundary")), element("p", "boundary", L(boundaryKey()))); if (node.kind === "action") target.append(element("p", "small muted", L("boundary.durable")));
  }
  function renderService() {
    const target = $("service-details"); target.replaceChildren();
    const production = state.session?.production || {}, status = state.status || {};
    addDefinition(target, [["web.identityIntegration", L(production.identity === "blocked" || !production.identity ? "web.blocked" : "web.configured")], ["web.collectorIntegration", L(production.collector === "blocked" || !production.collector ? "web.blocked" : "web.configured")], ["web.account", state.session?.user?.synthetic ? L("web.syntheticAccount") : L("web.unknownIdentity")], ["web.currentAdapter", state.metadata.adapter || L("status.unknown")], ["web.currentSource", state.metadata.sourceId || state.graph.source || L("source.empty")]]);
    if (Object.keys(status).length) { const details = element("details"); details.append(element("summary", "", L("web.capabilities")), element("pre", "", JSON.stringify(status, null, 2))); target.append(details); }
    target.append(element("p", "boundary", L("web.productionBoundary")));
  }

  $("login-form").addEventListener("submit", async event => {
    event.preventDefault(); const submit = event.submitter; if (submit) submit.disabled = true; $("login-message").hidden = true;
    try {
      const bytes = new TextEncoder().encode($("username").value + ":" + $("password").value); let binary = ""; for (const byte of bytes) binary += String.fromCharCode(byte);
      const session = await api("/api/login", {method: "POST", body: {}, headers: {Authorization: "Basic " + btoa(binary)}}); await enterSession(session);
    } catch (error) { $("login-message").textContent = L(error.status === 401 ? "web.loginFailed" : errorKey(error)); $("login-message").hidden = false; $("password").value = ""; }
    finally { if (submit) submit.disabled = false; }
  });
  $("logout").addEventListener("click", async () => { setBusy(1); try { await api("/api/logout", {method: "POST", body: {}}); showLogin(); $("username").focus(); } catch (error) { if (state.session) message(errorKey(error), "error"); } finally { setBusy(-1); } });
  for (const el of document.querySelectorAll("[data-page]")) el.addEventListener("click", event => { event.preventDefault(); if (state.page !== el.dataset.page) transition(() => { state.page = el.dataset.page; state.rowPage = 0; }); $("application").classList.remove("sidebar-open"); $("sidebar-toggle").setAttribute("aria-expanded", "false"); });
  $("sidebar-toggle").addEventListener("click", () => { const opened = $("application").classList.toggle("sidebar-open"); $("sidebar-toggle").setAttribute("aria-expanded", String(opened)); });
  function toggleInspector(open) { state.inspectorOpen = open; render(); if (open && window.innerWidth < 1000) $("inspector").scrollIntoView({block: "start", behavior: "auto"}); }
  $("inspector-toggle").addEventListener("click", () => toggleInspector(!state.inspectorOpen)); $("inspector-close").addEventListener("click", () => toggleInspector(false));
  $("language").addEventListener("change", event => chooseLanguage(event.target.value)); $("login-language").addEventListener("change", event => chooseLanguage(event.target.value));
  $("theme").addEventListener("change", event => { document.documentElement.dataset.theme = event.target.value; savePreference("theme", event.target.value); });
  $("report-select").addEventListener("change", event => loadReport(event.target.value));
  $("refresh").addEventListener("click", () => refreshReports());
  $("demo-load").addEventListener("click", async () => {
    const generation = ++loadGeneration; setBusy(1); message("");
    try { const payload = await api("/api/demo"); if (generation === loadGeneration && state.session) { setDocument(payload.graph, payload.metadata || {synthetic: true}, null, null); message("web.demoBoundary", "warning"); } }
    catch (error) { if (state.session) message(errorKey(error), "error"); } finally { setBusy(-1); }
  });
  async function loadHelpCenterDemo() {
    const generation = ++loadGeneration; setBusy(1); message("");
    try {
      const payload = await api("/api/hilfezentrum/demo", {method: "POST", body: {}});
      if (generation === loadGeneration && state.session) { state.page = "graph"; setDocument(helpCenterContextGraph(payload.context), payload.metadata, null, null); message("web.helpCenterBoundary", "warning"); }
    } catch (error) { if (state.session) message(errorKey(error), "error"); } finally { setBusy(-1); }
  }
  $("help-center-demo").addEventListener("click", loadHelpCenterDemo);
  $("export").addEventListener("click", () => {
    const value = reportText(state.graph, state.report, state.privateReport); if (value === null) return;
    const blob = new Blob([value], {type: "application/json"}), url = URL.createObjectURL(blob), link = element("a");
    link.href = url; link.download = state.metadata.adapter === "hilfezentrum-synthetic-context" ? "AgentAuthority-HelpCenter-SYNTHETIC.json" : state.privateReport ? "AgentAuthority-PrivateVerification.json" : state.graph.isDemo ? "AgentAuthority-SyntheticDemo.json" : "AgentAuthority-Evidence.json";
    document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  $("import-open").addEventListener("click", () => { $("import-message").hidden = true; $("import-dialog").showModal(); }); $("import-cancel").addEventListener("click", () => $("import-dialog").close());
  $("import-dialog").addEventListener("cancel", event => { if (state.importing) event.preventDefault(); });
  $("import-form").addEventListener("submit", async event => {
    event.preventDefault(); const file = $("import-file").files[0], scope = scopes()[Number($("import-scope").value)];
    const submit = event.submitter; $("import-message").hidden = true; if (submit) submit.disabled = true; state.importing = true; $("import-cancel").disabled = true; setBusy(1);
    try {
      if (!file || !scope) throw new APIError(400, "invalid_import"); if (file.size > 8 * 1024 * 1024) throw new APIError(413, "too_large");
      let rawData; try { rawData = new TextDecoder("utf-8", {fatal: true, ignoreBOM: true}).decode(await file.arrayBuffer()); } catch (_) { throw new APIError(400, "invalid_encoding"); }
      const payload = await api("/api/reports/import", {method: "POST", body: {sourceId: scope.sourceId, jobId: scope.jobId, kind: $("import-kind").value, rawData}});
      $("import-dialog").close(); $("import-file").value = ""; await refreshReports(false);
      const id = payload.id || payload.reportId || payload.metadata?.id; if (payload.graph) setDocument(payload.graph, payload.metadata || {}, payload.report || null, payload.privateReport || null, id || ""); else if (id) await loadReport(id);
      message("web.imported", "success");
    } catch (error) { $("import-message").textContent = L(errorKey(error)); $("import-message").hidden = false; }
    finally { if (submit) submit.disabled = false; state.importing = false; $("import-cancel").disabled = false; setBusy(-1); }
  });
  for (const el of $("modes").querySelectorAll("button")) el.addEventListener("click", () => { const mode = Number(el.dataset.mode); if (state.mode !== mode) transition(() => { state.mode = mode; }, true); });
  $("proof-filter").addEventListener("change", event => transition(() => { state.filter = Number(event.target.value); state.rowPage = 0; }, true));
  function applySearch() { const query = $("search").value.slice(0, 200); if (query !== state.query) transition(() => { state.query = query; state.rowPage = 0; }, true); }
  $("search-form").addEventListener("submit", event => { event.preventDefault(); applySearch(); }); $("search").addEventListener("search", applySearch);
  $("back").addEventListener("click", goBack); $("focus-chain").addEventListener("click", () => focusChain()); $("expand-group").addEventListener("click", () => expandGroup());
  $("copy-reference").addEventListener("click", async () => { try { await navigator.clipboard.writeText(state.selection); message("web.copied", "success"); } catch (_) { message("web.copyUnavailable"); } });
  $("critical-warning").addEventListener("click", () => focusChain("agent-003"));
  $("zoom-out").addEventListener("click", () => zoom(1 / 1.15)); $("zoom-in").addEventListener("click", () => zoom(1.15)); $("fit").addEventListener("click", fitGraph); $("minimap").addEventListener("click", fitGraph);
  $("pulse").addEventListener("change", () => { savePreference("pulse", String($("pulse").checked)); updateViewport(); }); document.addEventListener("visibilitychange", updateViewport);
  $("rows-previous").addEventListener("click", () => { state.rowPage = Math.max(0, state.rowPage - 1); renderTable(); }); $("rows-next").addEventListener("click", () => { state.rowPage++; renderTable(); });
  let drag = null;
  $("graph-svg").addEventListener("pointerdown", event => {
    if (event.target.closest(".graph-node") || event.button !== 0) return;
    drag = {id: event.pointerId, x: event.clientX, y: event.clientY, panX: state.panX, panY: state.panY}; $("graph-svg").setPointerCapture(event.pointerId); $("graph-svg").classList.add("dragging"); $("graph-area").focus();
  });
  $("graph-svg").addEventListener("pointermove", event => { if (drag && event.pointerId === drag.id) { state.panX = drag.panX + event.clientX - drag.x; state.panY = drag.panY + event.clientY - drag.y; updateViewport(); } });
  function endDrag() { drag = null; $("graph-svg").classList.remove("dragging"); }
  $("graph-svg").addEventListener("pointerup", endDrag); $("graph-svg").addEventListener("pointercancel", endDrag);
  $("graph-area").addEventListener("wheel", event => {
    event.preventDefault(); if (event.ctrlKey || event.metaKey) { const rect = $("graph-area").getBoundingClientRect(); zoom(event.deltaY < 0 ? 1.06 : .94, {x: event.clientX - rect.left, y: event.clientY - rect.top}); }
    else { state.panX -= event.deltaX; state.panY -= event.deltaY; updateViewport(); }
  }, {passive: false});
  $("graph-area").addEventListener("keydown", event => {
    if (["+", "=", "-", "0"].includes(event.key)) { event.preventDefault(); event.key === "0" ? fitGraph() : zoom(event.key === "-" ? 1 / 1.15 : 1.15); return; }
    if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key) && graph.nodes.length) {
      event.preventDefault(); const ids = graph.nodes.map(n => n.id), index = Math.max(0, ids.indexOf(state.selection)), delta = ["ArrowLeft", "ArrowUp"].includes(event.key) ? -1 : 1, id = ids[(index + delta + ids.length) % ids.length];
      selectNode(id); const p = layout.positions.get(id); if (p) { const dims = graphDimensions(); state.zoom = Math.max(.85, state.zoom); state.panX = dims.width / 2 - (p.x + 69) * state.zoom; state.panY = dims.height / 2 - (p.y + 24) * state.zoom; updateViewport(); }
      svgElements.get(id)?.focus({preventScroll: true});
    } else if (event.key === "Enter" || event.key === " ") { event.preventDefault(); state.selection.startsWith("cluster:") ? expandGroup() : focusChain(); }
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape") { $("application").classList.remove("sidebar-open"); $("sidebar-toggle").setAttribute("aria-expanded", "false"); }
    if (!state.session || $("import-dialog").open) return;
    if (event.altKey && event.key === "ArrowLeft" && navigation.canGoBack) { event.preventDefault(); goBack(); }
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "f" && !["settings", "host"].includes(state.page)) { event.preventDefault(); $("search").focus(); }
  });
  if (typeof ResizeObserver !== "undefined") { let previousWidth = 0; new ResizeObserver(() => { const width = $("graph-area").clientWidth; if (width && Math.abs(previousWidth - width) > 20 && state.session) { previousWidth = width; renderGraph(false); } else updateViewport(); }).observe($("graph-area")); }
  let helpAccountTicket = /^#account-ticket=([A-Za-z0-9_-]{43})$/.exec(location.hash)?.[1] || null;
  if (helpAccountTicket) history.replaceState(null, '', location.pathname);
  async function start() {
    preference = helpCenterDemoLanguage || readPreference("language", "system"); language = resolveLanguage(preference); document.documentElement.dataset.theme = readPreference("theme", "system"); $("theme").value = document.documentElement.dataset.theme; $("pulse").checked = readPreference("pulse", "true") !== "false";
    try { const response = await fetch(new URL("static/strings.json", appBase), {credentials: "same-origin"}); if (!response.ok) throw new Error("catalog"); catalog = await response.json(); } catch (_) { $("login-message").textContent = "Sprachressourcen nicht verfügbar / Language resources unavailable"; $("login-message").hidden = false; return; }
    translateStatic();
    if (helpAccountTicket) {
      showLogin();
      const button = document.createElement('button'); button.type = 'button';
      button.textContent = language === 'de' ? 'Mit ausgewähltem Hilfezentrum-Konto anmelden' : 'Sign in with the selected Help Center account';
      $('login-form').prepend(button);
      button.onclick = async () => {
        button.disabled = true;
        const ticket = helpAccountTicket; helpAccountTicket = null;
        try {
          const session = await api('/api/hilfezentrum/login', {method:'POST', body:{ticket}});
          await enterSession(session);
          const payload = await api('/api/hilfezentrum/context', {method:'POST', body:{}});
          setDocument(helpCenterContextGraph(payload.context), {adapter:'helpcenter-account-context', synthetic:false, accessIdentity:'helpcenter-account', sourceAuthentication:'helpcenter-account-only', agentIdentityVerified:false}, null, null);
        } catch (error) { $('login-message').textContent = L(errorKey(error)); $('login-message').hidden = false; }
      };
      return;
    }
    try { await enterSession(await api("/api/session")); } catch (error) { showLogin(); if (error.status !== 401) { $("login-message").textContent = L(errorKey(error)); $("login-message").hidden = false; } }
  }
  start();
})(typeof globalThis !== "undefined" ? globalThis : this);
