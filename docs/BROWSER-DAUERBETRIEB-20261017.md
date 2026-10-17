# Agent Authority / Hilfezentrum · Dauerbetrieb 17.10.2026

**Fortsetzung läuft. Noch kein Aktivierungsurteil.** Dieser Bericht wird vor dem
Abschluss um tatsächliche Quellpins, Aktivierung und gezielte Belege ergänzt.
Der bestätigte Auftrag vom 17.10. autorisiert den getrennten Dienst und die
Hilfezentrum-Verbindung. Frühere Deploymentverbote gelten für frühere Läufe.
Kein Push, Merge, Sichtbarkeitswechsel oder Social-Beitrag ist beauftragt.

Der gesicherte Zwischenstand wurde gegen alle sechs SHA-256 im Manifest der
Übergabe `fortsetzung-20261017T111828Z` abgeglichen: identisch. Vor Fortsetzung
war `agent-authority-browser.service` auf Debian nicht installiert. Ein eigener
Hilfezentrum-Integrationsworktree existierte bereits auf `2befbe0`; dessen
Änderungen werden übernommen. Builderworktree und eingefrorene Grok-Prüfkopien
bleiben erhalten. Laufende Reviews werden nicht als fertige Urteile ausgegeben.

## Betriebsgrenzen und vorhandener Weg

Vorhanden sind Debian 13 / Python 3.13.5, Docker-Caddy mit bestehendem Zertifikat
für `v2202608211799501333.goodsrv.de`, der Hilfezentrum-APIweg unter
`/ki-hilfezentrum/` und die separate öffentliche Hilfezentrum-Origin
`https://ki-hilfezentrum.netzwerkpunkt.de`. Der vorhandene `/sites`-Mount erlaubt
einen privaten Unix-Socket ohne Dockerneustart oder neue Portfreigabe.

AA verwendet eine eigene unprivilegierte UID `aa-browser`, private Statepfade,
eigene Releases und eine eigene isolierte Runtime aus den bereits qualifizierten
Gunicorn-/packaging-Bytes der Hilfezentrum-Runtime. Hilfezentrum-Runtime und
`/opt/ki-helper-runtime` werden dabei nicht verändert. Die Pythonquellen liegen
außerhalb des Webroots. Graphprojektion und Layout bleiben im Browser.

Das HTTPS-Profil erwartet feste Origin, festen unverändert weitergereichten
Prefix und privaten Proxytransport. Forwarded-Header begründen weder Identität
noch TLS oder Autorität. Der Proxy überschreibt `X-AA-Proxy-Token`; ohne diesen
Zugang und AF_UNIX-Socket scheitert der Backendzugriff. Das bestehende lokale
Loopbackprofil bleibt ein gesondertes Prüfprofil.

AA bleibt **single-instance-local-synthetic**: genau ein synchroner Worker,
ein Thread, POSIX-StateLease, lokale SQLite-Datei, Prozesssitzungen. Keine
geteilten Mehrserverzustände. Sitzungen werden bei Stop/Neustart verworfen;
Scopes, Quoten, Eigentümerfilter und CSRF bleiben serverseitig.

## Produktverbindung und Restvertrag

Im Hilfezentrum wird ein verständlicher DE/EN-Einstieg sowie ein kontextbezogener
Authority Graph aus bereits vorhandenen Vorgangs-/Zuordnungswerten ergänzt.
Die vorhandene Kontoprüfung begrenzt die Auswahl auf berechtigte Eigentümer oder
zugeordnete Beteiligte. Die Projektion verwendet nur IDs, gespeicherte Zustände,
Revisionen und vorhandene Zeiten; keine zweite vollständige Datensammlung.
Der Rückweg führt zur vorhandenen ausgewählten Anzeige.

Die reale Übergabe an AA prüft zunächst Anmeldung, Eigentümer-/Beteiligtenbezug
und CSRF. Sie bleibt mit `authority_identity_contract_missing` geschlossen.
Der private AA-Verbindungstest ist separat beschriftet, verwendet eine feste
synthetische Fixture und erfordert die eigene synthetische AA-Anmeldung.
Eine Hilfezentrum-E-Mailkontrolle wird nicht als Agentenidentität ausgegeben.

Kleinste noch benötigte Produktentscheidung ist ein verbindlicher Betreiber-
und Identitätsvertrag: zuständiger AA-Aussteller/Audience und die erlaubte
Zuordnung der bestehenden Hilfezentrum-Konto-/Zuordnungs-ID zu AA-Subject,
Tenant/Owner, Source/Job/Adapter einschließlich Ablauf und Widerruf. Ohne diesen
Vertrag dürfen reale IDs nicht als AA-Berechtigung übertragen werden. Für
reale Daten folgen zusätzlich Quelle/Verifier/Schlüsselpin und Aufbewahrung;
der Reportdownload begründet keinen Vertrauensanker.

## Stand der Arbeit

| Punkt | Status | Nächster Schritt |
| --- | --- | --- |
| Snapshot / Vorinstallation | geprüft | Beleg im Abschluss pinnen |
| HTTP-/Proxy-/Kontextcode | gezielte lokale Checks bestanden | Quellcommit / Lieferhash |
| Eigener Dienst und Zugang | vorbereitet | Installation / Start-Stop-Neustart |
| Hilfezentrum-Verbindung | eigener Integrationsworktree | enge Tests / koordinierte Übernahme |
| Echte Identität / Quellen | gesperrt | obigen Vertrag festlegen |
| Collector / Fremdaktionen | unverändert gesperrt | keine Aktion in diesem Auftrag |

Alle SSH-/Debianaktionen erfolgen durch den gemeinsamen Exklusivstarter
`/Users/landjunge/agent-bridge/queues/gesamtabschluss-20261017T084846Z/with-debian-lock.py`.
Eigene neue Dienst-/Prüfprozesse teilen die Slicegrenze 800 MiB / 40 % CPU /
Swap 0; höchstens ein Laborrunner. Bestehende Dienste erhalten ihre Limits.
