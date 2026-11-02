# Circuitron Changelog (collab_progress index)

## Purpose
- This file is the single, ordered index of all progress notes under collab_progress.
- It makes recent changes easy to find and links each entry to the detailed Markdown note(s).

## Rules
- Always append a new entry at the TOP after every task/change (feature, fix, refactor, tests, docs).
- Include Date and Time (prefer ISO 8601, UTC). Example: 2025-08-08T14:32Z
	To get the current time and date in the correct format, run this in PowerShell:
  
			Get-Date -Format o

- Keep the Summary concise; link to detailed files for depth.
- Reference the branch/PR when applicable.
- Do not remove or rewrite past entries; corrections should be a new entry.

Entry Template
- Copy/paste and fill all fields. Keep newest entries at the top.

```
## [Title]: Short description of the change
- Date: YYYY-MM-DD
- Time (UTC): HH:MMZ
- Branch/PR: <branch-name> (<PR link> if available)
- Files Changed (high level): <modules or folders>
- Details: See <relative-links-to-detailed-notes.md>
- Verification: <tests run, tools, results>
- Notes: <optional follow-ups/known issues>
```

### [Receiver PCB Fix]: Footprint Coordinate Offset Resolution & Full 3D Model Linking
- Date: 2026-11-02
- Time (UTC): 06:48Z
- Branch/PR: main
- Files Changed (high level): scripts/generate_wilo_pcb.py, output/wilo_receiver/
- Details: See [receiver-pcb-usbc-and-transient-upgrade-02-11-2026.md](receiver-pcb-usbc-and-transient-upgrade-02-11-2026.md)
- Verification: `kicad-cli pcb render --quality high` raytraced 3D render (iso 565 KB, top 306 KB), `pytest -q` (9 passed 100%)
- Notes: Diagnosed root cause of empty 3D board: footprints in cache contained redundant `(at 0 0)` tags that overrode the placement coordinates. Fixed `_load_and_embed_footprint` to strip redundant offsets, re-linked all 22 3D STEP models to `E:/kicad/share/kicad/3dmodels`, and added silkscreen labels (`gr_text`) for every component across Zone 1 and Zone 2.

### [Receiver Companion Firmware]: Sensor Calibration & Safety Protection Algorithms
- Date: 2026-11-02
- Time (UTC): 06:35Z
- Branch/PR: main
- Files Changed (high level): scripts/companion_firmware/, tests/test_companion_firmware.py
- Details: See [receiver-pcb-usbc-and-transient-upgrade-02-11-2026.md](receiver-pcb-usbc-and-transient-upgrade-02-11-2026.md)
- Verification: `pytest -q` (9 passed across hardware and firmware test suites)
- Notes: Implemented `tank_config.py` with all hardware pin assignments and safety constants, `calibrate_voltage.py` for True-RMS ZMPT101B scaling, `measure_current.py` with stateful dry-run (< 1.5A for > 2s) and overload (> 13.7A for > 3s) protection timers.

### [Receiver PCB Component Audit & Protection Hardening]: Optocoupler Drivers, LED Resistors, ACS712 Decoupling & Dual EMI Architecture
- Date: 2026-11-02
- Time (UTC): 06:30Z
- Branch/PR: main
- Files Changed (high level): circuitron/circuits/wilo_receiver.py, scripts/, tests/, output/wilo_receiver/
- Details: See [receiver-pcb-usbc-and-transient-upgrade-02-11-2026.md](receiver-pcb-usbc-and-transient-upgrade-02-11-2026.md)
- Verification: `pytest -q` (4 passed in 9.82s), SKiDL ERC 0 errors, KiCad 10 raytraced renders (`kicad-cli pcb render --quality high`)
- Notes: Verified all requested components (ZMPT101B, dual relays, snubber vs optocoupler analysis, CT clamp 3.5mm socket, voltage divider resistors, 33-ohm burden resistor, DC bias network, USB Type-C female connector). Added missing optocoupler input series resistors (470 ohm), NPN base drive resistors (1k ohm) and pull-down resistors (10k ohm), LED series resistors (470 ohm for 5V, 330 ohm for 3.3V), and 0.1uF ACS712 VCC decoupling capacitor.

### [Receiver PCB Upgrade]: USB Type-C Power Input, Filtering Decoupling, CT Clamp Audio Interface, Relay Transient Protection & KiCad 10 3D Raytracing
- Date: 2026-11-02
- Time (UTC): 06:10Z
- Branch/PR: main
- Files Changed (high level): circuitron/circuits/wilo_receiver.py, scripts/, tests/, output/wilo_receiver/
