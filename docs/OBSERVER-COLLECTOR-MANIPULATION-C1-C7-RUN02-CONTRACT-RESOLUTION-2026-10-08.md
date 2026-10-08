# Vertragsauflösung: C1–C7 Run 02 Gate-Zeitachse

8. Oktober 2026. Der eingefrorene Run-02-Vertrag
`OBSERVER-COLLECTOR-MANIPULATION-C1-C7-RUN02-CONTRACT-2026-10-08.md`
bleibt bytegleich.

## Festgestellter enger Konflikt

Im Abschnitt „Laufzeit- und Gate-Vertrag“ steht unter „Vor Aufnahme werden
gesichert und geprüft“, der Baum sei sauber und das additive Helper-/Testset
existiere noch nicht. Der spätere Abschnitt „Einmaligkeit, Prozesshaltung und
Pre-GT-Freeze“ verlangt dagegen zwingend, dass dieser Helper samt Tests vor der
Aufnahme implementiert, geprüft, committed, gepusht und remote bestätigt ist.
Beides kann unmittelbar vor demselben Aufnahmezeitpunkt nicht zugleich gelten.

Der Konflikt wurde bei der statischen Prüfung entdeckt. Zu diesem Zeitpunkt
hatte kein P1–P7-Messaufruf stattgefunden und keine Ground Truth begonnen.

## Verbindliche Auflösung ohne Änderung des Versuchsdesigns

Die zwei Zustände gelten an den zwei im Vertrag bereits vorgesehenen
Zeitpunkten:

1. **Vor experimenteller Implementierung:** Am Vertrags-Ausgangsstand
   `0532f31a726b3bb7675555c92bf9f78d00a20874` ist der Git-Baum sauber und
   der neue Helper samt Tests existiert noch nicht. Der Vertrag ist auf dem
   gleichnamigen Remote-Branch bestätigt.
2. **Unmittelbar vor Aufnahme:** Helper und Tests müssen vorhanden, statisch
   und mit Fake-Tests geprüft, in einem eigenen Commit gepusht und per
   `git ls-remote` bestätigt sein. Der Git-Baum muss dann wieder sauber sein.

Das ist eine reine Zeitachsenauflösung der widersprüchlichen
Existenzanforderung. H1–H4, C1–C7, P1–P7, A/B/C/D, Wrapperprofile,
I/O-Ground-Truth, Verzeichnis, Reihenfolge, Pre-GT-Checkpoint,
Einmaligkeitsregel, Bewertung und Stopregeln bleiben unverändert. Die
Auflösung erteilt keine Erlaubnis für einen zusätzlichen Lauf oder eine
nachträgliche Anpassung an Ergebnisse.
