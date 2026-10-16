# Isolierte Dienstqualifikation – vor Ausführung festgelegt

Basis: Master edd40b959fc898edc06e790fe3672e748d7dbb2c. Auftrag vom
16. Oktober 2026, eigene Sitzung. Keine Subagenten, Veröffentlichung, Installation,
Produktserveränderung, Produktintegration oder Merge. D-012 bleibt verbindlich.

## Reihenfolge und Abnahme

1. Originalverträge, A1–A4, Negativbefunde und App-Abschluss lesen; vorhandene
   Arbeitsstände prüfen. Neue Arbeit ausschließlich im begründeten Worktree
   `.worktrees/hosted-qualification`: separater Forschungsadapter und Ergebnisse
   dürfen weder sauberen integrierten Master noch lokale Appänderungen berühren.
2. Archivierten A4-100er-Join mit unverändertem Verifier erneut berechnen,
   Ergebnis außerhalb des Originalarchivs ablegen. PASS nur bei Gleichheit mit
   Original, allen Sammelchecks wahr und 99 Ketten. Das ist keine Livewiederholung.
3. Bestehende eigene Lima-VM `a1-research` starten, Konfiguration und Gast prüfen.
   Nur ohne Hostmounts/Agentforwarding, mit vorhandenen BCC-/Crypto-/Kernelmitteln
   fortfahren. Keine Pakete/VMs/Privilegienkonfiguration ergänzen. Bei fehlender
   Voraussetzung Blocker archivieren und betreffenden Schritt auslassen.
4. Genau ein frisches Zwei-Agenten-Gate mit unveränderten A4-completion-Messquellen:
   neue CA, neue Testkeys, neues Run-/Boot-/Instanzbinding, ein synthetischer
   16-Byte-Write, eigener Dateiscope. Observer nur Objekt und 12s-Fenster.
   Originalregistrar liefert getrennte SCM-/pidfd-/Lifecycle-/Orakelbelege.
   Vor Start Quellhashes, Trustpin und Versuchszahl speichern. PASS nur nach
   originalem OpenSSL-Join: 26 wahre Checks und 23 gemessene Nullverlustwerte.
   Fehler nicht überschreiben; kein automatischer zweiter Versuch/100er-Lauf.
5. Dienstvoraussetzungen getrennt offline qualifizieren: reale Ed25519-Signaturen
   durch vorhandene OpenSSL-Helfer; serverseitig vorgegebene Trustanker statt
   Uploadkeys; Test-Enrolment, Rotation/Widerruf, Mandantkontext. SQLite-Prototyp
   nur für atomare Speicherung eines Beobachtungsbefunds mit Nonce und
   Idempotenzkennung: parallele Prozesse, Neustart, Prozessabbruch vor/nach Commit,
   Konflikt und tenantgebundener Abruf. Kein Exactly-once-Vollzug einer Handlung.
   Fehlende Kernelbelege dürfen dadurch niemals BELEGT werden.
6. Bestehende relevante Produkt-/A1–A4-Regressionen unverändert prüfen; neue
   Qualifikation mit Rohlogs, JUnit/JSON und SHA-256-Index belegen. Neue Testzahlen
   getrennt vom historischen Archiv und vom neuen Live-Gate ausweisen.
7. Eigene Prozesse/Probes/Schlüssel prüfen, Forschungs-VM regulär stoppen.
   Nichtgeheime neue Gastdateien zunächst in expliziten Recovery-Scope verschieben;
   eigene private Schlüssel nur anhand exakter Dateiliste entfernen. Keine
   Bereinigung fremder/alter Arbeitsstände. Worktree bleibt überprüfbares Ergebnis.
8. Dienstbauplan erst auf Grundlage der Ergebnisse abschließen: getrennte
   Aufnahme/Verifier und Forschungsrunner, begrenzter kontrollierter Ablauf,
   je Kettenglied BELEGT/WIDERSPRÜCHLICH/UNVOLLSTÄNDIG/UNBEKANNT; Abnahme vor
   API/Browsergraph und vor öffentlichem Angebot.

## Aussagegrenzen

Ubuntu 24.04 / Kernel 6.8 qualifiziert Debian 13 / Kernel 6.12 nicht. Kein
Produkt-VPS-Zugriff ist Teil dieser Prüfung. Keine Provider-/Modellsitzung wird
beglaubigt. Kompromittierter Host/CA/Root/Kernel bleibt außerhalb der Garantie.
Signatur bestätigt Bytes und Schlüssel; entfernte Wirkung verlangt unabhängige,
vorher vertrauenswürdig registrierte Erfassung. Die SQLite-Prüfung qualifiziert
einen lokalen Datenträger und konkurrierende Prozesse, keinen verteilten Cluster,
keinen Stromausfall und keine VM-Restore-/Backup-Rollback-Sicherheit.

Nur synthetische Daten. Keine Prompts, Gespräche, Tokens oder Arbeitsinhalte.
Auch Metadaten sind potentiell sensibel. Rohdaten dieses internen Versuchs
werden als Forschungsbelege aufbewahrt; das ist keine Kundenaufbewahrungsregel.
