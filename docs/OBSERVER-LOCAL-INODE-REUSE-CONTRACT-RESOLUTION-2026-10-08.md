# Vorabklärung: Bedeutung von Frage A und fehlende Messreferenzen

8. Oktober 2026. Ergänzung zum unveränderten
[Vorabvertrag](OBSERVER-LOCAL-INODE-REUSE-CONTRACT-2026-10-08.md), Commit
`eea95b07605fb38d34158a7d333f7afab7e5f382`. Festgelegt **vor** Erstellung der
Messhilfen und vor jedem Ressourcenversuch. Die erste Vertragsfassung bleibt
erhalten; keine Forschungsfrage, Hypothese, Grenze oder Ergebnisregel verändern.

Die interne Vorabprüfung erkannte eine semantische Unschärfe: Der Vertrag
begründet A-UNBEKANNT bei unterschiedlichen Paaren damit, dass die alte Datei
anderswo weiterleben könnte. Die unveränderte Nutzerfrage betrifft jedoch
ausdrücklich **beide Beobachtungen als dieselbe** dauerhaft fortbestehende
Ressource. Der Fortbestand der alten Datei irgendwo ist ein anderer Gegenstand.
Diese zwei Aussagen dürfen nicht vermischt werden.

Die originale Frage A bleibt wörtlich:

> Trägt (st_dev, st_ino) in diesem beobachteten Fall sicher die Aussage, dass beide Beobachtungen dieselbe dauerhaft fortbestehende Ressource sind?

Verbindliche Auswertung im unveränderten, lokalen Linux/tmpfs-Scope:

- Zwei gültige **unterschiedliche** native Paare → **NEIN** zur Identität der
  beiden konkret ausgewählten Messreferenzen. Keine Behauptung, die alte Datei
  existiere nirgendwo mehr; kein Nachweis dauerhafter Eindeutigkeit des Verfahrens.
- Zwei gültige **gleiche** Paare ohne Freigabe-/Neuerstellungs-GT → **UNBEKANNT**.
  Die Paarwiederkehr allein belegt weder dauerhaften Fortbestand noch Austausch.
- Keine Ausgangsmessung, keine neue Messreferenz oder sichtbar ungültige
  Eingabe → **UNBEKANNT**. Kein Ausgang–Ausgang-Ersatzpaar, keine erfundene letzte
  Kennung. Dann auch B UNBEKANNT und Gesamturteil INCONCLUSIVE.

Das Analysepaar bleibt Ausgang + erster Paar-Treffer, ohne Treffer Ausgang +
letzte tatsächlich gemessene neue Kennung. B, C, H1–H3, MAX=10000, sofortiger
Treffer-/Fehlerstopp, GT-Trennung und No-hit-INCONCLUSIVE bleiben unverändert.
Insbesondere ändert ein A-NEIN bei Paarungleichheit das No-hit-Gesamturteil nicht.

Weitere Randfallpräzisierung: Den einen neuen privaten Testordner exklusiv mit
Modus **0700** erzeugen. Falls der festgelegte Ordner bereits existiert,
abbrechen; kein Alternativordner und kein zweiter Ressourcenversuch.

Originalvertrag und dieser Nachtrag werden beide vor Hilfen/Versuch remote
bestätigt. Kein Ergebnis liegt vor, keine Hypothese wird passend gemacht.
