# Browserdienst: vorhandene Daten- und Dienstverträge

Inventur vom 17.10.2026, ausschließlich lesend. Basis dieses eigenen Worktrees:
`22c4ee9fc479bb6a3df98fcbd786b0f5a7c9fe9b`. Fremde Worktrees, Konfiguration,
Schlüssel, Konten und produktive Daten wurden nicht übernommen oder verändert.
Diese Inventur gibt keinen Collector, Runner oder produktiven Anschluss frei.

## Bestehende Python-Engine und Produktbericht

`agent_authority/observations.py` definiert die unveränderlichen `Source`,
`Entry`, `Diagnostic` und `Snapshot`. `agent_authority/report.py:build_report`
analysiert ausschließlich diesen neutralen Snapshot. `json_source.py` und
`whiteboard.py` sind getrennte lesende Eingangsadapter; der ThreadDesk-Adapter
ist keine Voraussetzung für das Produkt. Die Browserfassung verwendet dieselbe
Engine, keine Nachbildung ihrer Auftragsanalyse.

| Vertrag | Tatsächlicher Umfang | Browser-/Serververwendung |
|---|---|---|
| `agent-authority-observation-v1` | Eine JSON-Datei je Eintrag: `id`, `source_id`, `ordinal`, `kind`, `reported_actor_type`, optional `task_key`; unbekannte Inhalte werden minimiert | Operatorseitig einem erlaubten Quellenverzeichnis zuordnen und durch `read_observations` lesen |
| `agent-authority-observation-report-v1` | `role=observer_only`; `source`, `summary`, `tasks`, `recent_entries`, `warnings`, `display` | Kennzahlen und Graph aus dem vorhandenen Bericht projizieren; keine Identität oder Wirkung daraus ableiten |
| `agent-authority-ui-graph-v1` | Darstellungsschema aus `AuthorityCore/Models.swift`: Knoten, Fakten, Kanten, Belegreferenzen | Gemeinsame Darstellung, kein zusätzlicher Bericht oder Herkunftsnachweis |
| `aa-report-v1` im `aa-private-v1`-GET | Anderes, signiertes und befristetes Privatdienstschema | Ausschließlich über den expliziten unten beschriebenen Adapter; niemals als neutralen Beobachtungsbericht ausgeben |

Die Engine ordnet Beiträge nur über ihre gemeldete Aufgabenkennung zu, vergibt
lokale Aliase und zählt gemeldete Arten. Eine Übernahme ohne späteren Ergebnisbeitrag
ist ein Hinweis auf den gelesenen Verlauf, kein Laufstatus. Gleiche Ordinals machen
die letzte Meldung und den ausstehenden Ergebnisbeitrag betroffener Aufgaben
unbekannt. `source_authenticated=false`, Identität/Wirkung/Gesamtabdeckung
`UNBEKANNT`, `task_completion_proven=false` und `rights_inherited=false` bleiben
erhalten. Anzeigegrenze 1–100, mit getrennten Ausblendungszählern.

Der vorhandene Dateileser `file_reader.py` begrenzt zwei Verzeichnisscans auf je
10.001 beobachtete Namen, übernimmt höchstens 10.000 Namen/JSON-Dateien, liest
höchstens 65.536 Bytes je Datei und 8 MiB Rohbytes insgesamt. Er verfolgt keine
Eintragssymlinks/FIFOs, prüft Dateisignaturen/Verzeichnisidentität und verwirft
doppelte JSON-Schlüssel/nicht endliche Zahlen. Bei Grenzen/Fehlern bleibt der
Bericht unvollständig. Das ist kein atomarer Snapshot und kein allgemeines
Dateisystem-Zeitlimit. Grundlage: `docs/PRODUCT-OBSERVATION-CONTRACT.md`,
`tests/test_product_contract.py`, `tests/test_product_input_bounds.py`.

## Vorhandener Linux-Prüfdienst

Lesend gefunden im eigenen fremden Entwicklungsstand
`/Users/landjunge/agent-authority-lab/.worktrees/hosted-qualification`,
Commit `2b7cd79e29ffb1e041906f1076de610d75fa8b21` zum Inventurzeitpunkt:

- `docs/PRIVATE-SERVICE-API-v1.md`, `docs/PRIVATE-SERVICE-OPENAPI-v1.json`:
  HTTP-/Signatur-/Mandantenvertrag.
- `research/private_service/http.py`, `service.py`, `verifier.py`, `retention.py`,
  `boundary.py`: tatsächlich implementierte Abruf-/Berichts-/Fristverträge.
- `docs/private-service-debian-20261017/README.md`, `research/debian_private/`:
  Debian-Adapter und begrenzter Nachweis für `a4-write16-v1`.

Der dokumentierte private Dienst bindet ausschließlich `127.0.0.1:8765`. Alle
Datenrouten benötigen einen operatorseitig zugeordneten Bearer-Testtoken.
Mandant, Rolle und Objekt-Subjects werden serverseitig geprüft; fremde/nicht
vorhandene Aufträge ergeben 404. `GET /v1/jobs/{id}` liefert Zustand,
`GET /v1/jobs/{id}/report` einen verfügbaren Bericht. Bericht ausstehend: 409;
nach Zugriffssperre: 410. Kein Listenabruf und keine Browser-SSO-Schnittstelle
sind damit zugesagt. Auch GET kann vorhandene Fristwartung auslösen; deshalb
wurde im Rahmen dieser Inventur kein produktiver Dienstabruf vorgenommen.

Die GET-Berichtsantwort hat die tatsächliche Form:

```json
{
  "schema": "aa-private-v1",
  "report": {"body": {"schema": "aa-report-v1"}, "signature": "BASE64"},
  "current_key_status": {"actor-key-id": "active"},
  "completed_at": "UTC", "expires_at": "UTC", "report_version": "1",
  "report_sha256": "SHA256", "receipt_state": "unconfirmed",
  "received_at": null, "access_state": "available", "deletion_reason": null,
  "cleanup_state": "...", "cleanup_completed_at": null,
  "cleanup_confirmed": false, "content_key_state": "present",
  "inputs_cleanup_completed_at": "UTC", "residual_expires_at": null,
  "cleanup_scope": "..."
}
```

Das Ausschnittsobjekt `body` oben ist keine vollständige gültige Fixture. Der
echte Body verlangt Domain `AA-REPORT-v1`, Audience `aa-private-local-v1`,
`signing_kid`, `tenant`, 32-stellige kleine Hex-`job_id`, Klassifikation,
Prüfer-/Trustkatalogversion, Zeit/Fristen, Umfang `controlled-a4-write16`,
`provider_model_session=UNBEKANNT`, Unsicherheiten und `grants_rights=false`.
Der vollständig gemessene Bericht benennt Auftrags-/Annahmedigest, Quellenpins,
28 Checks, 23 Verlustwerte und vier getrennte Ebenen. Ein Unknownbericht enthält
stattdessen `reason` und `sources=[]`; fehlende Messketten werden nicht erfunden.
`current_key_status` und Lifecycle-Metadaten gehören zum heutigen Außenobjekt,
werden von der historischen Berichtsignatur nicht gedeckt und dürfen den
historischen Body nicht verändern.

Signatur: bestehendes A2-Envelope `{body,signature}`, Ed25519, Standard-Base64
mit 64 Signaturbytes. Unterzeichnet wird der vollständige Body im vorhandenen
eingeschränkten ASCII-/Integer-JCS-Vertrag. Der Reportpublickey muss getrennt
gepinnt sein; ein Schlüssel im Ergebnisdownload ist kein Vertrauensanker.
Auch eine gültige Signatur beweist nur diese Reportbytes unter den benannten
Trustannahmen, keine Provider-/Modellidentität oder allgemeine Sicherheit.

Der letzte dokumentierte Debianstand hat Runner/Collector beendet, den
Collector-Socket geschlossen, Hardstop gesetzt und die Collector-Testidentität
stillgelegt. Diese Grenzen bleiben bestehen. Der Browserdienst startet keinen
Collector, keinen Prüflauf und keine automatische Wiederholung.

Der tatsächliche Debian-Code wurde am 17.10.2026 zusätzlich über SSH-Alias
`netcup` rein lesend überprüft: nur die fünf folgenden öffentlichen Quelldateien,
ihre SHA-256 und gezielte Schema-/Importzeilen. Keine Konfiguration, Schlüssel,
Laufberichte oder produktiven API-Routen wurden abgerufen. Alle fünf Hashes
stimmten mit dem oben benannten lokalen Referenzstand überein.

| Datei unter `/opt/aa-private/` | SHA-256 | Vertragsstelle |
|---|---|---|
| `research/debian_private/api.py` | `a0a5904cc02b622fc0387bac0211d0b1de703cc74d41127bfe55d3110218dd67` | Zeilen 11/14 importieren denselben HTTP-Server und `private_service.Service` |
| `research/debian_private/components.py` | `638e8d4493fc8841d6f3c708bebb8086f54dc2665cd0c851ccb4d091e3955106` | Zeilen 9/65 importieren/verwenden dieselbe `report_policy` |
| `research/private_service/service.py` | `fe06d4c628e050625508c6241a84025788b39cc929afa90231a4084ed317fd67` | Zeilen 591/592: `aa-report-v1`, `AA-REPORT-v1`; Abruf in Zeile 611 |
| `research/private_service/verifier.py` | `c591128646b6bb429f64a9c36cab3f1d51b5f86a78fb48d003f17302a432086d` | Zeilen 64/65: `aa-report-v1`, `AA-REPORT-v1` |
| `research/private_service/boundary.py` | `aa03b5b0e5b02f92a81fb88534f8e99cb7463c231e5ea1581f0011093d936a58` | Zeilen 103/104: tatsächlich zugelassenes Berichtsschema und Domain |

Ein separates `aa-debian-report-v1` ist in diesen aktiven Berichtswegen nicht
definiert. Die `aa-debian-single-qualification-v1` und
`aa-debian-completed-same-fresh-job-v1` aus den einmaligen Qualifikationsskripten
sind Versuchs-/Abschlussprotokolle, keine GET-Berichtsformate. Die vorhandenen
`prepare-host.json` und `source-upload-final*.json` sind Installations- bzw.
Uploadmetadaten, ebenfalls keine Berichtsverträge. Der implementierte Adapter
passt damit zum nachgewiesenen heutigen Debian-GET-Vertrag; er verspricht keine
allgemeine Verarbeitung beliebiger Linux-/Qualifikationsprotokolle.

## Implementierter rein lesender Anzeigeadapter

`agent_authority/browser_adapter.py:adapt_private_report(data, source_id, job_id)`
akzeptiert ausschließlich bereits serverseitig autorisiert bereitgestellte
GET-Antwortdaten. Er hat keine Netz-, Shell-, Crypto-, Collector- oder
Privatdienstimporte und liest keine Dateien. IDs müssen aus der Operatorzuordnung
stammen; die Formatprüfung eines passenden `job_id` ersetzt keine Kontorechte.
Rohes JSON muss der aufrufende Server mit Duplicate-Key-/Bytegrenzen lesen.

Der Adapter prüft die getrennten Schema-/Domain-/Audience-/Feldverträge, die
Auftragskennung, Rechte-/Providergrenzen und die 64-Byte-Base64-Signaturform.
Er begrenzt zusätzlich auf 64 KiB, 4.096 Werte, 12 Ebenen, 128 Listenelemente
und 2.048 druckbare ASCII-Zeichen pro String. Dies ist ein enger Anzeigeadapter;
größere ansonsten mögliche Dienstberichte werden ausdrücklich abgewiesen.

Rückgabe:

- `graph`: `agent-authority-ui-graph-v1`, Auftrags-/Berichts-/Ebenenknoten mit
  den passenden Digestreferenzen. Jede Kette und jeder Knoten bleibt `unknown`.
  `BELEGT` aus fremdem Body ist ausschließlich eine gemeldete Klassifikation.
- `metadata`: `signature_verification=UNBEKANNT`,
  `production_integration=blocked`, konkrete fehlende Bindungen und Digest des
  vollständigen Envelopes. Ein Digest ersetzt keine Signaturprüfung.
- `privateReport`: eindeutig bezeichnete, minimierte `aa-private-v1`-Projektion,
  Originalvertrag `aa-report-v1` im Body, Signatur ausdrücklich ausgelassen.
  Heutiger Keystatus und Lifecycle bleiben separat als gemeldete Werte.
  Diese Projektion ist kein signiertes Original und kein Download zur
  unabhängigen Signaturprüfung. Keine rohen Registry-/Capture-/Trialdaten.

Alle Texte bleiben JSON-Daten und müssen in der Oberfläche über `textContent`
oder gleichwertige HTML-Escapierung erscheinen. Der Adapter erzeugt kein HTML.
Er authentisiert keine synthetische Herkunft aus einem frei gelieferten Claim;
die umgebende isolierte Demoquelle muss ausdrücklich als synthetisch markiert
sein. `browser_adapter.py:synthetic_private_response(job_id, tenant, measured=...)`
konstruiert eine eigene vollständige GET-Fixture mit synthetischen IDs/Checks
und 64 Nullbytes als bewusst ungültiger Signatur. Die zwei Berichtsvarianten
werden in `tests/test_browser_adapter.py` geprüft. Kein vorhandener echter
Bericht wurde kopiert. Die feste historische Beispielzeit behauptet weder
heutige Abrufbarkeit noch Frische.

Produktionsanschluss bleibt gesperrt: separat gepinnte Signaturprüfung,
authentisierte Konten-/Mandanten-/Auftragszuordnung und freigegebene
Betreiberkonfiguration fehlen. Diese Fassung erfindet keinen Verifier oder
Nachweismechanismus, um die Lücken zu überdecken.

## KI-Hilfezentrum und vorhandene Runtime

Lesende Referenz: `/Users/landjunge/Projects/ki-hilfezentrum`, Commit
`1fdccc10d65dd2fc51e8948a8534b5fd08c233ab` zum Inventurzeitpunkt. Dort bestehen
eigene uncommittete/unversionierte Arbeiten; sie wurden nicht übernommen.
`HUMAN-ACCESS.md`, `human_auth.py` und `app.py` belegen:

- Botzugang mit persönlichem Bearertoken und `GET /api/account` ergibt
  `bot_id,name`; IDs sind keine Credentials oder verifizierte Identitäten.
- Menschenzugang mit E-Mail-Einmalcode und serverseitigem Sitzungshash;
  hostgebundenes `__Host-kh-session`, Secure/HttpOnly/SameSite=Lax, sieben Tage.
  Browser-Mutationen brauchen Sitzung/CSRF und die feste Hilfezentrum-Origin.
- Der private PHP-Relay hat eine feste Routen-/Cookie-Allowlist. Es gibt hier
  keinen belegten OIDC-/OAuth-Audience-/AA-Sessionaustausch, keine automatische
  Zuordnung zu privaten AA-Mandanten und keinen AA-Berichtsbesitzvertrag.

Deshalb werden weder Sessioncookie noch Bridge-Schlüssel oder Kontodatenbank
übernommen. Ein späterer Hilfezentrum-Link ist Zugang zum eigenständigen Produkt;
er schafft allein keine gemeinsame Identität oder Architekturfusion.

`helper_tests.py` und `helper_worker.py` belegen `/opt/ki-helper-runtime` als
festen Werkzeugpfad für bestehende begrenzte lokale Helfer (`gojq`, `jd`,
`csv-diff`, `trurl`, synthetisches `hurl`). Diese führen keine Agent-Authority-
Datenerfassung durch und liefern kein neutrales AA-Berichtsschema. Ohne passenden
expliziten AA-Vertrag wird die Runtime deshalb nicht als Collector eingebunden.
Die lokalen Researchdateien `research/a1_linux` bis `a4_*` sind begrenzte
Versuchs-/Prüfmechanismen, keine allgemein freigegebene Browser-Livebeobachtung.

Der aktuelle Auftrag setzt nur eigene synthetische private Prüfkonten voraus.
Echte Hilfezentrum-Konten, echte Daten und öffentliche Bereitstellung bleiben
getrennte spätere Schritte. D-012 bleibt für alle Adapter unverändert.
