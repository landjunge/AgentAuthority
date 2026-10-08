# Vorabvertrag: Identität echter lokaler temporärer Dateien

8. Oktober 2026. Ausgangscommit des abgeschlossenen Ressourcen-Epochen-
Papiervergleichs: `eca84266e4d5c52368b5f5f0ca8476dc1a834933`.
Neuer ausdrücklich beauftragter, isolierter Versuch; AA bleibt eigenständiger
Beobachter / Monitor / Analyseebene. Keine Produkt-/Observererweiterung.

## Gelesene Basis und untersuchte Frage

Vor Änderungen vollständig gelesen: Ressourcen-Epochen-Repeat-01-Ergebnis,
Real-Run-Prototyp-Ergebnis, Konsolidierung E1–E7, E3–E7-Bericht,
RESEARCH-METHOD und OUT-OF-SCOPE-DEBT. Die bereits vollständig gelesenen,
unveränderten Quellen sind gegen den Ausgangscommit bestätigt.

**Frage:** Welche vorhandenen lokalen Betriebssysteminformationen können
in diesem begrenzten Test belegen, dass eine Ressource trotz Referenzwechsel
dieselbe geblieben ist oder ersetzt wurde?

Ressource bedeutet hier **dasselbe lebende reguläre Dateisystemobjekt**,
nicht derselbe Pfad, Inhalt, Deskriptornummer oder offene Dateibeschreibung.
Keine persistente Identität nach Schließen/Löschen, über Neustarts, andere
Maschinen, Namensräume oder Netzwerke voraussetzen. Historisches K14 und
die Grenzen vorheriger Papier-/Fake-/Real-Run-Fälle nicht rückwirkend ändern.

## Vorab geprüfte lokale Eigenschaften und Aussagegrenze

Lesende Systemprüfung vor Versuch: Linux 6.18.44; /tmp ist tmpfs;
Python 3.12.14. Python-Dokumentation zu os.stat_result/os.fstat und vorhandene
glibc-Header struct_stat.h bestätigen die verfügbaren Felder st_dev/st_ino.
Keine Testdatei oder Probe wurde dafür vor diesem Freeze erzeugt.

- **st_dev:** native Geräte-/Dateisystemzuordnung des abgefragten Objekts.
- **st_ino:** native Inodenummer innerhalb dieser Dateisystemzuordnung.
- Nur das Paar hat hier eine Bedeutung; Inodenummer allein ist kein globaler
  Schlüssel. Werte sind keine kryptografisch authentisierten Identitäten.
- Abfrage mit **fstat am tatsächlich geöffneten Handle**; keine Behauptung
  allein aus Pfadstatistik, Name, Inhalt, Hash oder Empfangsordnung.
- Beide Handles bleiben vom ersten bis zum zweiten Messpunkt und durch die
  unabhängige Referenzprüfung offen; gleichzeitige Lebendigkeit wird per
  lokalem F_GETFD überprüft. Gleicher Prozess, keine Namespace-/Mountwechsel.

**Wesentliche Einschränkung L2:** Das alte Handle bleibt nach unlink offen.
Dadurch bleibt sein Dateisystemobjekt lebend und seine Inode wird während
dieses Vergleichs nicht durch Freigabe/Wiederverwendung zur Ersatzdatei.
Das ist Teil des kontrollierten Messaufbaus, keine Prüfung ungebundener
Snapshots oder einer Identität über vollständig abgeschlossene Lebenszeiten.
Inodenwiederverwendung nach Freigabe bleibt ungeprüft. Keine Gültigkeit des
Verfahrens für andere Dateisysteme oder reale Fremdressourcen behaupten.

## Festgeschriebene Fälle und Hypothesen

Genau ein neuer privater temporärer Ordner direkt unter /tmp; darin nur
selbst erzeugte Dateien und Messartefakte. Keine Nutzer-/Projektdateien,
Accounts, Secrets, Cloud- oder Netzwerkressourcen. Einmalige Ausführung von:

| Fall | Tatsächliche Operationen | Frage |
|---|---|---|
| L1 | A neu erzeugen; erstes offenes Handle samt fstat erfassen; A nach B umbenennen; B öffnen und fstat erfassen; beide Handles halten | Ist B dieselbe lebende lokale Datei wie zuvor A? |
| L2 | A neu erzeugen; erstes offenes Handle samt fstat erfassen; A unlinken; unter demselben Pfad eine neue Datei erzeugen/öffnen und fstat erfassen; beide Handles halten | Ist die neue Datei trotz gleichen Pfadtexts verschieden? |
| L3 | A neu erzeugen; B als echte Dateikopie mit identischen Bytes erzeugen; beide über offene Handles unabhängig fstat-abfragen und halten | Sind A/B trotz gleichen Inhalts verschiedene Dateien? |

**H1:** Das tatsächlich erhobene native Paar plus begrenzter, gemessener
Lebendigkeits-/Prozessscope erlaubt L1/L2/L3 innerhalb dieses Aufbaus korrekt
zu unterscheiden. Kein Falllabel ist ein Ableitungsbeleg.
**H2:** Pfadgleichheit, Inhaltsgleichheit oder gleicher Inhalts-Hash ohne
native Identitätsinformation tragen keine sichere Identitätsaussage.
Fehlende tragfähige Information führt zu UNBEKANNT.

Diese Hypothesen und Regeln bleiben nach Start unverändert. Kein Wiederholen,
Anpassen eines Fehlfalls oder nachträgliches Reparieren desselben Laufs.
Aufnahme-/I/O-/Referenzfehler unverändert sichern; dann nicht passende Aussage
erfinden, sondern UNBEKANNT/UNBEURTEILBAR und gegebenenfalls INCONCLUSIVE.

## Kleinste notwendige Aufnahme und getrennte Analyse

Zwei ausschließlich fallgebundene Hilfen unter probes/: feste Aufnahme der
drei Fälle und separater lesender Analyst. Notwendig zur reproduzierbaren
fstat-Aufnahme, Trennung der Inhalte/Referenz und Antwortcheckpoint vor Vergleich.
Keine Observermodule importieren/ändern, keine allgemeinen Ressourcensensoren,
freien Ressourcenargumente, Connectoren oder neue ID-/Feldstruktur für ein Produkt.
Vertrag zuerst docs-only committen/pushen; Hilfen separat festschreiben/pushen
und remote bestätigen, bevor irgendeine Testdatei erzeugt wird.

Primärinput je Paar: st_dev und st_ino beider tatsächlich referenzierter
Dateien; boolesche reguläre-Datei-Prüfung; gemessene Überlappung offener
Handles; benannter lokaler Linux/tmpfs-Prozessscope. Zeilenbezeichnungen sind
nur lokale Messreferenzen, keine neue Ressourcen-ID. Keine Fallnamen,
Operationen, Erwartungen, Referenzwerte, Inhalts-/Hash-/Pfaddaten, rohen
Argumente, vollständigen stat-Dumps, UID/GID oder Zeitstempel im Primärinput.

Analyst akzeptiert nur komplette native Paare im genannten Scope. Gleiche
Paare → DIESELBE; unterschiedliche Paare → VERSCHIEDEN. Ohne tragfähige
Identitäts-/Scopeinformation → UNBEKANNT. Keine Ersatzableitung aus anderen
Angaben. Pro Original-/Kontrollinput werden getrennt gespeichert:

A. Sind die beiden Referenzen DIESELBE Ressource, VERSCHIEDENE Ressourcen oder
   ist es UNBEKANNT? Zulässig: DIESELBE / VERSCHIEDEN / UNBEKANNT.
B. Welcher konkrete sichtbare Beleg trägt diese Aussage?
C. Welche Aussage darf daraus ausdrücklich nicht abgeleitet werden?

## Unabhängige Ground Truth ohne native Identitätsableitung

Erst Primärmetadaten aufnehmen; Referenz separat aus tatsächlichen festen
Offset-I/O-Proben über dieselben durchgehend offenen Handles bestimmen.
Keine st_dev/st_ino-Vergleiche, Observerantworten oder Fall-Sollwerte als Wahrheit.

1. Vor jeder Schreibrichtung die tatsächlichen vollständigen Handleansichten
   in flüchtigem Speicher lesen; L3-Inhaltsgleichheit/Hash vorher aufnehmen.
2. Frischen Marker von 64 Bytes über Handle 1 an Offset 0 schreiben, Datei
   auf diese Länge setzen; vollständigen Schreibrückgabewert und eigene
   neue Ansicht prüfen. Handle 2 erneut an Offset 0 lesen.
3. Neue tatsächliche Ansichten nach Schritt 2 als Basis der zweiten Richtung
   erfassen. Marker von 96 Bytes über Handle 2 schreiben; eigenen Vollzug
   prüfen; Handle 1 erneut an Offset 0 lesen.
4. Anfangsdateien sind 32 Bytes lang. Marker unterscheiden sich durch ihre
   Längen garantiert von beiden jeweiligen Voransichten; Zufall allein ist
   kein Nachweis einer Änderung. Markerbytes bleiben ausschließlich transient.
5. Erfolgreiche eigene Writes und übereinstimmende neue Gegenansicht in
   **beiden** Richtungen → DIESELBE. Erfolgreiche eigene Writes und gegenüber
   ihrer jeweils frisch gemessenen Basis unveränderte Gegenansicht in
   **beiden** Richtungen → VERSCHIEDEN. Gemischter Befund, kurzer/fehlgeschlagener
   I/O oder Referenzfehler → UNBEKANNT, keine vermutete Wahrheit.

Archiviert werden nur Operationserfolg, gemessene Längen und Vergleichsbooleans,
kein Payload, keine Marker und keine nativen Identitätspaare in der Referenz.
Die Referenz nutzt kausale Schreib-/Leseeffekte und ist vom getesteten
Metadatenvergleich getrennt; beide vertrauen demselben Kernel/Messprozess.
Keine externe unabhängige Prüfung oder Isolation gegen kompromittierte Quellen.
Temporäre Datenfiles danach schließen/löschen; Rohinhalte nicht archivieren.

## Drei Negativkontrollen, Antwortfreeze und Bewertung

Genau drei reduzierte Datensichten derselben Aufnahme, keine neuen Dateifälle:

- L2: nur tatsächlich gleicher Pfadtext → UNBEKANNT.
- L3: nur gemessener Status gleicher Bytes → UNBEKANNT; keine Inhalte vorlegen.
- L3: nur die beiden tatsächlich gleichen Inhalts-SHA256 → UNBEKANNT; dieser
  Hash ist ausschließlich die Negativkontrolle, keine erfundene Objekt-ID.

Originalinputs exklusiv speichern/read-only setzen und hashen. Danach separater
Analyst ohne Referenzzugriff; alle sechs Antworten unverändert speichern,
read-only setzen und hashen. Antwortcheckpoint committen/pushen und remote
bestätigen. **Erst danach** Ground Truth lesen und getrennt vergleichen.
Originalmessungen unverändert erhalten; keine Fehler beim Vergleich reparieren.

Je Fall KORREKT / FALSCH / UNBEURTEILBAR sowie UNBEKANNT bei unzureichenden
Inputbelegen getrennt ausweisen. Negativkontrollen nicht als zusätzliche echte
Ressourcenfälle oder richtige positive Identitätsbehauptungen zählen.
**SUPPORTED IN THIS TEST** nur bei sauberer unabhängiger Referenz und korrekter
belegter Unterscheidung aller drei Primärfälle sowie bestandenen Kontrollen.
**NOT SUPPORTED** bei falscher beurteilbarer Identitätsaussage. Sonstige nicht
sauber entscheidbare Primärfälle/Aufnahme/Referenz → **INCONCLUSIVE**; UNBEKANNT
bleibt wissenschaftlich gültig, kein falsch behaupteter negativer Beweis.

## Abschluss und STOPP

Bericht mit Ausgangs-/Vertrags-/Hilfencommit, tatsächlichem System/Dateisystem,
Originalinputs, Referenzen, vorab gesicherten Antworten, Fallbewertungen,
Kontrollen, Aussagegrenzen und getrennten Confidence-Achsen. Keine Rawpayloads.
Gemäß RESEARCH-METHOD Standardsuite nach Ergebnis zweimal identisch, bestehende
fünf RC-Deselektionen sichtbar/unverändert. Kein zusätzlicher Probe-/Dateifall.
Alle getrackten Ausgangsdateien per Freeze-Manifest bytegleich erhalten.

Keine Generalisierung auf Clouds, URLs, Datenbanken, Neustarts, fremde Rechner,
Netzwerke, kryptografische Echtheit oder allgemeine AA-Ressourcenidentität.
Keine neue Rechte-, Freigabe-, ALLOW/DENY- oder Stopbefugnis. Keine Graphen,
Architektur, universelle IDs oder Observererweiterung. K14 historisch
INCONCLUSIVE, E2-Metadaten-Lücke und OOS-021 bleiben offen.

Nach Ergebnisbericht Commit, Push, Remote-Bestätigung und Link.
**STOPP: keine allgemeine Ressourcenbindung, Cloudtests, nächste Ressource
oder Observererweiterung.**
