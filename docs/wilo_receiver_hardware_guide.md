# Wilo Water Pump Automation — Receiver Station PCB Assembly & Hardware Guide

This document provides complete instructions for fabricating, assembling, testing, and deploying the **Receiver Station PCB** designed for the Wilo Water Pump Automation System.

---

## 1. Board Specifications & PCB Fabrication Parameters

When submitting the PCB design (`output/wilo_receiver/wilo_receiver.kicad_pcb`) to PCB fabricators (such as JLCPCB, PCBWay, or OSH Park), use the following manufacturing parameters:

| Parameter | Specification | Recommendation / Notes |
| :--- | :--- | :--- |
| **Dimensions** | $85.0\,\text{mm} \times 65.0\,\text{mm}$ | Fits Raspberry Pi Zero 2W mounting footprint |
| **Layer Count** | 2 Layers | Top (F.Cu) + Bottom (B.Cu) |
| **Board Material** | FR-4 Standard TG150–TG170 | High thermal and mechanical resistance |
| **Finished Copper Weight**| **2 oz (70µm)** | **Essential**: Carries up to 10A–15A continuous motor pump currents |
| **Board Thickness** | $1.6\,\text{mm}$ | Standard mechanical rigidity |
| **Solder Mask** | Matte Green or Black | Both sides |
| **Silkscreen** | White | Zone 1 & Zone 2 safety markings clearly printed |
| **Surface Finish** | **ENIG (Electroless Nickel Immersion Gold)** | Recommended for planar SMD solderability and RF performance |
| **Isolation Routing Slots**| Non-plated milled slots ($1.5\,\text{mm}$ width) | **Mandatory**: Prevents surface tracking and flashover between 230V AC and DC |

---

## 2. Dual-Zone Safety & High-Voltage Isolation

The PCB is strictly partitioned into two physical zones separated by a **$5\,\text{mm}$ creepage air gap slot**:

```
┌──────────────────────────────────────────────────┬───┬───────────────────────────────┐
│              ZONE 1: LOW-VOLTAGE DC              │ S │       ZONE 2: 230V AC         │
│  - 40-Pin Raspberry Pi Header (J1)               │ L │  - AC Mains Input (TB2)       │
│  - Semtech SX1278 433MHz Ra-02 Module (U_LORA)   │ O │  - ACS712T-30A Hall Sensor    │
│  - 50Ω SMA Female Antenna Connector (J_SMA)      │ T │  - ZMPT101B Transformer (T1)  │
│  - ADS1115 16-Bit I2C ADC (U2)                   │   │  - Songle 10A Relays (K1, K2) │
│  - AMS1117-3.3 Dedicated LDO Regulator (U1)      │ C │  - Actuator Load Outputs (TB3)│
│  - Manual Override Tactile Buttons (SW1, SW2)    │ U │                               │
│  - Status & Power LEDs (PUMP, 5V, 3.3V)          │ T │                               │
└──────────────────────────────────────────────────┴───┴───────────────────────────────┘
```

> [!CAUTION]
> **High-Voltage Safety Notice**:
> Under no circumstances should traces, solder bridges, or test probes cross the milled isolation slot. Always disconnect the 230V AC mains terminal (`TB2`) before servicing or reprogramming the Raspberry Pi.

---

## 3. Step-by-Step Soldering & Assembly Sequence

### Step 1: Surface Mount Devices (SMD ICs & Passives)
1. **LDO Regulator (`U1`)**: Solder the AMS1117-3.3 (SOT-223) and decoupling capacitors $C_1$ ($10\mu\text{F}$) and $C_2$ ($22\mu\text{F}$).
2. **Current Sensor (`U3`)**: Solder the Allegro ACS712ELCTR-30A-T (SOIC-8). Apply generous solder fillet to high-current pins 1, 2 and 3, 4.
3. **ADC (`U2`)**: Solder the ADS1115 (MSOP-10) and $4.7\,\text{k}\Omega$ pull-up resistors $R_{PU1}, R_{PU2}$.
4. **Op-Amp (`U4`)**: Solder the LM358 (SOIC-8) conditioning IC.
5. **Driver Transistors & Diodes**: Solder $Q_1, Q_2$ (MMBT3904 SOT-23) and flyback diodes $D_2, D_3$ (1N4007 SMA).
6. **Passives & LEDs**: Solder SMD 0805 resistors, filter capacitors, and status LEDs ($LED_{PUMP}, LED_{5V}, LED_{3V3}$).

### Step 2: Radio & Through-Hole Components (THT)
1. **Semtech SX1278 Module (`U_LORA`)**: Align the castellated pads of the Ra-02 module. Solder ground corner pads first, verify alignment, and solder remaining signals.
2. **SMA Antenna Connector (`J_SMA`)**: Solder the edge-mount female SMA connector. Ensure clean $50\,\Omega$ RF trace joint.
3. **Optocouplers (`U5`, `U6`)**: Solder the PC817 4-pin DIP packages.
4. **Relays (`K1`, `K2`)**: Solder the Songle SRD-05VDC-SL-C power relays. Ensure complete pin wetting on the 10A contact pins.
5. **Voltage Transformer (`T1`)**: Solder the ZMPT101B micro-transformer and high-voltage resistors $R_{HV1}, R_{HV2}$ ($41.2\,\text{k}\Omega$ 1W each).
6. **Screw Terminals (`TB1`, `TB2`, `TB3`)**: Solder the heavy-duty $5.08\,\text{mm}$ pitch terminal blocks.
7. **Tactile Push Buttons (`SW1`, `SW2`)**: Solder the 6mm momentary buttons.
8. **Raspberry Pi Header (`J1`)**: Solder the $2\times 20$ female pin socket header on the underside or top as desired.

---

## 4. Pre-Power Checklist & Smoke Testing

Before seating the Raspberry Pi Zero 2W or connecting 230V mains:

1. **Short Circuit Inspection**:
   - Check resistance between `+5V` and `GND` with a digital multimeter (must be $> 10\,\text{k}\Omega$).
   - Check resistance between `+3V3_LORA` and `GND` (must be $> 1\,\text{k}\Omega$).
   - Check resistance between `AC_L_IN` and `GND` (must be infinite / open-circuit).
2. **Low-Voltage Power Verification**:
   - Apply $+5.0\,\text{V DC}$ to terminal block `TB1`.
   - Verify green `LED_5V` lights up.
   - Measure voltage at `U1` output: must read $3.30\,\text{V} \pm 0.05\,\text{V}$.
   - Verify blue `LED_3V3` lights up.
3. **RF Antenna Pre-Caution**:
   - **Attach a 433 MHz SMA antenna** to `J_SMA` before powering on or testing packet reception. Never operate without an antenna attached.
4. **Raspberry Pi Docking**:
   - Disconnect power, seat the Raspberry Pi Zero 2W firmly onto header `J1`, and re-apply 5V.
   - Run `ls -l /dev/spidev0.* /dev/i2c-1` and `sudo i2cdetect -y 1`. Address `0x48` (ADS1115) must be visible.

---

## 5. File Manifest

The generated design files in `output/wilo_receiver/` are ready to open in KiCad 10:

- **`wilo_receiver.kicad_pcb`**: Complete KiCad PCB layout with dual-zone placement, creepage slots, mounting holes, and routed nets.
- **`wilo_receiver.kicad_sch`** & **`wilo_receiver.sch`**: KiCad schematic with full pinout and symbols.
- **`wilo_receiver.net`**: Formal KiCad netlist.
- **`bom.csv`**: Complete bill of materials ready for component procurement.
