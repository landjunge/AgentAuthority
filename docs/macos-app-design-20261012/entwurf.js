'use strict';
// Ausschließlich lokaler Interaktionsentwurf. Keine Engine, kein Netzwerk, keine Freigaben.
const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const completeSteps = [
  ['Agentenidentität', 'Testagent B · Schlüssel B-02', 'Test-CA / registrierender Controller', 'E-091', 'agent-b'],
  ['Authority & Herkunft', 'Testauftrag J-024 · nur Testziel #17', 'Aussteller: Test-Controller · 14:32:03–14:32:13', 'E-096', 'authority'],
  ['Delegation A → B', 'Auftrag und Annahme signiert', 'Elternreferenz, Scope und Nonce geprüft', 'E-098', 'agent-b'],
  ['Ausführender Prozess', 'python3.12 · PID 8421 · Instanz #03', 'Audit-Token / Startzeit / Boot-Kontext', 'E-101', 'process'],
  ['Beobachtete Systemhandlung', 'Dateischreibzugriff auf Objekt #17', 'Kernelbeobachtung · 14:32:08.412', 'E-108', 'action'],
  ['Evidence & Verlustkontrolle', 'Dateireferenz und Erfassungsfenster geprüft', 'Signaturen gültig · keine gemessene Sequenzlücke', 'E-109', 'evidence']
];
const partialSteps = [
  ['Agentenidentität', 'Testagent C · als Actor gemeldet', 'Kein geprüfter Identitätsbeleg dieser Kette', 'E-104', 'agent-c', true],
  ['Authority & Herkunft', 'Testauftrag J-025 · Scope gemeldet', 'Aussteller und Gültigkeit nicht nachgewiesen', 'E-104', 'authority', true],
  ['Delegation A → C', 'Übergabe gemeldet · Annahme fehlt', 'Kein signierter Annahmebeleg eingelesen', '—', 'agent-c', true],
  ['Ausführender Prozess', 'Nicht belastbar zugeordnet', 'PID oder Prozessname allein reichen nicht', '—', 'unknown', true],
  ['Systemhandlung', 'Dateischreibzugriff als Ergebnis gemeldet', 'Kein passendes unabhängiges Kernelereignis', '—', 'unproven-action', true],
  ['Evidence & Verlustkontrolle', 'Abdeckung unbekannt', 'Fehlende Ereignisse sind kein Beleg für Untätigkeit', '—', 'evidence', true]
];
const selections = {
 'agent-a':['AGENT & IDENTITÄT','Koordinator A','Testidentität A-01 · registriert'],
 'identity':['IDENTITÄTSNACHWEIS','Testidentität A-01','Test-CA · Schlüssel und Registrierung'],
 'authority':['AUTHORITY & HERKUNFT','Testauftrag J-024','Externer Test-Controller · eingegrenzter Scope'],
 'agent-b':['AGENT & DELEGATION','Ausführender B','Testidentität B-02 · Delegation A → B'],
 'process':['AUSFÜHRENDE PROZESSINSTANZ','python3.12','PID 8421 · Instanz #03 · Start und Boot-Kontext'],
 'action':['BEOBACHTETE SYSTEMHANDLUNG','Datei schreiben','Testziel · Objekt #17'],
 'agent-c':['DELEGATION MIT NACHWEISLÜCKE','Testagent C','Chain C-025 · Annahmebeleg fehlt'],
 'unknown':['PROZESSZUORDNUNG','Nicht zugeordnet','Chain C-025 · kein belastbares Binding'],
 'unproven-action':['GEMELDETE SYSTEMHANDLUNG','Datei schreiben','Chain C-025 · tatsächliche Wirkung unbekannt'],
 'evidence':['EVIDENCE & NACHWEIS','Evidence E-108','Referenzen und Beweisgrenzen der ausgewählten Kette']
};
let selected = 'action', scale = 1, offset = { x: 0, y: 0 }, dragging = null, statusFilter = 'all', search = '', toastTimer;
const isMaster = () => $('#scenario').value === 'master';
const isPartial = (key) => ['agent-c','unknown','unproven-action'].includes(key);
function toast(message) { $('#toast').textContent = message; $('#toast').hidden = false; clearTimeout(toastTimer); toastTimer = setTimeout(()=>$('#toast').hidden=true, 4000); }
function openSheet(title, html) { $('#sheet-title').textContent=title; $('#sheet-body').innerHTML=html; if (!$('#sheet').open) $('#sheet').showModal(); }
function setTab(tab) { $$('.inspector-tabs button').forEach(b=>{ b.classList.toggle('active',b.dataset.tab===tab); b.setAttribute('aria-selected',String(b.dataset.tab===tab)); }); $('#chain-inspector').hidden=tab!=='chain'; $('#raw-inspector').hidden=tab!=='raw'; }
function drawChain(steps) {
 $('#evidence-chain').replaceChildren();
 steps.forEach(([title,detail,source,ref,key,missing])=>{
  const li = document.createElement('li');
  const icon = document.createElement('span'); icon.className='step-icon'+(missing?' missing':''); icon.textContent=missing?'?':'✓';
  const b = document.createElement('button');
  const head = document.createElement('b'); head.textContent=title;
  const r = document.createElement('span'); r.className='ref'; r.textContent=ref; head.append(r);
  const small = document.createElement('small');small.textContent=detail;
  const em = document.createElement('em');em.textContent=source;
  b.append(head,small,em);b.addEventListener('click',()=>selectNode(key));li.append(icon,b);$('#evidence-chain').append(li);
 });
}
function selectNode(key) {
 selected=key;
 document.body.classList.remove('no-inspector');
 $$('.node').forEach(n=>{const active=n.dataset.node===key;n.classList.toggle('selected',active);n.setAttribute('aria-pressed',String(active));});
 const s=selections[key]||selections.action, partial=isPartial(key);
 $('#inspector-type').textContent=s[0]; $('#selection-title').textContent=s[1]; $('#selection-subtitle').textContent=s[2];
 $('#selection-status').className='badge '+(isMaster()?'unknown':partial?'warning':'good');
 $('#selection-status').textContent=isMaster()?'? Identität & Wirkung unbekannt':partial?'△ Nachweiskette lückenhaft':'✓ Vollständig im Testscope';
 const selectedExplanations={
  'agent-a':'Koordinator A ist im Testlauf mit Schlüssel A-01 registriert. Der Test-Controller stellte seinen Auftrag aus. A delegierte den eingegrenzten Dateischreibzugriff an B.',
  'identity':'Die Test-CA bindet Schlüssel A-01 an Koordinator A. Dieser Anker gilt für den kontrollierten Testlauf und beglaubigt keine externe Modellsitzung.',
  'authority':'Der Test-Controller stellte J-024 für Testziel #17 aus. Die Delegation A → B übernimmt nur diesen Scope und dessen Gültigkeitsfenster. Agent Authority untersucht diese Nachweise.',
  'agent-b':'Testagent B ist mit Schlüssel B-02 registriert und nahm die Delegation von A signiert an. Sein Prozessbinding führt zu Instanz #03 und deren beobachtetem Schreibzugriff.',
  'process':'Instanz #03 gehört zu Testagent B. PID 8421 wird mit Startzeit, Audit-Token und Boot-Kontext verbunden. Der Kernelkanal ordnet den Schreibzugriff dieser Instanz zu.',
  'action':'Die Handlung ist Prozess #03 zugeordnet. Dessen Binding führt über die signierte Delegation zu Testagent B und Auftrag J-024.',
  'evidence':'Die Kette verweist auf Identitätsanker, Auftrag, Delegationsannahme, Prozessbinding und Kernelereignis. Signaturen, Objektbezug und Verlustkontrolle werden getrennt geprüft.'
 };
 $('#explanation').textContent=isMaster()?'Der aktuelle Produktbericht verknüpft Meldungen über einen gemeldeten Aufgabenbezug. Er liefert keinen Nachweis einer Agentenidentität, Rechteübernahme oder tatsächlichen Systemwirkung.':partial?'Eine Übergabe und ein Ergebnis wurden gemeldet. Annahme, Prozessbinding und unabhängige Handlung fehlen. Eine vollständige Agenten-Handlungszuordnung ist unbekannt.':selectedExplanations[key]||selectedExplanations.action;
 const masterSteps=[
  ['Quelle','json-directory · local-design-fixture','Quellenneutraler Eingang · nicht authentisiert','E1','identity',true],
  ['Gemeldeter Actor','local-client','Actor-Typ ist eine Meldung, keine Identität','E1','agent-b',true],
  ['Gemeldeter Aufgabenbezug','task-1 · Zuordnung durch task_key','Keine nachgewiesene Delegation oder Authority','E1','authority',true],
  ['Prozess & Systemwirkung','Im Produktvertrag nicht enthalten','Keine unabhängige Prozess-Handlungszuordnung','—','process',true],
  ['Dateinachweis','SHA-256 der gelesenen JSON-Datei','Fingerabdruck authentisiert keinen Verfasser','E1','evidence'],
  ['Aufnahmezustand','Vollständig im bezeichneten Leseumfang','Keine Vollständigkeit aller Agentenaktivität','E3','evidence']
 ];
 const selectionSteps=completeSteps.map(step=>[...step]);
 if(['agent-a','identity'].includes(key))selectionSteps[0]=['Agentenidentität','Koordinator A · Schlüssel A-01','Test-CA / registrierender Controller','E-090','identity'];
 drawChain(isMaster()?masterSteps:partial?partialSteps:selectionSteps);
 $('#chain-inspector .section-label span').textContent=isMaster()?'Vertrag v1':partial?'Nachweise fehlen':'6 / 6';
 const integrity=$('#integrity-box');
 integrity.querySelector('strong').textContent=isMaster()?'Struktur ≠ Authentisierung':partial?'Integrität nicht abschließend prüfbar':'Integrität im Testscope';
 [...integrity.querySelectorAll('li b')].forEach(b=>{b.textContent=isMaster()?'Unbekannt':partial?'Fehlt':'Geprüft';b.style.color=isMaster()?'var(--muted)':partial?'var(--amber-text)':'var(--green-text)';});
 $('#boundary-note p').textContent=isMaster()?'ordinal ist gespeicherte Reihenfolge, keine Kernelzeit. SHA-256 ist ein Dateifingerabdruck, keine Signatur. Ein Ergebnisbeitrag beweist keinen Abschluss oder Vollzug.':'Registrierte Testidentitäten. Keine Beglaubigung einer externen Provider- oder Modellsitzung. Ein Schreibereignis belegt keine dauerhafte Speicherung.';
 $('#evidence-open').firstChild.textContent=isMaster()?'Produktvertrag ansehen ':partial?'Fehlende Nachweise untersuchen ':'Evidence E-108 ansehen ';
 $('#graph-status').textContent=isMaster()?'Aktueller master: gemeldete Aufgabenbezüge':partial?'C-025: Nachweiskette lückenhaft':'C-024: vollständig im Testscope';
 $('#graph-status').style.color=isMaster()?'var(--muted)':partial?'var(--amber-text)':'var(--green-text)';
 $('#scope-integrity').textContent=isMaster()?'Identität, Authority, Prozess und Wirkung unbekannt':partial?'Annahme, Prozessbinding und Handlung nicht belegt':'Signaturen, Bindings & Verlustkontrolle geprüft';
 $('#chain-heading').textContent=isMaster()?'Gemeldeten Aufgabenbezug untersuchen':partial?'Fehlende Prozesszuordnung untersuchen':'Dateischreibzugriff untersuchen';
 $('#chain-meta').textContent=isMaster()?'Aufgabe A1 · gespeicherte Reihenfolge':partial?'Chain C-025 · 1 gemeldete Übergabe':'Chain C-024 · 1 Delegationsstufe';
 $('#raw-data').textContent=JSON.stringify(isMaster()?{
  schema_version:'agent-authority-observation-report-v1',role:'observer_only',source:{kind:'json-directory',source_id:'local-design-fixture',source_authenticated:false,identity:'UNBEKANNT',effect:'UNBEKANNT'},task_completion_proven:false,rights_inherited:false
 }:{schema:'UI-Konzept · nicht implementiert',sample:true,selection:key,chain:partial?'C-025':'C-024',scope:'kontrollierte Testidentitäten',identity:partial?'gemeldet':'Test-CA',process_instance:partial?null:{pid:8421,instance:'#03',binding:'Beispiel eines Kernelbindings'},action:partial?'gemeldet':'Dateischreibzugriff',chain_completeness:partial?'lückenhaft':'vollständig im Testscope',provider_identity:'UNBEKANNT',durable_effect:'UNBEKANNT'},null,2);
 setTab('chain');
 $$('.activity-panel tr[data-select]').forEach(r=>r.classList.toggle('selected-row',isPartial(r.dataset.select)===partial));
}
function applyTransform(){ $('#graph-content').setAttribute('transform',`translate(${offset.x} ${offset.y}) scale(${scale})`); $('#zoom-value').textContent=`${Math.round(scale*100)} %`; const visible=Math.min(100,100/scale); $('#mini-view').style.width=`${visible}%`; $('#mini-view').style.height=`${visible}%`; }
function zoom(delta){const next=Math.max(.5,Math.min(2.5,scale+delta));offset.x+=(1030/2-offset.x)*(1-next/scale);offset.y+=(440/2-offset.y)*(1-next/scale);scale=next;applyTransform();}
function fit(){scale=1;offset={x:0,y:0};applyTransform();}
function applyFilter(){ $$('.node').forEach(n=>{const partial=isPartial(n.dataset.node);const matches=(statusFilter==='all'||(statusFilter==='partial'?partial:!partial))&&(!search||n.textContent.toLocaleLowerCase('de').includes(search));n.classList.toggle('dimmed',!matches);});$('.links').style.opacity=search?.3:1;$('#filter').firstChild.nextSibling.textContent=statusFilter==='all'?'Alle Zustände ':statusFilter==='partial'?'Nachweise fehlen ':'Belegte Beziehungen '; }
function updateMode(){document.body.classList.toggle('master-mode',isMaster());$('.demo-tag').textContent=isMaster()?'MASTER · HEUTIGER DATENVERTRAG':'ENTWURF · BEISPIELDATEN';
 const metricValues=isMaster()?['—','—','—','—']:['12<span> / 16 registriert</span>','18','36<span> / 42 vollständig</span>','248'];
 const descriptions=isMaster()?['Keine aktive Prozessmessung im Vertrag','Keine nachgewiesene Delegation im Vertrag','Vollständige Chains nicht messbar','Meldungen sind keine Systemhandlungen']:['Mit beobachteter Prozessinstanz','16 angenommen · 2 offen','<b class="amber-text">4 lückenhaft</b> · 2 unbekannt','Beobachtet · im ausgewählten Lauf'];
 ['agents','delegations','chains','actions'].forEach((n,i)=>{$(`#${n}-value`).innerHTML=metricValues[i];$(`#${n}-description`).innerHTML=descriptions[i];});
 $('#coverage').innerHTML=isMaster()?'Dateifingerprints & Strukturanalyse <i>·</i> <b class="amber-text">Quellenauthentisierung fehlt</b>':'Signaturen geprüft <i>·</i> <b class="amber-text">2 Chains: Verlustkontrolle fehlt</b>';
 const nodeChanges=isMaster()?{
  'agent-a':['MELDUNG','Auftrag gemeldet','local-client · ordinal 1','Actor nicht authentisiert'],
  'identity':['QUELLENREFERENZ',null,'json-directory · lokale Datei',null],
  'authority':['AUTHORITY','Unbekannt','Keine Authority-Felder im Vertrag','Rechteübernahme unbelegt'],
  'agent-b':['AUFGABENBEZUG','Übernahme gemeldet','task-1 · ordinal 2','Nur gemeldeter Aufgabenbezug'],
  'process':['PROZESSINSTANZ','Unbekannt','Kein Prozessfeld im Vertrag','Keine Prozessmessung'],
  'action':['ERGEBNISMELDUNG','Ergebnis gemeldet','task-1 · ordinal 3','Wirkung unbekannt']
 }:{
  'agent-a':['TESTAGENT','Koordinator A','Registrierte Testidentität','Identität belegt'],
  'identity':['IDENTITÄTSNACHWEIS',null,'Test-CA · Schlüssel A-01',null],
  'authority':['AUTHORITY','Testauftrag J-024','Dateischreibzugriff · Testziel','Aussteller: Test-Controller'],
  'agent-b':['DELEGIERTER AGENT','Ausführender B','A → B · Annahme signiert','Scope eingegrenzt'],
  'process':['PROZESSINSTANZ','python3.12','PID 8421 · Instanz #03','Kernelzuordnung belegt'],
  'action':['HANDLUNG','Datei schreiben','Testziel · Objekt #17','Beobachtet']
 };
 Object.entries(nodeChanges).forEach(([key,values])=>{const node=$(`.node[data-node="${key}"]`);['.node-kind','.node-title','.node-meta','.node-state'].forEach((sel,i)=>{const t=node.querySelector(sel);if(t&&values[i]!=null)t.textContent=values[i];});});
 $$('.node .status-good').forEach(c=>c.style.fill=isMaster()?'var(--faint)':'var(--ok)');
 $$('.links .verified').forEach(p=>{p.style.stroke=isMaster()?'var(--ghost)':'var(--line)';p.style.strokeDasharray=isMaster()?'4 5':'';p.style.markerEnd=isMaster()?'none':'';});
 $$('.edge-labels text').forEach((t,i)=>{if(i<4)t.textContent=isMaster()?['kein Nachweis','task_key','kein Nachweis','kein Nachweis'][i]:['bezieht sich auf','delegiert','gebunden','beobachtet'][i];});
 $$('.node[data-node="agent-c"],.node[data-node="unknown"],.node[data-node="unproven-action"],.links [data-chain="partial"]').forEach(n=>n.style.display=isMaster()?'none':'');
 $$('.edge-labels text').slice(4).forEach(n=>n.style.display=isMaster()?'none':'');
 $('#graph-count').textContent=isMaster()?'3 synthetische Meldungen · keine Live-Daten':'3 von 12 Agenten im Fokus';
 $('#activity-rate').textContent=isMaster()?'Kein Ereignistakt oder Parallelitätsnachweis im Vertrag':'248 Ereignisse / 15 Min. · 0,28 / s im Mittel · max. 3 parallele Prozesse';
 $('.activity-panel').hidden=isMaster();
 $$('.sidebar nav button span').forEach(s=>s.hidden=isMaster());
 selectNode(isMaster()?'action':selected);fit();
}
$$('.node').forEach(n=>{n.addEventListener('click',()=>selectNode(n.dataset.node));n.addEventListener('keydown',e=>{if(['Enter',' '].includes(e.key)){e.preventDefault();selectNode(n.dataset.node);}if(['ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();const nodes=$$('.node').filter(x=>getComputedStyle(x).display!=='none');nodes[(nodes.indexOf(n)+(e.key==='ArrowRight'?1:nodes.length-1))%nodes.length].focus();}});n.addEventListener('contextmenu',e=>{e.preventDefault();selectNode(n.dataset.node);openSheet('Kontextaktionen',`<p class="sheet-copy">${selections[n.dataset.node]?.[1]||'Auswahl'}</p><button class="small-button" data-context="focus">Kette fokussieren</button><br><button class="small-button" data-context="raw">Rohdaten im Inspector</button><p class="sheet-note">Spätere native Aktionen: Nachweisreferenz kopieren, Quelle im Finder zeigen, minimierten Bericht exportieren.</p>`);$$('[data-context]').forEach(b=>b.onclick=()=>{$('#sheet').close();if(b.dataset.context==='raw')setTab('raw');else fit();});});});
$$('.activity-panel tr[data-select]').forEach(r=>{r.onclick=()=>selectNode(r.dataset.select);r.onkeydown=e=>{if(e.key==='Enter')selectNode(r.dataset.select);};});
$$('[data-tab]').forEach(b=>b.onclick=()=>setTab(b.dataset.tab));
$('#theme').onclick=()=>{const light=document.documentElement.dataset.theme!=='light';document.documentElement.dataset.theme=light?'light':'dark';$('#theme').setAttribute('aria-label',light?'Dark Mode wechseln':'Light Mode wechseln');};
$('#scenario').onchange=updateMode;
$('#sidebar-toggle').onclick=()=>document.body.classList.toggle('no-sidebar');
$('#inspector-toggle').onclick=()=>document.body.classList.toggle('no-inspector');
$('#close-inspector').onclick=()=>document.body.classList.add('no-inspector');
$('#zoom-in').onclick=()=>zoom(.15);$('#zoom-out').onclick=()=>zoom(-.15);$('#fit').onclick=fit;$('.minimap').onclick=fit;
$('#search').oninput=e=>{search=e.target.value.trim().toLocaleLowerCase('de');applyFilter();};
$('#filter').onclick=()=>{statusFilter=statusFilter==='all'?'partial':statusFilter==='partial'?'complete':'all';applyFilter();};
$('#stage').addEventListener('pointerdown',e=>{if(e.target.closest('.node,.minimap'))return;dragging={x:e.clientX,y:e.clientY,origin:{...offset},pointer:e.pointerId};$('#stage').setPointerCapture(e.pointerId);$('#stage').classList.add('dragging');});
$('#stage').addEventListener('pointermove',e=>{if(!dragging)return;const ratio=1030/$('#authority-graph').getBoundingClientRect().width;offset={x:dragging.origin.x+(e.clientX-dragging.x)*ratio,y:dragging.origin.y+(e.clientY-dragging.y)*ratio};applyTransform();});
$('#stage').addEventListener('pointerup',()=>{dragging=null;$('#stage').classList.remove('dragging');});
$('#stage').addEventListener('pointercancel',()=>{dragging=null;$('#stage').classList.remove('dragging');});
$('#stage').addEventListener('wheel',e=>{e.preventDefault();if(e.ctrlKey||e.metaKey)zoom(e.deltaY>0?-.08:.08);else{offset.x-=e.deltaX;offset.y-=e.deltaY;applyTransform();}},{passive:false});
$('#chain-mode').onclick=()=>{$('#chain-mode').classList.add('selected');$('#all-mode').classList.remove('selected');fit();$('#graph-count').textContent=isMaster()?'3 synthetische Meldungen · keine Live-Daten':'3 von 12 Agenten im Fokus';};
$('#all-mode').onclick=()=>{$('#all-mode').classList.add('selected');$('#chain-mode').classList.remove('selected');openSheet('Große Graphen · Laufübersicht',`<p class="sheet-copy">Die native Laufübersicht gruppiert zuerst nach Lauf, Agent und Delegationszweig. Auswahl eines Clusters öffnet dessen Ketten; die Positionen bleiben beim Eintreffen neuer Ereignisse stabil.</p><div class="permission-row"><div><strong>Übersicht</strong><p>Cluster mit Agentenzahl, vollständigen und offenen Ketten. Keine tausenden Einzelknoten auf einmal.</p></div><span class="badge">500 sichtbare Knoten als Startbudget</span></div><div class="permission-row"><div><strong>Nahansicht</strong><p>Selektion zeigt Elternkette, Delegierte und verbundene Prozesse. Nachladen verändert den Kontext nicht. Alles Ausgeblendete wird gezählt.</p></div></div><div class="permission-row"><div><strong>Semantischer Zoom</strong><p>Übersicht: Cluster. Mittlere Stufe: Name, Typ, Status. Detail: Prozessinstanz, Scope und Evidence. Dieselbe Information bleibt im Inspector erreichbar.</p></div></div><p class="sheet-note">Diese Aggregation ist eine Entwurfsentscheidung. Im Prototyp ist nur der gezeigte Ausschnitt navigierbar.</p>`);};
$('#host').onclick=()=>openSheet('macOS-Testhost einrichten',`<p class="sheet-copy">Der Testhost führt kontrollierte Testprozesse aus und prüft die Voraussetzungen im tatsächlich ausführenden App-, Helper- und Erweiterungskontext. Die Beobachtung bewilligt oder blockiert keine Agentenhandlungen.</p><div class="permission-row"><div><strong>1 · Endpoint-Security-Entitlement</strong><p>Für den Collector bei Apple beantragen. Keine Benutzerfreigabe kann ein fehlendes Entitlement ersetzen.</p></div><span class="badge warning">Apple-Freigabe offen</span></div><div class="permission-row"><div><strong>2 · Systemerweiterung aktivieren</strong><p>Signierte App in /Applications. Installation über OSSystemExtensionRequest; macOS fordert die Zustimmung an.</p></div><span class="badge unknown">Nicht installiert</span></div><div class="permission-row"><div><strong>3 · Vollzugriff für den Collector</strong><p>Benutzer erteilt Vollzugriff auf Festplatten in den Systemeinstellungen. ES prüft den tatsächlichen Client über es_new_client.</p></div><span class="badge unknown">Nicht geprüft</span></div><div class="permission-row"><div><strong>4 · Beobachtungskanal qualifizieren</strong><p>A schreibt, B bleibt untätig, C schreibt anderes Ziel, Kindprozess schreibt, falscher PID-Claim, zwei aufeinanderfolgende Writer. Instanz-, Objekt-, Lifecycle- und Verlustkontrollen separat ausweisen.</p></div><span class="badge unknown">Nicht ausgeführt</span></div><div class="permission-row"><div><strong>Weitere fallbezogene Freigaben</strong><p>Ordnerzugriff für Eingaben; Bedienungshilfen für UI-Tests; Automation je Ziel-App; Bildschirmaufnahme nur für visuelle Nachweise. Die App fordert diese beim jeweiligen Test an.</p></div><span class="badge">Bei Bedarf</span></div><p class="sheet-note">Harte Grenzen: SIP und geschützte Prozesse, fehlende Provider-Attestierung, Beobachtungslücken, nicht bewiesene Dauerhaftigkeit eines Writes. Vollzugriff oder Adminrechte beheben diese Grenzen nicht pauschal.</p>`);
$('#coverage-button').onclick=()=>selectNode('evidence');
$('#evidence-open').onclick=()=>isMaster()?openSheet('Heutiger Produktvertrag',`<p class="sheet-copy">agent-authority-observation-v1 → Snapshot → agent-authority-observation-report-v1. Source, Entry, Diagnostic und Snapshot sind die vorhandenen unveränderlichen Modelle.</p><pre>Entry: identifier, ordinal, kind, reported_actor_type, task_key, file_sha256</pre><p class="sheet-copy">Keine Identity-, Authority-, Delegations-, PID- oder Kernelereignisfelder. Die neutrale Berichtsausgabe und ihre Begrenzungen bleiben die erste lesende Schnittstelle zur bestehenden Engine.</p>`):openSheet(isPartial(selected)?'Nachweislücke C-025':'Evidence E-108',`<p class="sheet-copy">${isPartial(selected)?'Gelesen wurde eine Übergabe-/Ergebnismeldung. Der Annahmebeleg und das unabhängige Prozess-Handlungsbinding fehlen.':'Im Zielbild referenziert der Inspector das ursprüngliche Collector-Ereignis, das Prozessbinding, den signierten Auftrag und den Prüfbericht.'}</p><pre>${$('#raw-data').textContent.replaceAll('&','&amp;').replaceAll('<','&lt;')}</pre><p class="sheet-note">Dies sind synthetische Entwurfsdaten. Es existiert kein neuer verifizierter macOS-Testlauf.</p>`);
$('#export').onclick=()=>{const blob=new Blob([$('#raw-data').textContent+'\n'],{type:'application/json;charset=utf-8'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='agent-authority-entwurfsdaten.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
$('#scope').onclick=()=>openSheet('Beobachtungsraum',`<p class="sheet-copy">AA-042 ist ein synthetischer, lokaler Beispieldatensatz für das UI. Kein Terminal oder externer Store ist angeschlossen.</p><div class="permission-row"><div><strong>Spätere Auswahl</strong><p>Lokale Beobachtungsquelle, kontrollierter Testlauf oder importiertes Evidence-Paket. Quelle, Host, Zeitfenster, Vertrauensanker und Aufnahmegrenzen bleiben sichtbar.</p></div></div><p class="sheet-note">Die App bleibt ein eigenständiges Agent-Authority-System. Andere Systeme werden später über getrennte Adapter angebunden.</p>`);
$('#settings').onclick=()=>openSheet('Darstellung & Bedienung',`<p class="sheet-copy">Native Zielfassung: Systemdarstellung, Light oder Dark. Schrift und Auswahlgrößen folgen macOS. Kein permanenter GPU-Effekt.</p><div class="permission-row"><div><strong>Tastatur</strong><p>⌘F sucht · Tab erreicht Knoten · Pfeiltasten wechseln Knoten · Enter wählt aus · +/− zoomt · 0 passt ein · Esc schließt den Dialog.</p></div></div><div class="permission-row"><div><strong>Graphnavigation</strong><p>Hintergrund ziehen oder mit dem Trackpad verschieben. ⌘/Ctrl + Scrollen zoomt. Rechtsklick öffnet Kontextaktionen. Miniatur stellt den Ausschnitt zurück.</p></div></div><p class="sheet-note">Der Prototyp läuft im Browser. Einige Browser können ihre eigenen Tastaturkürzel abfangen; die native App bekommt eigene Menübefehle.</p>`);
const navDescriptions={agents:'Agenten und gemeldete Actor-Typen getrennt anzeigen. Identitätsanker, Schlüssel, Registrierungsquelle, Providerbindung und verbundene Prozessinstanzen untersuchen.',delegations:'Sender, Empfänger, Auftragsscope, Elternreferenz, Annahme, Ablauf und Vollständigkeit vergleichen. Eine gemeldete Übergabe ist keine bewiesene Delegation.',actions:'Beobachtete Kernelereignisse nach Prozessinstanz, Objekt, Typ und Zeitfenster filtern. Gemeldete Ergebnisse stehen in einer gesondert gekennzeichneten Ansicht.',evidence:'Quellenreferenzen, Dateifingerprints, Signaturen und Prüfberichte öffnen. Menschliche Erklärung zuerst, minimierte Rohdaten auf Abruf.',findings:'Nachweislücken, Widersprüche, Aufnahmegrenzen und gemessene Ereignisverluste nach Ursache gruppieren. Kein Ergebnis ohne Messung als null ausgeben.'};
$$('[data-nav]').forEach(b=>b.onclick=()=>{if(b.dataset.nav==='overview'||b.dataset.nav==='graph'){$$('[data-nav]').forEach(x=>x.classList.toggle('active',x===b));document.body.classList.toggle('overview',b.dataset.nav==='overview');if(b.dataset.nav==='overview')toast('Übersicht: Kennzahlen und derselbe Untersuchungsraum.');return;}openSheet(b.textContent.replace(/\d+/g,'').trim(),`<p class="sheet-copy">${navDescriptions[b.dataset.nav]}</p><p class="sheet-note">Diese Bereiche sind Teil der Informationsarchitektur; in dieser Entwurfsphase wird keine vollständige App implementiert.</p>`);});
$$('[data-metric]').forEach(b=>b.onclick=()=>{if(b.dataset.metric==='chains'){selectNode('agent-c');statusFilter='partial';applyFilter();}else if(b.dataset.metric==='actions')selectNode('action');else if(b.dataset.metric==='agents')selectNode('agent-b');else selectNode('authority');});
$('#activity-all').onclick=()=>openSheet('Systemhandlungen im Lauf',`<p class="sheet-copy">Geplante Tabellenansicht: Zeit, Handlungstyp, Objektidentität, ausführende Prozessinstanz, Agentenzuordnung, Kettenstatus und Evidence. Auswahl fokussiert denselben Nachweis im Graphen.</p>`);
$('#sheet-close').onclick=()=>$('#sheet').close();
document.addEventListener('keydown',e=>{if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='f'){e.preventDefault();$('#search').focus();}if(e.key==='Escape'){$('#toast').hidden=true;if($('#sheet').open)$('#sheet').close();}if(e.target.matches('input,select,textarea')||$('#sheet').open)return;if(e.key==='+'||e.key==='=')zoom(.15);if(e.key==='-')zoom(-.15);if(e.key==='0')fit();});
if(new URLSearchParams(location.search).get('theme')==='light')document.documentElement.dataset.theme='light';
selectNode('action');applyTransform();
