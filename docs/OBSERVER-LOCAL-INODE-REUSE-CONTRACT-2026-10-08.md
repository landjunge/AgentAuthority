# Vorabvertrag: native Dateikennung nach vollständiger Freigabe

8. Oktober 2026. Ausgangscommit:
`bd00c3f56d56fbf86da42be8d59c81a7da8f352b`.
Neuer ausdrücklich beauftragter isolierter Forschungsversuch. Keine
Produktentwicklung; Agent Authority bleibt eigenständiger Beobachter.

## Gelesene Basis und genaue Frage

Vor Versuch vollständig gelesen: LOCAL-FILE-IDENTITY-RESULTS,
RESOURCE-EPOCH-REPEAT-01-RESULTS, REAL-RUN-PROTOTYPE-RESULTS,
RESEARCH-CONSOLIDATION-E1-E7, RESEARCH-METHOD und OUT-OF-SCOPE-DEBT.
Historische Dateien/Befunde bleiben unverändert.

**Kann `(st_dev, st_ino)` über zwei nicht überlappende Dateilebenszeiten hinweg
fälschlich dieselbe Ressourcenidentität nahelegen?**

Gesucht wird ausschließlich die Wiederkehr **der einen Ausgangskennung** bei
einer später exklusiv erzeugten Datei. Keine allgemeine Suche nach beliebigen
neue–neue Kollisionen. Keine universelle Lösung oder zukünftige ID voraussetzen.
Vorab lesend geprüft: Linux 6.18.44, /tmp auf tmpfs, Python 3.12.14;
`/proc/self/fd` ist vorhanden. Keine Versuchsdatei dafür erzeugt.

## Hypothesen und unveränderliche Grenzen

- **H1:** Ohne beobachtete Wiederkehr der Ausgangskombination ist
  Wiederverwendung in diesem Versuch NICHT NACHGEWIESEN. Daraus folgt keine
  Unmöglichkeit von Wiederverwendung.
- **H2:** Ein tatsächlich gleiches natives Paar bei unabhängig belegten
  getrennten Dateilebenszeiten zeigt: Das Paar allein reicht nicht für
  dauerhafte Ressourcenidentität über vollständige Freigabe hinweg.
- **H3:** Kein Treffer innerhalb der festgeschriebenen Grenze →
  **INCONCLUSIVE**, keine dauerhafte Sicherheit.

**MAXIMUM: 10.000 neue Dateilebenszeiten nach genau einer Ausgangsdatei.**
Höchstens 10.001 exklusive Dateierstellungen insgesamt. Das ist ein fester,
vernünftiger lokaler Aufwandsrahmen, keine Wahrscheinlichkeits- oder
Ratenannahme. Keine Erhöhung, Wiederholung, Optimierung oder zweite Suchphase.

Genau ein neuer privater Ordner direkt unter /tmp:
`/tmp/aa-local-inode-reuse-20261008`. Darin ausschließlich eigene temporäre
reguläre Testdatei und notwendige Messartefakte. Die Testdateien bleiben leer;
keine Inhalte lesen, schreiben oder archivieren. Keine Nutzer-/Repositorydatei
als Ressource, Accounts, Secrets, Netzwerk- oder Cloudressourcen.

Unverändertes vorhandenes Dateisystem. Kein Mount, Kernel-/Dateisystemtuning,
Neustart, Inodenmanipulation oder parallele künstliche Last. Strikt sequenziell,
höchstens eine eigene Testdatei zur selben Zeit.

## Kontrollierter Ablauf und operative Freigabe

Ein kleines, ausschließlich für diesen Versuch festes Messwerkzeug ist nötig;
keine Observer-/Labmodule importieren oder ändern. Neue Hilfen separat
festschreiben/pushen, nachdem dieser docs-only Vertrag remote bestätigt ist.
Kein Entwicklungslauf der Dateien vor Freeze.

1. Ausgangsdatei exklusiv mit `O_CREAT|O_EXCL|O_NOFOLLOW` im privaten Ordner
   erzeugen/öffnen; `fstat` bestätigt reguläre Datei und liefert st_dev/st_ino.
   Genau dieses eine eigene Handle; kein dup, fork, mmap oder weiterer Hardlink.
2. Handle schließen. **Unmittelbar danach**, vor jedem neuen open, proc-Scan
   oder Artefaktschreiben: `F_GETFD` muss EBADF ergeben.
3. Datei unlinken; `lstat` muss ENOENT ergeben.
4. Eigene `/proc/self/fd`-Symlinks ausschließlich per enumeration/readlink
   prüfen. Für den privaten Zielpfad einschließlich „(deleted)“ müssen
   **null eigene FD-Symlinktreffer** verbleiben. Keine FD-Ziele öffnen/fstat,
   keine fremden Pfade/FD-Listen speichern. Ein verschwundener temporärer
   proc-Enumerationseintrag darf ENOENT ergeben; andere Scanfehler abbrechen.
5. Erst nach diesen tatsächlichen Prüfungen beginnt die nächste exklusive
   Erstellung am selben privaten Zielpfad. Für jeden neuen Kandidaten:
   fstat-Paar aufnehmen → mit Ausgangspaar vergleichen → sole Handle schließen
   → unmittelbares EBADF → unlink → ENOENT → eigener Ziel-FD-Trefferstand null.
6. Erster gleicher Paarbefund → aktuellen Kandidaten trotzdem vollständig
   bereinigen, dann keine weitere Erstellung. Ohne Treffer spätestens nach
   Kandidat 10.000 beenden.

**Vollständige Freigabe ist operational begrenzt:** Das einzige eigene Handle
ist geschlossen, kein eigener zusätzlicher Zugriff hält die Datei offen,
der einzige kontrollierte Verzeichnislink ist entfernt. Keine künstliche
Pinning-Brücke wie im früheren L2. Kein Nachweis physischer Kernel-Reklamation
oder fehlender Zugriffe fremder privilegierter Prozesse; kontrollierter
Collector und Kernel bleiben vertrauenswürdige Voraussetzungen.

Keine frei gewählten FD-Pfade, Dateien oder Ressourcenparameter. Gleicher
Pfad/Name/Inhalt ist weder Gleichheits- noch Verschiedenheitsbeweis.
Die neue Lebenszeit folgt aus tatsächlich erfolgreicher exklusiver Erstellung
**nach** bestätigter Freigabe, nicht aus Native-Paarungleichheit.

## Originaldaten, unabhängige Ground Truth und Abbruch

Native Paare und operationale Teilbefunde während der Suchschleife nur im
Speicher sammeln. Keine je-Kandidat-Artefaktdateien oder Archivhandles während
des Vergleichs, damit sie keinen zusätzlichen Inoden-/FD-Verbrauch in der
Schleife verursachen. Nach Abbruch/Ende unverändert getrennt archivieren:

- `original/native-pairs.jsonl`: erste Zeile Ausgangspaar, danach je tatsächlich
  erfolgreich fstat- und regulär-geprüfter neuer Datei genau ein Paar mit nur
  st_dev/st_ino. Kein übersprungener Messfehler mit anschließendem Fortsetzen.
- `original/identity-scope.json`: tatsächlich gemessenes Linux/tmpfs sowie
  eingefrorenes MAX=10000. Kein Trefferurteil oder Lebenszeitbeleg.
- `ground-truth/lifetimes.jsonl`: tatsächliche Exklusiverstellung, reguläre-Datei-
  Prüfung, Close/EBADF, unlink/ENOENT und eigener FD-Symlinktrefferstand;
  lokale Versuchsposition nur zur Zuordnung der verlangten Trefferstelle.
  Keine nativen Paare, Gleichheitsurteile, Inhalte oder erwarteten Antworten.
- `capture-status.json`: tatsächliche Zähler, Stopgrund, Fehler und Cleanup;
  separat vom Analysteninput.

Referenz für getrennte Lebenszeiten ist ausschließlich die vollständig
kontrollierte Close/Unlink/Prüf-/Neuerstellungsfolge. Keine erwartete
Paarungleichheit, Pfad-/Inhaltsschlüsse oder spätere Analystantwort als GT.
Native Metadaten und Lifecycle-Befunde vertrauen demselben Kernel/Collector;
methodisch getrennte Ableitungen, kein externer Audit.

**Abbruch:** erster nativer Treffer, MAX=10000 oder erster Aufnahme-/Freigabe-/
Scanfehler. Fehler samt Stufe, Typ, errno und tatsächlichen Teilbefunden sichern;
keine nächste Kandidatenerstellung nach Fehler, keine Reparatur/Wiederholung.
Nur notwendiges Cleanup der selbst erzeugten aktuellen Datei versuchen und
seine tatsächlichen Fehler getrennt erhalten. Keine fehlgeschlagene Freigabe
als erfüllt markieren. Harte Prozessunterbrechung mit verlorenen Speicher-
messungen → unbeurteilbar/INCONCLUSIVE; keine Daten rekonstruieren oder nachtesten.

## Getrennte Analyse, Antwortfreeze und Bewertung

Nach Sicherung/Hashen der Originale erhält der separate Analyst **ausschließlich**
`native-pairs.jsonl` und `identity-scope.json`. Keine Ground Truth,
Exklusiverstellungs-/Freigabebefunde, Capture-Stopgründe, Fall-Sollwerte oder
historischen Antworten. Analysepaar: Ausgang + erster gleicher Kandidat;
ohne Treffer Ausgang + letzte tatsächlich gemessene neue Kennung.

Die drei unveränderten Fragen:

**A:** Trägt `(st_dev, st_ino)` in diesem beobachteten Fall sicher die Aussage,
dass beide Beobachtungen dieselbe dauerhaft fortbestehende Ressource sind?
JA / NEIN / UNBEKANNT.

Ohne tatsächliche Lebenszeitbindung ist dauerhafte Fortexistenz **UNBEKANNT**.
Ungleiche Paare zeigen die native Kennungsdifferenz der Messreferenzen, aber
nicht, ob die Ausgangsdatei anderweitig weiterlebt. Gleiche Paare ohne
Freigabe-/Neuerstellungsbeleg beweisen weder Fortbestand noch Wiederverwendung.
Keine Umformulierung von A zur bloßen Paar-/Referenzgleichheit.

**B:** Wurde in diesem Versuch eine Wiederverwendung derselben lokalen Kennung
für zwei getrennte Dateilebenszeiten beobachtet? JA / NEIN / UNBEKANNT.

Bei Paarwiederkehr ohne Lebenszeit-GT → **UNBEKANNT**; sichtbare
Metadatenrekurrenz und nachgewiesene getrennte Lebenszeiten bleiben verschieden.
Bei genau 10000 vollständig vorliegenden gültigen neuen Messpaaren ohne Wiederkehr →
**NEIN**, ausschließlich für beobachtete Ausgangspaar-Wiederverwendung in
diesem festen Umfang. Die 10001 gültigen Zeilen einschließlich Ausgangspaar
belegen hier die native Listen-Vollständigkeit. Unvollständige oder sichtbar
fehlerhafte native Eingabe → **UNBEKANNT**. Verdeckte Lifecyclefehler sind dem
Analysten nicht zugänglich: Sie ändern das Gesamturteil zu INCONCLUSIVE,
werden aber nicht nachträglich als Analystenfehler ausgegeben.
Kein B-NEIN für grundsätzliche Wiederverwendbarkeit oder dauerhafte Sicherheit.

**C:** Welche Aussage darf aus diesem Versuch ausdrücklich nicht verallgemeinert
werden? Kein dauerhafter Eindeutigkeits-/Unmöglichkeitsbeweis, keine andere
Dateisystem-/Host-/Cloud-/Netzwerk-/Neustartgeltung oder Wiederverwendungsrate,
keine Kryptoechtheit und kein zukünftiges Identitätssystem.

A/B/C mit sichtbarem Beleg und Grenze unverändert speichern, read-only setzen
und hashen. Antwortcheckpoint committen/pushen und remote bestätigen.
**Erst danach** Ground Truth lesen und getrennt bewerten.

- **SUPPORTED IN THIS TEST:** native Ausgangspaar-Wiederkehr tatsächlich
  aufgenommen **und** getrennter Lifecycle-Nachweis sauber; damit H2 innerhalb
  dieses Systems gestützt. UNKNOWN des minimal informierten Analysten bleibt
  zulässige epistemische Zurückhaltung, kein falscher Lebenszeitschluss.
- **INCONCLUSIVE:** kein Treffer innerhalb der eingefrorenen Grenze; oder
  Aufnahme/Referenz/Abbruch erlaubt keine saubere Bewertung. Kein Fehlschlag
  und kein dauerhafter Sicherheitsbeweis.
- **NOT SUPPORTED:** nachweislich falsche beurteilbare Aussage. Nicht durch
  Reparatur oder stillschweigende Umdeutung aufheben.

Wahrer Ablauf, Beurteilbarkeit und Wissensgrenze des Analysten getrennt
ausweisen. Ein unbekannter Schluss ist kein negativer Beweis.

## Abschluss und STOPP

Bericht: Ausgangs-/Vertrags-/Hilfen-/Antwortcheckpoint, tatsächliches System,
MAX, Ausgangspaar, tatsächliche Neuerstellungen/Messungen, erster Treffer oder
nicht beobachtet, vorab gespeicherte Antworten, GT, Fehler/Cleanup,
Standardsuite und beide Confidence-Achsen. Alle getrackten Ausgangsdateien
gegen Freeze-Manifest bytegleich erhalten.

Standardsuite gemäß Methodik nach Ergebnis zweimal unverändert, fünf bestehende
RC-Deselektionen sichtbar. Kein weiterer Dateiversuch. Ergebnis committen,
pushen und remote bestätigen; Link ausgeben.

Historische K14-/E2-/OOS-021-Grenzen nicht schließen. Keine dauerhafte ID,
Generation-ID, Hash-ID, Register, Datenbank, Graph, Observererweiterung oder
Reparatur. **STOPP nach Ergebnis, Commit und Push.**
