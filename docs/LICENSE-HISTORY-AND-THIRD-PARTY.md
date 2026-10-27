# Lizenzhistorie und Drittbestandteile

Geprüft am 27.10.2026; Ausgangsstand
`75fb14e99a50b967b8624191f0178963c433fbd9`.
Dies ist eine Belegübersicht, keine neue Lizenz oder Rechtegarantie.

## Aktuelle Bedingungen und Sprachstand

Die [LICENSE](../LICENSE) enthält weiterhin das englische Original des
Rechtevorbehalts und erhält historische MIT-Rechte. Die vollständige deutsche
Übersetzung mit deutscher Vorrangklausel ist als konkreter externer Entwurf
vorbereitet, aber noch nicht freigegeben oder angewandt. Deutsch ist als
Zielsprache entschieden; bis zur Freigabe des genauen Texts wird keine bereits
maßgebliche deutsche Lizenzfassung behauptet. Der frühere Vorschlag eines
englischen Sprachvorrangs ist verworfen.

[pyproject.toml](../pyproject.toml) verweist bereits mit
`license = { file = "LICENSE" }` auf diese Datei und deklariert das aktuelle
Projekt nicht als MIT. Das README bezeichnet das Repository als privat.
Zugriffseinstellungen sind von urheberrechtlichen Erlaubnissen und bereits
eingeräumten historischen Rechten getrennt. Der Sichtbarkeitssatz in LICENSE
wurde neutralisiert; Verbote, Copyright und historische Grenze blieben erhalten.
Die deutschen Erläuterungen dieser Übersicht erteilen keine zusätzlichen Rechte.

## Historische Belege

| Beleg | Umfang |
| --- | --- |
| [MIT-Parent `dff10d5be32213b768f3bd7564b52f2b3b52b828`](https://github.com/landjunge/agent-authority-lab/blob/dff10d5be32213b768f3bd7564b52f2b3b52b828/LICENSE) | Genauer ursprünglicher MIT-Text mit `Copyright (c) 2026 landjunge` unmittelbar vor dem Wechsel in master. |
| [Wechsel `67657654896a36aa6f3b29a840249c2711d92f94`](https://github.com/landjunge/agent-authority-lab/commit/67657654896a36aa6f3b29a840249c2711d92f94), 21.09.2026 04:17:49 UTC | Einführung des jetzigen Rechtevorbehalts in master mit ausdrücklichem Erhalt früherer MIT-Rechte. |
| Aktueller Hinweis | Maßgeblich ist seine genaue historische Klausel. Ein neuer Commit beseitigt keine bereits eingeräumten Rechte am darin weiter enthaltenen MIT-Altmaterial. |

Die Pins belegen die Quellhistorie, nicht sämtliche Empfänger oder privaten
Verträge. Ein früherer Arbeitsbranch enthält ebenfalls einen Lizenzwechselcommit
(`745641c509826791586e8e7dfd5c49c17b025c0d`); sein Datumsstempel allein belegt
keine öffentliche Verteilung. Historische Kopien sind nach den tatsächlich
mitgegebenen Bedingungen zu beurteilen. Die autorisierte GitHub-Releaseabfrage
lieferte am 27.10.2026 keine Einträge; das beweist nicht, dass nie Kopien
anderweitig verteilt wurden.

Rechtmäßig eingeräumte historische MIT-Rechte bleiben einschließlich Nutzung,
Änderung, Weitergabe und kommerzieller Verwertung unter den damaligen
Bedingungen bestehen. Erforderliche Copyright-/Lizenzhinweise sind zu erhalten.
Historische und fremde Originaltexte werden nicht durch Übersetzungen der
heutigen eigenen Bedingungen ersetzt.

## Drittbestandteile

| Deklarierter Umfang | Beleg und offene Auslieferungsarbeit |
| --- | --- |
| Python-Produkt | Root-pyproject deklariert `dependencies = []`. Dies beschreibt Projektabhängigkeiten, nicht den Python-Interpreter, das Betriebssystem oder den gesamten Forschungsbaum. |
| Bau und Entwicklung | `setuptools>=68`, `pytest>=8`, `hypothesis>=6.100` sind Versionsbereiche, kein Inventar installierter Versionen. Setuptools/pytest verwenden MIT, Hypothesis MPL-2.0; einschlägige Originalhinweise für tatsächlich weitergegebene Komponenten erhalten. |
| Native macOS-Anwendung | [Package.swift](../native/macos/Package.swift) deklariert interne Targets und Apple-Security-Linking, keine externen Swift-Pakete. Swift-/Apple-Laufzeit- und SDK-Bedingungen bleiben gesondert zu prüfen. |
| Eingebettetes Python | [fetch_runtime.py](../native/macos/scripts/fetch_runtime.py) pinnt CPython 3.12.15 aus python-build-standalone 20261009, Intel-Archiv SHA-256 `fb3187d95334813b88940db0f1ca57b84cedfd552739c3a5771c3ea0e49988c9`. [build_app.py](../native/macos/scripts/build_app.py) kopiert gefundene LICENSE/COPYING-Dateien nach `Runtime/licenses` und die eigene LICENSE separat. Das genaue endgültige Laufzeit-/Native-Bundle samt Bibliotheken und allen erforderlichen Hinweisen prüfen; die Existenz einzelner Lizenzdateien ist kein Vollständigkeitsbeweis. |
| Linux-Forschung | `research/a1_linux/observer.py` und weitere Forschungsmodule importieren `bcc.BPF`; Kryptografieimporte stehen u.a. in `research/a2_linux/protocol.py`. Root-pyproject pinnt diese Umgebungen nicht. BCC, Kernel/BPF/LLVM, cryptography und VM-Images benötigen bei Weitergabe eigene genaue Inventare. |

Der eigene Rechtevorbehalt belegt kein Eigentum an Fremdkomponenten. Vor
Auslieferung sind tatsächliche Versionen, zulässige Lizenzwahl, Originalhinweise
und erforderliche Quellverfügbarkeit je Lieferziel zu dokumentieren. Diese
Quellprüfung ist keine finale SBOM und keine vollständige Prüfung aller nativen
und Laufzeitbestandteile.

Für Verkauf oder exklusive Lizenz sind eigene übertragbare Rechte, historische
MIT-Rechte und Fremdrechte getrennt zu erfassen. Beiträge, Arbeitgeber- und
Auftragsbezüge, Übertragungs-/Unterlizenzrechte sowie KI-/Referenzherkunft
bedürfen eigener Nachweise. Dieser Index erweitert keine Nutzungsrechte.
