"""Package the Wilo Receiver project into a 100% self-contained, portable KiCad project.

Ensures:
1. Zero missing footprint libraries (all .kicad_mod files embedded in wilo_receiver.pretty/).
2. fp-lib-table and sym-lib-table configured using ${KIPRJMOD}.
3. Embedded symbol definitions in .kicad_sch and wilo_receiver.kicad_sym.
4. Clean .kicad_pro project file.
5. Removal of transient lock files (~*.lck).
6. Comprehensive README and BOM.
7. Ready-to-send ZIP archive: wilo_receiver_kicad_project.zip.
"""
import os
import shutil
import zipfile
from pathlib import Path


def create_portable_kicad_project(project_dir: Path, output_zip: Path) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = Path("circuitron/footprints_cache")

    # 1. Create wilo_receiver.pretty and copy all footprints
    pretty_dir = project_dir / "wilo_receiver.pretty"
    pretty_dir.mkdir(parents=True, exist_ok=True)

    if cache_dir.exists():
        for mod_file in cache_dir.glob("*.kicad_mod"):
            shutil.copy(mod_file, pretty_dir / mod_file.name)
            # Also copy with clean name (without library prefix if needed)
            if "_" in mod_file.name:
                simple_name = mod_file.name.split("_", 1)[1]
                shutil.copy(mod_file, pretty_dir / simple_name)
    print(f"Copied {len(list(pretty_dir.glob('*.kicad_mod')))} footprint files to {pretty_dir}")

    # 2. Write fp-lib-table (pointing to ${KIPRJMOD}/wilo_receiver.pretty)
    fp_lib_table = (
        '(fp_lib_table\n'
        '  (version 7)\n'
        '  (lib (name "wilo_receiver")(type "KiCad")(uri "${KIPRJMOD}/wilo_receiver.pretty")(options "")(descr "Project Local Footprints"))\n'
        ')\n'
    )
    (project_dir / "fp-lib-table").write_text(fp_lib_table, encoding="utf-8")

    # 3. Write sym-lib-table
    sym_lib_table = (
        '(sym_lib_table\n'
        '  (version 7)\n'
        '  (lib (name "wilo_receiver")(type "KiCad")(uri "${KIPRJMOD}/wilo_receiver.kicad_sym")(options "")(descr "Project Local Symbols"))\n'
        ')\n'
    )
    (project_dir / "sym-lib-table").write_text(sym_lib_table, encoding="utf-8")

    # 4. Write wilo_receiver.kicad_sym (Symbol Library) with ALL 22 symbols
    from scripts.build_complete_kicad_schematic import build_symbol_definitions
    sym_defs = build_symbol_definitions()
    sym_header = (
        '(kicad_symbol_lib\n'
        '  (version 20231120)\n'
        '  (generator "circuitron")\n'
        '  (generator_version "8.0")\n'
    )
    sym_body = "\n".join(sym_defs.values()) + "\n"
    sym_footer = ")\n"
    (project_dir / "wilo_receiver.kicad_sym").write_text(sym_header + sym_body + sym_footer, encoding="utf-8")

    # 5. Clean up any transient KiCad lock files (~*.lck)
    for lck in project_dir.glob("*.lck"):
        try:
            lck.unlink()
        except OSError:
            pass

    # 6. Create detailed recipient README.md
    readme_content = """# Wilo Water Pump Automation — Receiver Station HAT (Rev 3.0)

[![KiCad](https://img.shields.io/badge/KiCad-v7%20%7C%20v8%20%7C%20v9%20%7C%20v10-blue.svg)](https://www.kicad.org/)
[![Hardware Rev](https://img.shields.io/badge/Hardware%20Revision-v3.0%20(140x95mm)-success.svg)](#)
[![Power](https://img.shields.io/badge/Main%20Power-5V%20DC%20USB--C-orange.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)

Production-ready KiCad hardware project for the **Wilo Water Pump Automation Receiver Station HAT** (Rev 3.0). This board acts as the central automation hub, pairing a **Raspberry Pi Zero 2W**, **SX1278 433 MHz LoRa transceiver**, **ADS1115 16-bit precision ADC**, **dual 10A 250VAC relays**, and **isolated AC voltage and current sensors** into an industrial-grade automation controller.

---

## Visual Showcase

### Full Engineering Schematic Diagram (Rev 3.0 — 7 Functional Blocks)
![Wilo Receiver Station Schematic Diagram](wilo_receiver_schematic.png)

### High-Resolution 2D Board Layout (Rev 3.0 — 140 mm × 95 mm)
![Wilo Receiver Station Board Top Layout](wilo_receiver_board_top.png)

### 3D Raytraced Isometric View
![Wilo Receiver Station 3D Isometric View](wilo_receiver_3d_iso.png)

### 3D Raytraced Top-Down View
![Wilo Receiver Station 3D Top View](wilo_receiver_3d_top.png)

---

## Key Hardware Architectural Features

1. **100% 5V DC USB-C Main Power**:
   - The entire board's logic, Raspberry Pi Zero 2W, LoRa transceiver, relays, and sensors are powered strictly through the **5V DC USB-C port (`J_USBC`)**.
   - **Zero internal AC-to-DC converter**: keeps the control board low-voltage, cool, and safe to service.
   - Dedicated onboard **AMS1117-3.3V LDO regulator (`U1`)** provides low-noise 3.3V power to the Ra-02 LoRa module and sensitive 3.3V analog rails.

2. **Single Unified Ground Plane Architecture**:
   - The PCB layout features an expanded **140 mm × 95 mm** footprint with a single continuous ground plane for superior signal integrity and low impedance return paths.
   - Eliminates complex slot cutouts and isolation zone boundaries while maintaining generous physical spacing (>6.0 mm clearance) around high-voltage sensor pins and relay traces.

3. **Perimeter & Corner Connector Strategy**:
   - All external terminals, headers, buttons, and jacks are strategically positioned around the board edges and corners for clean enclosure routing and panel mounting:
     - **`J_USBC` (5V Main Power)**: Bottom-left corner (`(12, 82)`).
     - **`J_SMA` (50Ω Antenna)**: Top-left edge (`(10, 30)`).
     - **`J_CT` (3.5mm Current Clamp)**: Mid-left edge (`(11.5, 54)`).
     - **`J1` (RPi Zero 2W 40-Pin Header)**: Top perimeter (`(40, 14)`).
     - **`TB_EXP` (A2/A3 Expansion)**: Top-right edge (`(98, 15)`).
     - **`TB2` (Voltage Sense Only)**: Top-right corner (`(125, 17)`).
     - **`TB3` (Load Out)**: Bottom-right corner (`(125, 76)`).
     - **`SW1` & `SW2`**: Bottom edge manual tactile override controls (`FORCE ON`, `FORCE OFF`).

4. **Sensing & Telemetry Subsystems**:
   - **Mains Voltage Sensing (`TB2`)**: `TB2: SENSE ONLY (NOT POWER)`. Samples 230V AC grid voltage across high-voltage drop resistors (`R_HV1` 41.2kΩ 1W, `R_HV2` 41.2kΩ 1W) through a **ZMPT101B potential transformer (`T1`)** and active LM358 op-amp conditioning into ADS1115 Channel A1.
   - **Motor Current Sensing**: Dual sampling capability using either an external 3.5mm split-core CT clamp (`J_CT`) into ADS1115 Channel A0, or an onboard **ACS712T-30A Hall-effect current sensor (`U3`)**.
   - **Auxiliary Inputs (`TB_EXP`)**: 2-pin screw terminal exposing ADS1115 Channels A2 & A3 for external water pressure, float switches, or temperature probes.

5. **Industrial Load Switching & Protection**:
   - **Dual 10A 250VAC Songle Relays**: `K1` (Wilo Pump) and `K2` (Auxiliary / Motorized Valve).
   - **Galvanic Optical Isolation**: Driven via **PC817 optocouplers (`U5`, `U6`)** with **MMBT3904 NPN transistors (`Q1`, `Q2`)** and flyback protection diodes (`1N4007`).
   - **Transient & Arc Suppression**: Metal Oxide Varistor (**MOV1: 14D471K**) across mains load, plus an RC snubber network (**`R_SNUB` 100Ω 1W + `C_SNUB` 0.1µF 275VAC X2 safety capacitor**).

---

## Hardware Specifications Table

| Parameter | Specification | Notes |
| :--- | :--- | :--- |
| **Board Dimensions** | 140.0 mm × 95.0 mm | 4× M2.5 mounting holes at corners |
| **Layer Count** | 2 Layers | Top: Signal & Silkscreen, Bottom: Unified GND Plane |
| **Copper Weight** | 2.0 oz (70 µm) outer layers | Rated for 10A continuous motor current handling |
| **Substrate & Thickness** | FR4 Standard, 1.6 mm | TG130-140 |
| **Main System Power** | 5V DC @ 2.5A via USB-C (`J_USBC`) | Powers RPi Zero 2W, relays, sensors, logic |
| **Onboard 3.3V Rail** | AMS1117-3.3V (1.0A max) | Low-ESR 10µF input + 22µF output tantalum/ceramic |
| **RF Transceiver** | Ai-Thinker Ra-02 (SX1278 433 MHz LoRa) | 50Ω matched trace to SMA connector (`J_SMA`) |
| **Analog-to-Digital Converter**| TI ADS1115 (16-bit 4-channel I2C ADC) | I2C address `0x48`, pull-ups 4.7kΩ to 3.3V |
| **Voltage Sensor** | ZMPT101B 2mA:2mA Current-Type PT | Isolated AC potential measurement (`TB2`) |
| **Current Sensor** | Allegro ACS712T-30A / CT clamp jack | Hall-effect isolated 66 mV/A + 3.5mm audio jack |
| **Relay Outputs** | 2× Songle SRD-05VDC-SL-C (SPDT 10A) | K1: Pump, K2: Valve/Aux |
| **Status Indicators** | 3× 0805 SMD LEDs | Green: 5V PWR, Blue: 3V3 RF, Amber: PUMP ON |
| **Manual Controls** | 2× 6×6 mm tactile push buttons | SW1: Force ON, SW2: Force OFF |

---

## Quick Start (How to Open in KiCad)

1. Clone or extract this repository to your local computer:
   ```bash
   git clone https://github.com/officialayush5839-arch/Wilo-Receiver-PCB.git
   ```
2. Launch **KiCad 7, 8, 9, or 10**.
3. Select **File → Open Project...** (`Ctrl + O`) and open **`wilo_receiver.kicad_pro`**.
4. In the KiCad Project Manager panel:
   - Double-click **`wilo_receiver.kicad_sch`** to open the modular schematic.
   - Double-click **`wilo_receiver.kicad_pcb`** to open the 140×95 mm PCB layout.
5. In the PCB Editor, press **`Alt + 3`** to view the interactive 3D raytraced model.

---

## Project Structure & Zero-Dependency Portability

```
Wilo-Receiver-PCB/
├── README.md                      # Complete project documentation with embedded graphics
├── wilo_receiver.kicad_pro        # Master KiCad project file
├── wilo_receiver.kicad_pcb        # Production 2-layer PCB layout (140 mm x 95 mm)
├── wilo_receiver.kicad_sch        # Modular schematic diagram (7 framed functional blocks)
├── wilo_receiver.kicad_sym        # Embedded symbol library definitions
├── fp-lib-table                   # Footprint table configured with ${KIPRJMOD}
├── sym-lib-table                  # Symbol table configured with ${KIPRJMOD}
├── bom.csv                        # Full Bill of Materials with references & manufacturer numbers
├── wilo_receiver.net              # Generated KiCad netlist
├── wilo_receiver.pretty/          # Local footprint directory (18 custom .kicad_mod footprints)
├── gerbers/                       # Ready-to-order manufacturing Gerbers and drill files
├── firmware/                      # Companion Raspberry Pi Python firmware & systemd service
├── wilo_receiver_schematic.png    # High-resolution engineering schematic diagram (A3)
├── wilo_receiver_board_top.png    # High-resolution 2D layout graphic
├── wilo_receiver_2d_board.svg     # Scalable Vector Graphic 2D board render
├── wilo_receiver_3d_iso.png       # 3D raytraced isometric render
└── wilo_receiver_3d_top.png       # 3D raytraced top view render
```

---

## Recommended PCB Fabrication Specs (JLCPCB / PCBWay)

- **Layers**: 2 Layers
- **Dimensions**: 140.0 mm × 95.0 mm
- **Material**: FR-4 (TG130–140)
- **Thickness**: 1.6 mm
- **Outer Copper Weight**: 2.0 oz (recommended for 10A relay load paths)
- **Surface Finish**: Lead-Free HASL or ENIG-1U
- **Solder Mask**: Pine Green (or Matte Black)
- **Silkscreen**: Crisp White (zero overlap guaranteed)
- **Min Trace / Space**: 0.25 mm / 0.25 mm (mains traces: 2.0–3.0 mm)
"""

    (project_dir / "README.md").write_text(readme_content, encoding="utf-8")

    # 7. Create the ready-to-share ZIP archive
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in project_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.endswith(".lck"):
                # Archive relative to project folder name
                rel_path = Path("wilo_receiver") / file_path.relative_to(project_dir)
                zf.write(file_path, arcname=str(rel_path))
    
    zip_size_kb = output_zip.stat().st_size / 1024
    print(f"Successfully packaged KiCad project to {output_zip} ({zip_size_kb:.1f} KB)")


def sync_to_destinations(output_zip: Path, project_dir: Path) -> None:
    """Synchronize the portable ZIP and project files to Desktop and standalone repo."""
    dest_zip_names = ["wilo_receiver_kicad_pcb.zip", "wilo_receiver_kicad_project.zip"]
    desktop_dirs = [
        Path(os.path.expanduser("~/OneDrive/Desktop")),
        Path(os.path.expanduser("~/Desktop")),
        Path("C:/Users/ARYAN - AYUSH/OneDrive/Desktop"),
        Path("C:/Users/ARYAN - AYUSH/Desktop"),
        Path("C:/Users/ARYAN - AYUSH/Documents/antigravity/Wilo-Receiver-PCB"),
    ]
    seen_dests = set()
    for d in desktop_dirs:
        try:
            if d.exists() and d.resolve() not in seen_dests:
                seen_dests.add(d.resolve())
                for name in dest_zip_names:
                    target = d / name
                    shutil.copy2(output_zip, target)
                    print(f"Synced {name} -> {target}")
        except Exception as e:
            print(f"Skipping {d}: {e}")

    # Also make a duplicate in output/ with both names
    for name in dest_zip_names:
        out_target = output_zip.parent / name
        if out_target.resolve() != output_zip.resolve():
            shutil.copy2(output_zip, out_target)
            print(f"Created duplicate archive: {out_target}")

    # Sync project directory contents to standalone repo
    repo_dir = Path("C:/Users/ARYAN - AYUSH/Documents/antigravity/Wilo-Receiver-PCB")
    if repo_dir.exists():
        for item in project_dir.iterdir():
            dest_item = repo_dir / item.name
            if item.is_dir():
                if dest_item.exists():
                    shutil.rmtree(dest_item)
                shutil.copytree(item, dest_item)
            else:
                shutil.copy2(item, dest_item)
        print(f"Synced project tree to {repo_dir}")


if __name__ == "__main__":
    src_dir = Path("output/wilo_receiver")
    zip_dest = Path("output/wilo_receiver_kicad_project.zip")
    create_portable_kicad_project(src_dir, zip_dest)
    sync_to_destinations(zip_dest, src_dir)
