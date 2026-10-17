# Spätere Bereitstellung auf dem vorhandenen Debian-vServer

Dieser Ablauf ist ein überprüfbarer Vorschlag, keine jetzt ausgeführte
Bereitstellung. Der Nutzerauftrag untersagt System-, Dienst-, Firewalländerung,
Installation und Neustarts bestehender Dienste. Geprüft wird ausschließlich eine
eigene temporäre synthetische Loopbackkopie. SSH-Alias `netcup`, Debian 13.6,
Python 3.13.5 sind lesend bestätigt. Keine Schritte benötigen den Mac zur
eigentlichen Dienstbedienung nach erfolgter Bereitstellung.

## Paketprüfung und private Vorführung

1. Sauberen lokalen Quellcommit festhalten; mit `scripts/package_browser.py`
   das Paket bauen. `sourceClean=true`, Manifest und Paket-SHA-256 prüfen.
   Der Paketinhalt enthält keine States, Credentials, Rohbelege oder Research-
   Collector. Keine unveröffentlichten nativen Änderungen werden mitgenommen.
2. Nach späterer Bereitstellungsfreigabe ein eigenes privates Release-/State-
   Verzeichnis unter dem benannten Dienstbetreiberkonto festlegen. Keine
   bestehende `/opt/ki-helper-runtime`- oder `/opt/aa-private`-Installation
   überschreiben; beide sind getrennte Produkte/Verträge.
3. Paket und SHA256SUMS übertragen und auf Debian `sha256sum -c SHA256SUMS`
   ausführen. Start zunächst ausschließlich mit neu initialisierten synthetischen
   Konten und leerem State: `python3 -B agent-authority-browser.pyz serve
   --state <eigener-state> --port <freier-loopbackport>`.
4. Für diese private Vorführung den gleichen lokalen Port tunneln:
   `ssh -N -L 8873:127.0.0.1:8873 netcup`. Browserziel exakt
   `http://127.0.0.1:8873`. Bei belegtem anderen Port beide Seiten passend
   wählen; keine öffentliche Portfreigabe. Kein Fremddienst wird beendet, um
   einen Port freizumachen. Auf Debian ist kein Browser nötig.
5. Zwei Prüfkonten, leere Auswahl, neutraler Import, Detail-/Kettenzuordnung,
   fremde ID=404, anonym=401 und Stop prüfen. Eigene Prozesse sauber beenden,
   eigenen State/Release nach vereinbarter Aufbewahrung entfernen. Der
   Prüfablauf darf keine echten Agentenaufträge oder Collectoraktionen auslösen.

## Vor dauerhafter oder öffentlicher Nutzung nötige Entscheidungen

| Punkt | Konkrete fehlende Entscheidung / Umsetzung | Abhängige Funktion |
|---|---|---|
| Betreiber und Prozessbetrieb | Eigene unprivilegierte UID, privates Statevolume, feste Release-/Arbeitsverzeichnisse, Ressourcenlimits, Start/Stop/Update und Verantwortlicher; geeigneter Produktions-HTTP-Server | Dauerbetrieb; der aktuelle stdlib-Server bleibt privates Prüfprofil |
| Identität | Separater AA-Client/Audience bei einem vereinbarten standardbasierten Identitätsdienst oder belegte Hilfezentrum-Sessionbrücke; exakte Subject-/Tenant-/Owner-/Source-/Job-Zuordnung, Ablauf/Widerruf | Echte Konten gesperrt; keine erfundenen Produktionsnutzer |
| Öffentlicher Zugang | Eigene Origin/HTTPS, sichere Cookies, Proxy-/Forwarded-Header-Vertrauensgrenze, CSP-/CSRF-/Originvertrag, Rücksprung aus Hilfezentrum | Kein öffentlicher Bindhost/Deployment in dieser Fassung |
| Datenzuführung | Je Quelle eigener neutraler Adapter oder vorhandener Privatdienstabruf mit serverseitiger fester Endpoint-/Objektzuordnung; keine URLs/Pfade aus Browserdaten | Echte Quellenanbindung gesperrt |
| Privatdienstvertrauen | Separat gepinnter vorhandener Reportpublickey, bestehender geeigneter Verifier, tenant/job/source-Zuordnung, Trennung historischer Signatur vom heutigen Keystatus | `aa-report-v1` bleibt nur gemeldete Anzeige; keine positiven Vertrauensstatus |
| Debianbeobachtung | Vorhandener Collector-Hardstop, stillgelegte Testidentität und Auftragssperren bleiben bestehen; zusätzliche Freigaben nur im zuständigen Dienstvertrag | Keine neue Erfassung und kein automatischer Auftrag aus der Browser-App |
| Aufbewahrung | Rechte, Verschlüsselung, Fristen, Empfängerkopien, Backup-/Restore-/Ausfallvertrag; importierte Kopien erben keine Privatdienst-ACK-/Löschgarantie | Reale/private Daten dauerhaft speichern gesperrt |

Erst nach konkretem Review dieser Entscheidungen ein separates Deployment
freigeben. Ein Hilfezentrum-Link ist Zugang zum eigenständigen Agent Authority;
er gibt keine gemeinsame Architektur oder Rechte-/Secret-/Budgetzuständigkeit.
Keine beliebigen Kundenskripte, Auftragswiederholungen oder neuen Collector
einführen. Die unabhängige Teamprüfung wird nach fertigem lokalem Stand extern
eingeplant; hier wird kein Ergebnis dieser späteren Prüfung behauptet.
