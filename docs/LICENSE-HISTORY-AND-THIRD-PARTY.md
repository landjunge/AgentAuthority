# License history and third-party scope / Lizenzhistorie und Drittbestandteile

Checked / geprüft: 2026-10-27, source / Quellstand
`75fb14e99a50b967b8624191f0178963c433fbd9`.
This is an evidence index, not a new license or an ownership warranty.
Dies ist eine Belegübersicht, keine neue Lizenz oder Rechtegarantie.

## Current terms / Aktuelle Bedingungen

[LICENSE](../LICENSE) contains the all-rights-reserved notice and preserves
historical MIT grants. [pyproject.toml](../pyproject.toml) already points to that
file with `license = { file = "LICENSE" }`; it does not declare the current
project MIT. The README records the repository as private. Access settings
are separate from copyright permissions, including permissions already granted
for historical material. The visibility sentence in LICENSE was made neutral;
the permission restrictions, copyright and historical boundary remain unchanged.

Die aktuelle LICENSE enthält den Rechtevorbehalt und erhält historische
MIT-Rechte. Die Python-Metadaten verweisen bereits auf diese Datei. Der private
Zugriffsstatus im README ist keine Rücknahme historischer Rechte. Korrigiert
wurde nur die Aussage über öffentliche Sichtbarkeit; Copyright,
Erlaubnisvorbehalte und historische Grenze sind unverändert.

## Historical evidence / Historische Belege

| Evidence / Beleg | Scope / Umfang |
| --- | --- |
| [MIT parent `dff10d5be32213b768f3bd7564b52f2b3b52b828`](https://github.com/landjunge/agent-authority-lab/blob/dff10d5be32213b768f3bd7564b52f2b3b52b828/LICENSE) | Exact MIT text and `Copyright (c) 2026 landjunge` immediately before the change in master. / Unmittelbar vorheriger MIT-Text mit Copyright. |
| [Change `67657654896a36aa6f3b29a840249c2711d92f94`](https://github.com/landjunge/agent-authority-lab/commit/67657654896a36aa6f3b29a840249c2711d92f94), 2026-09-21 04:17:49 UTC | Introduction of the current notice in master; its historical clause expressly preserves earlier MIT rights. / Einführung in master unter ausdrücklichem Erhalt früherer MIT-Rechte. |
| Current notice / Aktueller Hinweis | Applies to material first published under it, subject to its exact historical clause. A later repository revision containing older MIT material does not erase the earlier grant. / Maßgeblich ist die vorhandene Klausel; ein neuer Commit beseitigt keine Rechte am darin weiter enthaltenen MIT-Altmaterial. |

These are source-history pins, not a complete record of distribution, recipients
or private agreements. A predecessor work branch also contains a notice-change
commit (`745641c509826791586e8e7dfd5c49c17b025c0d`); its commit date alone does
not establish public distribution. Preserve the actual terms accompanying each
historical copy. The authorized GitHub releases query returned no entries on
2026-10-27; that does not establish that no copies were ever distributed.

Die Pins belegen die Quellhistorie, nicht sämtliche Empfänger oder Verträge.
Der Datumsstempel eines früheren Arbeitsbranch-Commits beweist keine damalige
Veröffentlichung. Rechtmäßig eingeräumte MIT-Rechte bleiben einschließlich der
Nutzungs-, Änderungs-, Weitergabe- und kommerziellen Rechte unter den damaligen
Bedingungen bestehen; erforderliche Copyright-/Lizenzhinweise sind zu erhalten.

## Third-party components / Drittbestandteile

| Declared scope / Deklarierter Umfang | Evidence and remaining work / Beleg und offene Arbeit |
| --- | --- |
| Python product / Python-Produkt | Root pyproject declares `dependencies = []`. This describes project dependencies, not the Python interpreter, OS or whole research tree. / Keine externen Produktabhängigkeiten im Manifest; Interpreter, OS und Forschung separat. |
| Build and development / Bau und Entwicklung | `setuptools>=68`, `pytest>=8`, `hypothesis>=6.100` are ranges rather than an installed-version inventory. Setuptools/pytest use MIT, Hypothesis MPL-2.0; retain applicable upstream notices for actual redistributed components. / Konkrete Versionen und tatsächlich weitergegebene Teile noch zu belegen. |
| Native macOS / Native macOS-Anwendung | [Package.swift](../native/macos/Package.swift) declares internal targets and Apple Security linking, no external Swift package. Swift/Apple runtime and SDK terms remain separate. / System- und Laufzeitrechte gesondert prüfen. |
| Embedded Python / Eingebettetes Python | [fetch_runtime.py](../native/macos/scripts/fetch_runtime.py) pins CPython 3.12.15, python-build-standalone 20261009, Intel archive SHA-256 `fb3187d95334813b88940db0f1ca57b84cedfd552739c3a5771c3ea0e49988c9`. [build_app.py](../native/macos/scripts/build_app.py) copies discovered LICENSE/COPYING files into Runtime/licenses and the own LICENSE separately. Inspect the exact final runtime/native bundle and all required notices, including bundled libraries; existence of some license files is not completeness. / Endgültiges Bundle einschließlich fremder Laufzeitbibliotheken prüfen. |
| Linux research / Linux-Forschung | `research/a1_linux/observer.py` and other research modules import `bcc.BPF`; research cryptography imports include `research/a2_linux/protocol.py`. Root pyproject does not pin these environments. BCC, kernel/BPF/LLVM, cryptography and VM images need their own exact inventory if supplied. / Forschungsumgebungen benötigen vor Weitergabe eigene Versions- und Lizenzbelege. |

The own notice does not establish ownership of upstream components. Before
distribution, record actual versions, license choices, original notices and any
required source availability per shipped target. This source review does not
provide a final SBOM or a complete native/runtime compliance assessment.

Der Rechtevorbehalt belegt kein Eigentum an Fremdkomponenten. Für einen Verkauf
oder eine exklusive Lizenz sind eigene übertragbare Rechte, bestehende
MIT-Rechte und Fremdrechte getrennt zu erfassen. Beiträge, Arbeitgeber- und
Auftragsbezüge, Übertragungs-/Unterlizenzrechte sowie KI-/Referenzherkunft
bedürfen eigener Nachweise. Dieser Index erweitert keine Nutzungsrechte.
