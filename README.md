**English** · [Deutsch](README.de.md)

<p align="center">
  <img src="assets/readme/Agent-Authority-dark.svg" alt="Agent Authority" width="256" height="256">
</p>

<p align="center">
  <a href="https://github.com/landjunge/threaddesk/blob/docs/readme-current-20261107/README.md" title="ThreadDesk"><img src="assets/readme/normalized/ThreadDesk-small.svg" alt="ThreadDesk" width="48" height="48"></a>
  &nbsp;
  <a href="https://github.com/landjunge/KiraBridge/blob/docs/readme-current-20261107/README.md" title="KiraBridge"><img src="assets/readme/KiraBridge-dark.svg" alt="KiraBridge" width="48" height="48"></a>
  &nbsp;
  <a href="https://github.com/landjunge/4AllPass/blob/docs/readme-current-20261107/README.md" title="4AllPass"><img src="assets/readme/normalized/4AllPass-small.svg" alt="4AllPass" width="48" height="48"></a>
  &nbsp;
  <a href="https://github.com/landjunge/tollgate/blob/docs/readme-current-20261107/README.md" title="TollGate"><img src="assets/readme/normalized/TollGate-small.svg" alt="TollGate" width="48" height="48"></a>
</p>

<h1 align="center">Agent Authority</h1>

<p align="center"><strong>Understand what your AI agents report.</strong></p>

Agent Authority reads selected local observations and shows task activity, contradictions and missing evidence. It helps you inspect reports and their sources before drawing conclusions.

**Source version: 0.3.0a2 · Local product preview · Python 3.12 or newer**

[Set up the local preview](docs/PRODUCT-PREVIEW.md) · [macOS development interface](native/macos/README.md)

The repository is private and requires an invitation. There is no published installation package or finished web service. Use and modifications require permission under the [license](LICENSE).

## What Agent Authority helps you do

- **Read observations:** import selected local JSON data; ThreadDesk is an optional read adapter.
- **Inspect activity:** show reported tasks, returns and structural warnings; gaps and conflicts stay visible.
- **View reports:** use text, JSON or an offline HTML report.
- **Explore relationships:** use the dashboard, Authority Graph and evidence inspector in the native macOS development interface.

Agent Authority observes and analyses. It does not approve actions, release secrets or budgets, or stop work. Stored identity and success reports are not independently verified evidence. Existing workflow readers process selected metadata; complete live connections across all products remain planned. [Observation contract](docs/PRODUCT-OBSERVATION-CONTRACT.md) · [Workflow boundaries](docs/WORKFLOW-OBSERVATIONS.md).

## Get started

1. **Arrange access and permission.** The preview currently serves invited users with a local source installation.
2. **Choose observations.** Use local JSON files or explicitly select the ThreadDesk read adapter.
3. **Inspect a report.** Read the text output or save an HTML report. Read warnings together with their evidence references. [Step-by-step guide](docs/PRODUCT-PREVIEW.md).

The normal read path does not change tasks or source data. macOS sample data is for exploring the interface; live Endpoint Security observation needs separate Apple approval and OS permissions. The preview is not a general safety certification.

## Planned collaboration

The five products remain independent. The goal is a shared workflow with **KiraBridge as the communication hub**:

| Product | Role in the shared workflow |
| --- | --- |
| [ThreadDesk](https://github.com/landjunge/threaddesk/blob/docs/readme-current-20261107/README.md) | Keeps project context, knowledge and results. |
| [KiraBridge](https://github.com/landjunge/KiraBridge/blob/docs/readme-current-20261107/README.md) | Relays tasks, questions and replies between chat, local agents and tools. |
| [4AllPass](https://github.com/landjunge/4AllPass/blob/docs/readme-current-20261107/README.md) | Manages credentials; is intended to enable specifically approved access. |
| [TollGate](https://github.com/landjunge/tollgate/blob/docs/readme-current-20261107/README.md) | Checks connected calls and enforces usage limits and stops. |
| [Agent Authority](https://github.com/landjunge/agent-authority-lab/blob/docs/readme-current-20261107/README.md) | Shows observations, contradictions and missing evidence; does not approve actions. |

Some interfaces already exist. A fully configured and verified workflow across all five products is still planned. Approvals stay with the responsible tool and the human. KiraBridge and Agent Authority require access to their private repositories.

## License

[Source-available, all rights reserved](LICENSE). Repository access alone does not permit use, modification or redistribution. Historical MIT license rights remain intact.

Product concept and architecture: **Daniel Filipek (landjunge)**. AI assists with implementation and documentation. Verifiable reviews are welcome; lab results retain their limited research scope.

[Product usage](docs/PRODUCT-PREVIEW.md) · [Workflow findings](docs/WORKFLOW-WARNINGS.md) · [macOS and builds](native/macos/README.md) · [Historical research](docs/RESEARCH-BASELINE.md)
