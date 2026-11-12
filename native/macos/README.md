# Agent Authority for macOS

Native observer application; the family-header change is based on master `23dd5f8`.
AppKit split window, compact dashboard, graph, inspector, evidence tables,
DE/EN localization, read-only product input and a separate macOS test host.
The Python product engine and historical lab remain unchanged.

## Build and open

Requires Xcode / Swift 5.9 or newer and Python 3.12 for build tooling.
The supplied runtime download is pinned for Intel Macs. The application target
and native helpers use macOS 12; the embedded Intel Python runtime targets 10.15.

```sh
cd native/macos
python3.12 scripts/fetch_runtime.py
python3.12 scripts/build_app.py
open "build/Agent Authority.app"
```

The build directory is ignored by Git. It contains the app with a relocatable
Python runtime, unchanged `agent_authority` modules, native process probe,
controlled writer and compiled observer system extension. No pip installation,
Terminal process or project checkout is required when using the built app.
An explicit external Python 3.12+ interpreter may be selected in Settings.

The default build is **ad-hoc signed for local development**. It is not notarized
and cannot activate an Endpoint Security collector. Privacy grants are tied to
the executing signed component; rebuilding can require renewed user consent.

## Using real input

Choose a folder of `agent-authority-observation-v1` JSON files and its source ID.
The app launches its own bounded reader process and displays the neutral report.
It never writes the source. Source reads have a 30-second supervisor deadline,
bounded output, cancellation, and the existing engine's independent input limits.
The report's display truncation is shown separately from read completeness.
You can also open a saved `agent-authority-observation-report-v1` JSON report.

Meldungen are reported entries. They do not prove an agent, authority,
delegation, completion or external effect. Structural warnings are selectable
evidence nodes. The initial 50-agent sample is explicitly synthetic.

Graph modes: focused chain, compact agent overview, aggregated branches.
Double-click a cluster to expand it. Incoming/outgoing group relationships and
their evidence references remain in the model. Hover shows the full node facts.
Selection preserves the contextual attribution chain; raw data is selectable.
Large agent samples automatically aggregate above 80 agents. The graph is drawn
on demand with visible-node clipping and spatial hit testing. No periodic
animation or permanent GPU effect. Tables and inspector use overlay scrollers.

## Localization

`AuthorityCore/Resources/Strings.json` contains every owned UI phrase in German
and English. Stable keys, complete catalogs and visible unknown-key markers
follow the inspected ThreadDesk principle without importing ThreadDesk code,
preferences, terminology or architecture. Language priority: explicit command
argument / app selection, saved app preference, Agent Authority / locale environment,
first supported macOS preferred language, then German. `C` / `POSIX` are skipped.
Language and appearance can be switched in the app without restarting.
System privacy dialogs remain owned and localized by macOS.

## macOS test host and real external prerequisites

The test host implements native folder selection, Accessibility checks/prompts,
screen capture preflight/request, Apple Events consent per chosen target app,
version-specific Full Disk Access settings links, and system extension activation
through `OSSystemExtensionRequest`. It never changes TCC databases, resets
permissions, disables SIP or launches the main app or its test writers as root.
The local process probe records own-process instance metadata in the app context;
it is not presented as an independent writer proof.

The system extension uses only ES NOTIFY write/close/fork/exec/exit events.
Its XPC interface has four fixed read/scope operations, bounded JSON, a finite
scope lifetime and mutual kernel-enforced code-signature requirements available
on macOS 12. No PID-based IPC authentication and no arbitrary root commands.
Events omit paths, argv, environments and file content. Selected held file objects,
owner UID, process start, PID version, boot context, lifecycle, kernel sequence
gaps, nonmonotonic sequences and local buffer drops are kept separate.

The seven launches implement the six controls: A writes, B idle, C writes another
file, child writes, forged PID claim, and two sequential writers. The collector
must actually connect. Qualification requires kernel instance/lifecycle matches,
known loss controls and the expected write count. Missing prerequisites or
events produce UNKNOWN; a mocked channel never supplies proof. Provider/model
identity and durable file effects remain UNKNOWN even with successful controls.
The resulting minimized events can be examined in the graph and exported.

To activate the collector, an Apple-approved Endpoint Security entitlement,
Developer ID identity and matching provisioning are required. This session had
**zero valid signing identities**. No live privileged collector or writer battery
was claimed or executed. Build with the real credentials once available:

```sh
python3.12 scripts/build_app.py --sign "Developer ID Application: YOUR IDENTITY" \
  --team YOURTEAMID --host-profile /path/host.provisionprofile \
  --collector-profile /path/collector.provisionprofile
```

Install the signed app in `/Applications`, notarize the distribution through
Apple's tooling, activate its extension and grant **the collector's own** Full
Disk Access. The main app's grant is not a substitute. ES's actual initialization
result distinguishes privilege, entitlement and TCC failures. These prerequisites
cannot be manufactured by a build flag or ordinary user approval alone.

Official sources: [Apple ES sample](https://developer.apple.com/documentation/endpointsecurity/monitoring-system-events-with-endpoint-security),
[ES entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.endpoint-security.client),
[XPC peer requirement](https://developer.apple.com/documentation/xpc/xpc_connection_set_peer_code_signing_requirement),
[SIP runtime boundaries](https://developer.apple.com/library/archive/documentation/Security/Conceptual/System_Integrity_Protection_Guide/RuntimeProtections/RuntimeProtections.html).
API declarations were also checked in the installed Xcode 16 / SDK 15 headers.

## Verification

```sh
swift test
python3.12 scripts/check_sources.py
```

Native view screenshots and smoke results are in `docs/native-macos-20261012`.
Snapshot mode caches the app's own native view; it needs no screen-recording grant
and does not capture other apps. It can render a 2560×1440 logical / 5120×2880 pixel
view without changing the user's display settings:

```sh
"build/Agent Authority.app/Contents/MacOS/AgentAuthorityMac" \
  --lang de --theme dark --size 2560x1440 --graph-mode 1 \
  --snapshot /tmp/agent-authority-native-5k.png
```

Actual UI checks were run on the R9 M380 / 2 GB host, running macOS 15.7.4.
macOS 12 compatibility is checked through API availability and Mach-O deployment
targets; an actual Monterey run is still needed. The local package is Intel;
an Apple Silicon distribution needs a corresponding runtime and signing build.

## Graph Back and separate warning demo

The visible Back button restores one previous focused view, including graph mode,
chain anchor, selection, proof filter, search, expanded groups and the exact zoom
and pan. Focus, mode, filter and group expansion record navigation; typing, zoom
and pan alone do not. Restoration never records a new entry or fits the viewport.
Replacing the source document clears history, including on refresh.

Warnings are separate from `ProofStatus` and its unchanged palette. The clearly
marked synthetic warning menu provides information, elevated attention, warning,
critical, not assessable and an explicitly checked clear case. The Inspector
shows reason, assessability, node/relationship, time, source and evidence references.
Absent references remain unknown. Critical has a persistent selectable message.
These fixtures are not part of engine reports or evidence exports. Imported
reports and kernel observations have no warning evaluation and remain neutral
not assessable; no production risk detection or safety assurance is implemented.

Only visible warning/critical node borders animate in local Core Animation layers
(2.8/1.8 second legs, autoreversing). They stop offscreen or when the window is
occluded/minimized. The graph has no animation render timer or repeated layout.
The Warning pulses checkbox persists its choice; the official NSWorkspace Reduce
Motion setting always overrides it. Static symbols, colors, labels and the critical
message remain. Blue/orange use native system colors; existing ThreadDesk-derived
amber/red and all proof colors remain unchanged.

In a logged-in graphical macOS session, run the actual-controller regressions:

```sh
python3.12 scripts/check_ui_regressions.py \
  --executable "build/navigation-warnings-review/Agent Authority.app/Contents/MacOS/AgentAuthorityMac" \
  --output /tmp/authority-ui-regression
```

The runner checks DE 1680×960 and EN 1150×730, fails for any failed assertion,
and starts no permission prompts or experiments. New unit tests cover history,
assessability, synthetic/real separation and motion policy. Final results and
inspected native captures are in `docs/native-ui-navigation-warnings-20261012`.
`--reduce-motion` only forces reduction for capture diagnostics; it cannot disable
the system setting. The real system preference was read, not changed in this task.

## Normal startup investigation

The reported blank graph on normal review startup could not be reproduced in
the subsequent controlled launches. The original failing process had already
exited. A confirmed fix for that original symptom is therefore still open.
Normal Launch Services starts without diagnostic arguments, sidebar interaction,
and simultaneous operation with the older bundle were inspected through existing
authorized Accessibility access and real WindowServer captures, separately from
bitmap diagnostics. Results are in `docs/native-ui-start-fix-20261012`.

New AppKit XCTest cases cover initial view loading and application startup without
an explicit rebuild, sidebar navigation, distinct empty-source/filter messages,
and passive diagnostics that must not load missing views. Existing Back and warning
logic and proof colors are retained. Empty sources now have a distinct explanation;
they never cause an automatic switch to synthetic data.

A review build can identify itself visibly while retaining the same product:

```sh
python3.12 scripts/build_app.py --output build/navigation-warnings-review \
  --review-label startup-check-20261012
```

To capture a future failing state, start the exact bundle with the optional
`--normal-state-json /tmp/authority-live-state.json` argument. For 30 seconds the
app passively records source, filters, graph mode, selection, geometry, viewport,
draw count, history and animation state. It never rebuilds, lays out, fits,
renders, changes preferences or terminates the app; diagnostic event traces go
to stdout only with this argument. Without it no observer or event logging runs.
The investigation also exercised actual menu actions, zoom, mouse pan and three
Back steps; automation must wait for menu focus completion before sending its
next zoom action. Static capture comparisons are not a claim of continuous manual
visual testing of the running animation.

## Native family header and switching / Nativer Familienheader und Fensterwechsel

**Deutsch:** Der vorhandene AppKit-Renderer `ProductHeaderView` wird weiterverwendet;
kein Webview-/SwiftUI-Umbau. Originale PNGs, Katalog und Manifest stammen aus dem
ThreadDesk-Modul 1.2.0, Pin `cb4261cbd240834390e9ce24909f2ab5a01492d9`.
Die fünf Bedienziele sind 44×44 Punkte, die Originalausschnitte 32 Punkte groß.
Das Fenster erlaubt 900×600 äußere Punkte; unter 1150 Punkten Breite klappt der
vorhandene Inspector ein. Seine bisherige manuelle Einklappwahl bleibt erhalten;
bei schmaler Ansicht sind Navigation und Inspector wechselweise aufklappbar.
Version und Status stehen in Hover- und Tastaturfokusdetails statt einer zusätzlichen
Versionszeile. Wortmarkenfarben folgen `assets/design/wordmarks/AgentAuthority-*.svg`.
DE/EN nutzt den bestehenden Katalog. Das Original-ICNS wird als `CFBundleIconFile`
in das lokale Bundle eingebunden; Dock-/Finder-Laufzeitabnahme ist separat.

Der eigene native Host startet direkt, ohne Shell:
`~/.local/bin/kirabridge --principal local family switch TARGET --source-pid EIGENER_NATIVE_PID`.
Nur `kirabridge`, `threaddesk`, `4allpass`, `tollgate`, `agent-authority` sind zulässig.
Die frische Bindung von PID/Startzeit/Installpfad/UID/NativeCaller und der erneute
Effektpunktcheck gehören zum Broker. AA übergibt keine Browserpfade, URLs oder Kommandos.
Erfolg erfordert Exit 0 und JSON mit `success:true`, passender `active_product`,
endlichen `actual_outer_bounds` (positive Breite/Höhe) und `visible_family_windows:1`.
Fehler, unvollständige Antworten und Zeitüberschreitungen sind unbestätigt; kein Blind-Replay.
Doppelklicks werden nicht als weitere Wechsel eingereiht. Der Broker setzt die äußeren
Bounds und zeigt/fokussiert das Ziel, bevor er andere registrierte Familienfenster verbirgt.
AA selbst schließt, lädt oder startet beim Wechsel keine Produktoberfläche neu.
Reopen verwendet das gespeicherte Hauptfenster statt `NSApp.mainWindow`;
identische installierte Executables wählen bei konkurrierenden Starts deterministisch die ältere Instanz.
Historische Bundles an anderen Pfaden bleiben getrennt. Sicherheitsdialoge blockieren
den AA-Wechsel. 4AllPass-Sperrregeln und alle bisherigen Beobachtungsgrenzen bleiben erhalten.
AA erhält keine Approve-/Stop-/Grant-Funktion. Alle 20 Produktwechsel und die gemeinsame
Geometrie benötigen nach der Integration eine eigene native Abnahme.

**English:** This reuses the existing AppKit renderer and pinned original assets, with
32-point artwork, 44×44 targets, centered icons, original two-color wordmark and visible
DE/EN. Version/status details are available on hover and keyboard focus. The original
ICNS is embedded in the bundle. No framework migration or new icon motif is involved.
The native host invokes the fixed broker argv above with its own PID, never a shell.
Success requires the complete JSON evidence described above, not just exit 0. Failures,
missing broker and unknown outcomes never become connectivity or automatic retries.
The broker owns identity validation, equal outer bounds and show/focus/hide across the
registered family. Reopen uses the stored main window; Hide preserves the state and
collector, whereas normal Close/Quit is unchanged. An identical installed executable
is not retained as a second running instance. No approval, stop or grant capability is
added. Cross-product geometry, lifecycle and 4AllPass lock-policy acceptance remain
integration gates, not claims from isolated AA tests.

Local Intel build using an existing pinned Python runtime, without installing:

```sh
python3.12 native/macos/scripts/build_app.py \
  --runtime-python /path/to/existing/standalone/python/bin/python3.12 \
  --output native/macos/build/family-design-20261112
```

Bundle: `native/macos/build/family-design-20261112/Agent Authority.app`.
Executable: `Contents/MacOS/AgentAuthorityMac`. Ad-hoc development signing does not
qualify the Endpoint Security collector. No permission prompts/activation are needed
for these synthetic UI checks:

```sh
swift test --package-path native/macos --filter 'FamilyDesignTests|StartupTests|InspectorFilterTests'
python3.12 native/macos/scripts/check_sources.py
python3.12 native/macos/scripts/check_ui_regressions.py \
  --executable "native/macos/build/family-design-20261112/Agent Authority.app/Contents/MacOS/AgentAuthorityMac" \
  --output /tmp/aa-family-ui-regression
```

The private repository's native CI job requires an operator-owned Intel macOS runner;
it does not request a GitHub-hosted Mac. No runner installation or production app
installation is performed by this source change.
