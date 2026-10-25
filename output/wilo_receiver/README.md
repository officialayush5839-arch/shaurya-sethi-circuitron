# Wilo Water Pump Automation Receiver Station — KiCad Hardware Project

This archive contains the complete, production-ready KiCad 7 / 8 / 9 / 10 hardware project for the **Wilo Water Pump Automation Receiver Station HAT** (120 mm × 85 mm).

---

## Quick Start (How to Open in KiCad)

1. Extract this entire zip folder to your desired location.
2. In **KiCad**, select **File → Open Project...** (`Ctrl + O`).
3. Select `wilo_receiver.kicad_pro`.
4. In the Project Manager panel:
   * Double-click **`wilo_receiver.kicad_pcb`** to open the PCB layout.
   * Double-click **`wilo_receiver.kicad_sch`** to open the Schematic.
5. In the PCB Editor, press **`Alt + 3`** to launch the interactive 3D raytraced viewer.

---

## Project Structure & Zero-Dependency Portability

* **`wilo_receiver.kicad_pro`**: Main project configuration file.
* **`wilo_receiver.kicad_pcb`**: 120 × 85 mm 2-layer PCB layout with 5 mm isolation creepage slots, complete component footprints, netlists, and 3D packages.
* **`wilo_receiver.kicad_sch`**: Schematic with symbols, pinouts, and net labels.
* **`fp-lib-table`**: Footprint library table pointing to local `${KIPRJMOD}/wilo_receiver.pretty`.
* **`sym-lib-table`**: Symbol library table pointing to local `${KIPRJMOD}/wilo_receiver.kicad_sym`.
* **`wilo_receiver.pretty/`**: Project-local footprint library containing all 18 `.kicad_mod` files (Relays, SX1278 LoRa, ZMPT101B transformer, terminal blocks, ICs, buttons, LEDs).
* **`bom.csv`**: Full Bill of Materials with quantities, footprint references, and manufacturer designations.
* **`wilo_receiver.net`**: Standard KiCad netlist.

---

## Hardware Specifications

* **Form Factor**: Raspberry Pi Zero 2W HAT (120 mm × 85 mm, dual-zone layout).
* **Isolation**: Dual-zone architecture:
  * **Zone 1 (0–5V DC Logic)**: Raspberry Pi Zero header, SX1278 433 MHz LoRa radio, ADS1115 16-bit ADC, AMS1117-3.3V LDO regulator, status LEDs, and manual override push buttons.
  * **Zone 2 (230V AC Mains & Power)**: 230V AC mains input, ZMPT101B potential transformer, Allegro ACS712T-30A Hall current sensor, dual 10A 250VAC Songle relays, and 3-pin pump/valve load terminal block.
  * **Barrier**: 5 mm creepage non-plated routing slots with PC817 optical isolation.
* **Recommended PCB Fabrication Specs**:
  * Layers: 2 Layers
  * Board Thickness: 1.6 mm
  * Copper Weight: 2.0 oz (70 µm) outer layers (recommended for 10A pump motor current handling)
  * Surface Finish: HASL lead-free or ENIG (Electroless Nickel Immersion Gold)
  * Solder Mask: Dark Green (or Matte Black)
  * Silkscreen: White
