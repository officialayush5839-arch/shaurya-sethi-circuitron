# Wilo Water Pump Automation Receiver PCB Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a production-ready, fully validated SKiDL circuit model, KiCad schematic, netlist, SVG preview, and PCB layout for the Wilo Water Pump Automation Receiver Station HAT.

**Architecture:** The design implements a dual-zone high-voltage isolation HAT for Raspberry Pi Zero 2W. It integrates the SX1278 433MHz LoRa transceiver, ADS1115 16-bit I2C ADC, ACS712T-30A current sensor, ZMPT101B AC voltage transformer conditioning circuit, dual optocoupled 10A relays, and tactile manual controls with clean 5V/3.3V power rails.

**Tech Stack:** Python 3.11+, SKiDL 3.0, KiCad 10 / KiCad CLI, Pytest.

**Spec:** `docs/superpowers/specs/2026-10-25-wilo-receiver-pcb-design.md`

## Global Constraints
- Target Controller: Raspberry Pi Zero 2W standard 40-pin 2x20 GPIO interface.
- SPI0 Pinout: MOSI=GPIO10, MISO=GPIO9, SCLK=GPIO11, CE0=GPIO8, RST=GPIO25, DIO0=GPIO24.
- I2C1 Pinout: SDA=GPIO2, SCL=GPIO3 with 4.7kΩ pull-ups to 3.3V rail.
- Relay Controls: Primary Pump=GPIO17 (active-LOW via PC817+NPN buffer), Aux Valve=GPIO27.
- Buttons & LEDs: Force ON=GPIO22, Force OFF=GPIO5, Pump LED=GPIO6.
- High-voltage isolation: Minimum 5.0mm creepage clearance between AC mains and DC low-voltage traces.

## Review Focus
1. **Unconnected Pins**: Any floating unused analog input or floating reset line must be safely terminated or tied.
2. **LoRa 3.3V Power Sizing**: SX1278 must be supplied strictly from the dedicated 3.3V LDO (`+3V3_LORA`) and never directly from 5V or noisy MCU rails.
3. **Relay Failsafe Inversion**: Optocoupler inputs must be buffered via an NPN switching stage to ensure guaranteed 0V true-off state without 3.3V-to-5V threshold ghosting.
4. **Current Trace Carrying Capacity**: ACS712 and relay contact traces must support continuous 10A current draw.
5. **Netlist & Symbol Footprint Compatibility**: Every component in the SKiDL model must specify a valid, standard KiCad footprint for seamless PCB layout generation.

---

### Task 1: Receiver Circuit SKiDL Netlist & Model Definitions

**Files:**
- Create: `circuitron/circuits/wilo_receiver.py`
- Create: `tests/test_wilo_receiver.py`

**Interfaces:**
- Produces: `create_wilo_receiver_circuit() -> Circuit` returning the complete SKiDL circuit containing all parts, nets, and footprints.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_wilo_receiver.py
from circuitron.circuits.wilo_receiver import create_wilo_receiver_circuit

def test_wilo_receiver_circuit_components():
    circuit = create_wilo_receiver_circuit()
    part_names = {p.ref for p in circuit.parts}
    expected_parts = {"J1", "U_LORA", "U1", "U2", "U3", "T1", "U4", "U5", "U6", "K1", "K2", "SW1", "SW2"}
    assert expected_parts.issubset(part_names)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& .venv\Scripts\python.exe -m pytest tests/test_wilo_receiver.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'circuitron.circuits'`

- [ ] **Step 3: Implement `create_wilo_receiver_circuit` in `circuitron/circuits/wilo_receiver.py`**

Define SKiDL parts, power nets (`+5V`, `+3V3_RPI`, `+3V3_LORA`, `GND`, `AC_L`, `AC_N`), signal nets (`SPI0_*`, `I2C_*`, `RELAY*`, `BTN*`, `LED*`), and all interconnections according to the specification.

- [ ] **Step 4: Run test to verify it passes**

Run: `& .venv\Scripts\python.exe -m pytest tests/test_wilo_receiver.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add circuitron/circuits/wilo_receiver.py tests/test_wilo_receiver.py
git commit -m "feat: Add Wilo receiver SKiDL circuit definition and component tests"
```

---

### Task 2: Pin Mapping & Signal Net Verification

**Files:**
- Modify: `tests/test_wilo_receiver.py`
- Modify: `circuitron/circuits/wilo_receiver.py`

**Interfaces:**
- Consumes: `create_wilo_receiver_circuit()` from Task 1

- [ ] **Step 1: Write the failing test for pin connectivity**

```python
def test_pin_connectivity():
    circuit = create_wilo_receiver_circuit()
    j1 = next(p for p in circuit.parts if p.ref == "J1")
    # Verify RPi Pin 3 (SDA) is connected to Net I2C_SDA
    sda_net = j1[3].net
    assert sda_net.name == "I2C_SDA"
    # Verify RPi Pin 24 (CE0) is connected to LoRa NSS
    ce0_net = j1[24].net
    assert ce0_net.name == "SPI0_CE0"
    # Verify RPi Pin 11 (Relay 1)
    relay_net = j1[11].net
    assert relay_net.name == "RELAY1_CTRL"
```

- [ ] **Step 2: Run test to verify it fails or validates correct connections**

Run: `& .venv\Scripts\python.exe -m pytest tests/test_wilo_receiver.py::test_pin_connectivity -v`  

- [ ] **Step 3: Implement or refine pin bindings in `circuitron/circuits/wilo_receiver.py`**

Ensure all 40 RPi GPIO pins, LoRa SPI pins, I2C ADC lines, relay drivers, buttons, and status LEDs match the spec verbatim.

- [ ] **Step 4: Run test to verify it passes**

Run: `& .venv\Scripts\python.exe -m pytest tests/test_wilo_receiver.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add circuitron/circuits/wilo_receiver.py tests/test_wilo_receiver.py
git commit -m "test: Verify exact GPIO and bus net connectivity for receiver circuit"
```

---

### Task 3: SKiDL Electrical Rules Check (ERC) & Validation

**Files:**
- Modify: `tests/test_wilo_receiver.py`
- Modify: `circuitron/circuits/wilo_receiver.py`

**Interfaces:**
- Consumes: `circuit.ERC()` from SKiDL

- [ ] **Step 1: Write the failing test for ERC validation**

```python
def test_wilo_receiver_erc():
    from circuitron.circuits.wilo_receiver import validate_wilo_receiver_erc
    errors, warnings = validate_wilo_receiver_erc()
    assert errors == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& .venv\Scripts\python.exe -m pytest tests/test_wilo_receiver.py::test_wilo_receiver_erc -v`  

- [ ] **Step 3: Implement `validate_wilo_receiver_erc` and fix pin drive types / unattached pins**

Add no-connect (`NC`) designations to unused ADC and header pins; set appropriate power-in (`pwr_in`) and power-out (`pwr_out`) pin properties so SKiDL ERC reports 0 errors.

- [ ] **Step 4: Run test to verify it passes**

Run: `& .venv\Scripts\python.exe -m pytest tests/test_wilo_receiver.py::test_wilo_receiver_erc -v`  
Expected: PASS (0 errors)

- [ ] **Step 5: Commit**

```bash
git add circuitron/circuits/wilo_receiver.py tests/test_wilo_receiver.py
git commit -m "fix: Pass SKiDL Electrical Rules Check with zero errors"
```

---

### Task 4: Artifact Generation (KiCad Schematic, Netlist & SVG Preview)

**Files:**
- Create: `scripts/generate_wilo_pcb.py`
- Create: `tests/test_artifact_generation.py`

**Interfaces:**
- Produces: Files in `output/wilo_receiver/` (`wilo_receiver.net`, `wilo_receiver.sch`, `wilo_receiver.kicad_pcb`, `wilo_receiver.svg`, `bom.csv`)

- [ ] **Step 1: Write the failing test for artifact generator**

```python
from pathlib import Path
from scripts.generate_wilo_pcb import build_receiver_artifacts

def test_receiver_artifacts_generated(tmp_path):
    output_dir = tmp_path / "receiver_out"
    build_receiver_artifacts(output_dir=str(output_dir))
    assert (output_dir / "wilo_receiver.net").exists()
    assert (output_dir / "bom.csv").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& .venv\Scripts\python.exe -m pytest tests/test_artifact_generation.py -v`  
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement `build_receiver_artifacts` in `scripts/generate_wilo_pcb.py`**

Invoke SKiDL's `generate_netlist()`, `generate_schematic()`, `generate_pcb()`, and export a formatted CSV BOM with designators, component values, footprints, and descriptions.

- [ ] **Step 4: Run test to verify it passes**

Run: `& .venv\Scripts\python.exe -m pytest tests/test_artifact_generation.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_wilo_pcb.py tests/test_artifact_generation.py
git commit -m "feat: Add artifact generation script for netlist, schematic, and BOM"
```

---

### Task 5: Physical Board Layout, DRC Verification & Documentation Guide

**Files:**
- Modify: `scripts/generate_wilo_pcb.py`
- Create: `docs/wilo_receiver_hardware_guide.md`
- Create: `collab_progress/2026-10-25-wilo-receiver-pcb.md`

**Interfaces:**
- Produces: Complete KiCad project folder with generated schematic and PCB layout files ready for PCB fabrication (JLCPCB / PCBWay) and assembly instructions.

- [ ] **Step 1: Execute `generate_wilo_pcb.py` to produce project files in `output/wilo_receiver/`**

Run: `& .venv\Scripts\python.exe scripts/generate_wilo_pcb.py`  
Verify files:
- `output/wilo_receiver/wilo_receiver.net`
- `output/wilo_receiver/wilo_receiver.sch`
- `output/wilo_receiver/wilo_receiver.kicad_pcb`
- `output/wilo_receiver/bom.csv`

- [ ] **Step 2: Write hardware assembly and PCB ordering guide in `docs/wilo_receiver_hardware_guide.md`**

Detail:
- PCB stackup and clearance specs (creepage slots, trace widths, copper thickness).
- Solder and assembly sequence (SMD ICs first, then passives, connectors, relays, and RPi header).
- Initial power-on checklist and smoke testing before plugging in the Raspberry Pi Zero 2W.

- [ ] **Step 3: Write collab progress note according to repository protocol**

Document changes, tests executed, and artifacts produced in `collab_progress/2026-10-25-wilo-receiver-pcb.md` and update `collab_progress/CHANGELOG.md`.

- [ ] **Step 4: Run full test suite to ensure clean passing state**

Run: `& .venv\Scripts\python.exe -m pytest tests/test_wilo_receiver.py tests/test_artifact_generation.py -v`  
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add output/ docs/wilo_receiver_hardware_guide.md collab_progress/
git commit -m "docs: Add hardware fabrication guide and project progress notes"
```
