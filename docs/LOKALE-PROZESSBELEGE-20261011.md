# Lokale Prozessbelege und Herkunftsdiagnose

WB1651/1652 geben nach der Machbarkeitsprüfung WB1647–1650 die minimale
Umsetzung frei. D-012 gilt: beobachten, analysieren, warnen. WB1654 verlangt
den geprüften Kandidaten; WB1655 erlaubt anschließend einen regulären Merge
unter frischen HEAD-/Diff-/Review-/Schutzregelkontrollen, grünen Pflichtchecks
und unabhängiger Grok-Prüfung des tatsächlichen Kandidaten. Diese Bedingungen
sind hier vor dem Kandidatenabschluss dokumentiert, nicht als bereits erfüllt
behauptet. Produktiv-Release und stärkere Nachrichtenbindung bleiben offen.

`python -B scripts/local_process_evidence.py` misst einmalig den lokalen
Beobachter und seinen Elternprozess. Die Ausgabe steht getrennt von der
Wirkungs-/Herkunftsauswertung. Sie liest auf macOS Boot-ID, PID, PPID, UID
und Kernelstartzeit mit Mikrosekunden sowie eine dynamische Codesignatur,
soweit verfügbar. Pfade, argv, Umgebung, Prompt und Inhalte werden nicht
ausgegeben. Es werden keine Eingangs-JSONs oder gespeicherten Belege angenommen.

Das Feld `aussage: BELEGT` innerhalb eines Prozessdatensatzes gilt nur für
die dort beobachteten lokalen Prozessmerkmale. Herkunft und Identität bleiben
auf der getrennten Aussageebene **UNBEKANNT**, `source_authenticated` und
`recht_uebernommen` bleiben falsch. Ein Elternprozess kann mehrere Sitzungen
bedienen; ein signiertes Programm kann fremde Angaben weiterreichen.

Die Signaturabfrage wählt über PID ohne Nachrichten-Audit-Token und ohne
zusätzliches Signer-Requirement. Vorher-/Nachher-Abfragen begrenzen beobachtete
Prozesswechsel, garantieren keine atomare Nachrichten- oder Exec-Bindung.
Eine fehlende Signatur wird als UNBEKANNT dokumentiert, ohne sie aus einem
Dateinamen oder Label zu ersetzen. Plattformen ohne diese macOS-Abfragen
geben UNBEKANNT mit `unsupported_platform` aus. Die Ausgabe ist eine
Momentaufnahme; Kopien authentisieren keine spätere Nachricht.

`assess` erklärt fehlende, alte und gefälschte Eingangsklassen nun auch auf
der Herkunftszeile mit `missing_evidence`, `stale_source`, `forged_source`.
Ungültige Klassen fallen wie bisher auf `forged` zurück. Bei `current`
bleibt `no_source_field`, weil auch eine aktuelle lokale Wirkung kein
Quellenfeld authentisiert. Die Klasse ist eine Diagnose des Eingangs,
kein unabhängig nachgewiesener ursprünglicher Autor. Die bestehenden
Identitätsgründe bleiben passend getrennt. Prozessbelege werden nicht
automatisch als Eingänge in `assess` übernommen.

Apple-Primärquellen: [Prozessfelder und Kernelstart](https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/sys/proc_info.h),
[dynamische Signaturprüfung](https://raw.githubusercontent.com/apple-oss-distributions/Security/main/OSX/libsecurity_codesigning/lib/SecCode.h).
Die ABI folgt den installierten SDK-Headern. Gegenfälle und tatsächliche
Messungen sind getrennt zu kennzeichnen. Historische Archive und
P4/RC/CB-/OOS-021-Grenzen werden durch diese Diagnose nicht geschlossen.
