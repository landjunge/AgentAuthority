# A3.1: Anbieterbeleg und getrennte lokale Client-/Auftragsbindung

Aktueller Nutzerauftrag, Basis28ff798e2548a82dbf787cbba0399c5a1857437f.
Keine historischen Änderungen. A1/A2/A3-Battery wird nicht wiederholt.

H-A31-PROVIDER: Eine verfügbare echte Providersitzung beglaubigt einen frischen
künstlichen Job/Antwortdigest mit unabhängig prüfbarem Providertrustanchor,
Sitzung, Challenge und Ablauf. Accounttoken/Client-ID/Thread-ID genügen nicht.
Fehlt dieser reale Mechanismus, bleibt die Kette UNBEKANNT, keine Simulation.

Separater schwächerer Versuch H-A31-LOCAL: Ein vom Host gestarteter echter,
Apple-Developer-ID-validierter Clientprozess wird per Kernelstart und dynamischem
SecCodeCheckValidity geprüft; sein exklusiver Antwortkanal liefert einen
frischen künstlichen Job. Ein lokaler Attestor signiert Prozess/Codepin,
Transportkontext, Challenge, Jobdigest, Zeitfenster und einmalige Receipt-ID.
Dies ist Hostvertrauen, keine signierte Providerantwort/Modellidentität.
Geerbte stdout-Pipes erlauben Clientnachkommen, daher keine unabhängige
Zuordnung jedes Antwortbytes zum Rootclientprozess behaupten.

Vor echten Clientversuchen neue Quellpins/CA committen. Tatsächlich vorhandene
Codex-/Grok-Binärsignaturen und OAuth/OIDC-/Responseverträge lesen/testen.
Bekannte Issuer/Audience aus unabhängigem Clientvertrag pinnen, nicht aus dem
zu prüfenden Token kopieren. Subject nur in privatem Speicher vergleichen;
kein Token, Subject, Privatekey oder Modelltext archivieren. Ohne originale
OIDC-Loginchallenge kein historisches nonce-PASS. Keine neue Anmeldung,
Tokenkopie, Scopeänderung oder produktive API-/Accountänderung.

Echte Clientfälle: je ein frischer Codex- und Grok-Auftrag; zusätzliche echte
Sitzung für Fremdkontext/Sitzungswechsel; genau ein echter Delegationsversuch.
Die unabhängige lokale Receiptprüfung testet gültigen Auftrag, fremden
Prozess-/Sitzungskontext, einmaliges Receipt-Replay, mutierten Jobdigest,
Sitzungswechsel, Delegierten-/Elternbinding und Ablauf. Mutationen sind lokale
Negativkontrollen, keine simulierten Providerfunktionen. Fehlende Delegierten-
Belege ausdrücklich UNBEKANNT. Echte Fehler zählen, kein stiller Retry.

Nur zwei neue Linux-Integrationwrites (Codex/Grok), wenn der neue lokale
Client-/Jobnachweis qualifiziert ist: konkreter Grund ist der neue dynamisch
geprüfte Signatur-/Prozess-/Digest-Eintrittspunkt. Vorher bestehende A3-Quellen
bytegleich in separaten Gastpfad kopieren, frische CA/Wrapperregistrierung,
A2-Starter und unabhängigen A1-Observer wiederverwenden. Keine sechsfache
Writerbattery, kein PID-Reuse/Kernelumbau. Neue Eingangsbindung/offline-Join
additiv prüfen; echte externe Agentenketten bleiben getrennt.

BELEGT / TEILWEISE BELEGT / WIDERLEGT / UNBEKANNT getrennt für Provider,
Account, Clientcode, Hostprozess, Threadclaim, Job und Linux-Wirkung. Verlust/
fehlende Felder nicht als0/Erfolg. D-012: Beobachtung/Analyse, keine Produkt-
ALLOW/DENY-/Rechtefolge. GastRoot ausschließlich eigene bestehende VM.
Keine Hostfreigabe umgehen. Private Versuchsschlüssel nach Export löschen,
eigene VM stoppen, neue Daten/Tests/Quellen archivieren und regulär nur
eigenen Branch pushen, kein Merge/Ready. Passende Tests und fixe Gesamtsuiten.
