# Wilo Water Pump Automation — Receiver Station PCB Design Specification

**Date**: 2026-10-25  
**Status**: Approved (Draft for Implementation)  
**Author**: Antigravity Assistant & Engineering Team  
**Reference Document**: `RECEIVER_GUIDE.md` (Wilo Water Pump Automation Receiver Specification)

---

## 1. Executive Summary & Purpose

The **Wilo Receiver Station PCB** is a specialized industrial Raspberry Pi Zero 2W HAT / Carrier Board designed for autonomous water pump control, long-range wireless telemetry reception, and power mains monitoring in residential/commercial pump rooms.

The board integrates:
1. **Semtech SX1278 LoRa 433 MHz Transceiver** (Ra-02 surface-mount module footprint) with matched $50\,\Omega$ SMA RF output.
2. **Texas Instruments ADS1115 16-Bit I2C ADC** for high-resolution sensor sampling.
3. **Allegro ACS712T-30A Hall-Effect AC Current Sensor** for motor current draw and dry-run detection ($2100\,\text{V RMS}$ galvanic isolation).
4. **ZMPT101B Precision AC Voltage Sensor & Active Op-Amp Conditioning** for continuous mains voltage monitoring.
5. **Dual 5V 10A Optocoupled Relay Drivers** (Primary Pump Relay on GPIO 17, Auxiliary/Inlet Valve Relay on GPIO 27) with true-off NPN isolation drivers and fail-safe Normally Open contacts.
6. **Hardware Manual Overrides & Status Indicators** (Tactile switches for Force ON and Force OFF with hardware debouncing; Pump Status LED and Power LEDs).
7. **Dual-Zone High-Voltage Isolation** with physical PCB routing slots, $5\,\text{mm}$ creepage clearance, and dedicated 3.3V LDO regulator.

---

## 2. System Architecture & Block Diagram

```
                                  +230V AC MAINS
                                         │
                 ┌───────────────────────┴────────────────────────┐
                 ▼                                                ▼
     ┌───────────────────────┐                        ┌───────────────────────┐
     │   ZMPT101B Voltage    │                        │  ACS712T-30A Current  │
     │     Transformer       │                        │     Sensor (Hall)     │
     └───────────┬───────────┘                        └───────────┬───────────┘
                 │ (Galvanic Isolation)                           │ (Magnetic Isolation)
                 ▼ (Scaled 0-5V AC)                               ▼ (2.5V ± 66mV/A)
     ┌────────────────────────────────────────────────────────────────────────┐
     │                       ADS1115 16-Bit I2C ADC                           │
     │                      (Channel A0: I, A1: V)                            │
     └───────────────────────────────────┬────────────────────────────────────┘
                                         │ I2C Bus (SDA / SCL @ 3.3V)
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Raspberry Pi Zero 2W (40-Pin Header)                     │
│                                                                             │
│  [SPI0] ──────────► SX1278 433 MHz LoRa Transceiver ──► 50Ω SMA Antenna     │
│  [GPIO 17] ───────► Optocoupler PC817 ──► NPN Driver ──► 10A Pump Relay     │
│  [GPIO 27] ───────► Optocoupler PC817 ──► NPN Driver ──► 10A Aux Relay      │
│  [GPIO 22] ◄────── Manual Force ON Button (Active-LOW + RC filter)         │
│  [GPIO 05] ◄────── Manual Force OFF Button (Active-LOW + RC filter)        │
│  [GPIO 06] ───────► Pump Status LED (Green)                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                         ▲
                                         │ Clean 3.3V / 5.0V
                 ┌───────────────────────┴────────────────────────┐
                 │  Power: 5V DC In (Terminal / USB) + 3.3V LDO   │
                 └────────────────────────────────────────────────┘
```

---

## 3. Detailed Circuit Schematics & Pin Mapping

### 3.1 40-Pin Raspberry Pi Header (`J1`)
Standard $2\times 20$ $2.54\,\text{mm}$ pitch receptacle connecting to the RPi Zero 2W:

| Pin | BCM Name | Net / Signal | Destination / Function |
| :---: | :---: | :---: | :--- |
| **1** | 3V3 | `+3V3_RPI` | Pull-ups for I2C lines ($4.7\,\text{k}\Omega$) |
| **2** | 5V | `+5V` | Primary Board 5V supply input from terminal |
| **3** | GPIO 2 | `I2C_SDA` | ADS1115 Pin 9 (SDA) |
| **4** | 5V | `+5V` | Secondary 5V tie |
| **5** | GPIO 3 | `I2C_SCL` | ADS1115 Pin 10 (SCL) |
| **6** | GND | `GND` | Ground return |
| **9** | GND | `GND` | Ground return |
| **11** | GPIO 17 | `RELAY1_CTRL` | PC817 Optocoupler 1 input (Pump Relay) |
| **13** | GPIO 27 | `RELAY2_CTRL` | PC817 Optocoupler 2 input (Aux Valve Relay) |
| **14** | GND | `GND` | Ground return |
| **15** | GPIO 22 | `BTN_FORCE_ON` | Tactile Push Button 1 (Active LOW with pull-up & 100nF cap) |
| **18** | GPIO 24 | `LORA_DIO0` | SX1278 Pin 14 (DIO0 Interrupt) |
| **19** | GPIO 10 | `SPI0_MOSI` | SX1278 Pin 10 (MOSI) |
| **20** | GND | `GND` | Ground return |
| **21** | GPIO 9 | `SPI0_MISO` | SX1278 Pin 9 (MISO) |
| **22** | GPIO 25 | `LORA_RST` | SX1278 Pin 12 (Hardware Reset) |
| **23** | GPIO 11 | `SPI0_SCLK` | SX1278 Pin 11 (SCK) |
| **24** | GPIO 8 | `SPI0_CE0` | SX1278 Pin 13 (NSS / Chip Select) |
| **25** | GND | `GND` | Ground return |
| **29** | GPIO 5 | `BTN_FORCE_OFF` | Tactile Push Button 2 (Active LOW with pull-up & 100nF cap) |
| **30** | GND | `GND` | Ground return |
| **31** | GPIO 6 | `LED_PUMP_RUN` | Green Status LED Anode (via $330\,\Omega$ resistor) |
| **34** | GND | `GND` | Ground return |
| **39** | GND | `GND` | Ground return |

---

### 3.2 Power Supply & Regulation
- **$5\,\text{V}$ Input**: 2-pin screw terminal block (`J_PWR`) or USB-C connector.
  - Reverse polarity protection: Schottky diode $D_1$ (SS34, 3A 40V).
  - Bulk filter: $C_1$ ($100\,\mu\text{F}$ 16V electrolytic), $C_2$ ($10\,\mu\text{F}$ ceramic), $C_3$ ($100\,\text{nF}$ ceramic).
- **Dedicated $3.3\,\text{V}$ LDO (`U1`)**:
  - Regulator: AMS1117-3.3 or AP2112K-3.3 ($500\,\text{mA}$ to $1\,\text{A}$ rating).
  - Input: $+5\,\text{V}$ from $D_1$ output.
  - Output capacitors: $C_4$ ($22\,\mu\text{F}$ ceramic) + $C_5$ ($100\,\text{nF}$ ceramic).
  - Dedicated net: `+3V3_LORA` powering the SX1278 RF module to prevent MCU brownout during packet transmission.

---

### 3.3 LoRa Transceiver Front-End (`U_LORA`)
- **Module**: Semtech SX1278 (Ra-02 surface-mount module footprint).
- **Supply**: Powered strictly from `+3V3_LORA`.
- **Decoupling**: $100\,\text{nF}$ and $10\,\mu\text{F}$ adjacent to module VDD pins.
- **RF Output**:
  - Controlled $50\,\Omega$ microstrip trace from RF pin.
  - Matching/filter $\pi$-network footprint pads ($0\,\Omega$ series link installed by default).
  - Standard edge-mount female SMA connector (`J_SMA`).

---

### 3.4 ADS1115 16-Bit I2C ADC (`U2`)
- **IC**: ADS1115IDGSR (MSOP-10 package).
- **Supply**: $+5\,\text{V}$ to enable full $0\text{--}5\,\text{V}$ dynamic analog range.
- **I2C Bus**: Connected to RPi GPIO 2 (`SDA`) and GPIO 3 (`SCL`) with $4.7\,\text{k}\Omega$ pull-up resistors to `+3V3_RPI`.
- **Address Pin (`ADDR`)**: Hardwired to `GND` to select I2C address `0x48`.
- **Analog Inputs**:
  - `A0`: Connected to ACS712T-30A current output via $1\,\text{k}\Omega / 100\,\text{nF}$ RC low-pass filter.
  - `A1`: Connected to ZMPT101B voltage output via $1\,\text{k}\Omega / 100\,\text{nF}$ RC low-pass filter.
  - `A2`, `A3`: Connected to test pad / expansion header with $100\,\text{nF}$ capacitor pads.

---

### 3.5 ACS712T-30A Current Sensor (`U3`)
- **IC**: Allegro ACS712ELCTR-30A-T (SOIC-8 package).
- **Primary Side (High Current AC)**:
  - Pins 1, 2 (`IP+`) tied together; Pins 3, 4 (`IP-`) tied together.
  - Connected between AC Mains Live input terminal and Pump Live terminal.
  - High-copper polygon pour ($\ge 120\,\text{mil}$ width, 2 oz copper recommended) to carry continuous pump currents up to $10\,\text{A}$ ($15\,\text{A}$ surge).
- **Secondary Side**:
  - Pin 5 (`GND`), Pin 8 (`VCC` tied to $+5\,\text{V}$ with $100\,\text{nF}$ decoupling).
  - Pin 6 (`FILTER` with $4.7\,\text{nF}$ noise suppression cap).
  - Pin 7 (`VIOUT` producing $2.5\,\text{V} \pm 66\,\text{mV/A}$).

---

### 3.6 ZMPT101B Precision Voltage Sensor (`T1` & `U4`)
- **Transformer**: ZMPT101B galvanic micro-transformer ($2\,\text{mA} / 2\,\text{mA}$).
- **Primary Side**:
  - In series with two $1\,\text{W}$ or $2\,\text{W}$ high-voltage metal-film resistors ($41\,\text{k}\Omega + 41\,\text{k}\Omega = 82\,\text{k}\Omega$) across AC Mains Live and Neutral.
- **Secondary Conditioning**:
  - Operational amplifier LM358 / MCP6002 powered by $+5\,\text{V}$.
  - Current-to-voltage feedback circuit with a multi-turn precision trimmer potentiometer ($50\,\text{k}\Omega$) for fine-calibrating AC voltage amplitude.
  - Mid-rail reference bias ($2.5\,\text{V}$) generated via a resistor divider ($10\,\text{k}\Omega / 10\,\text{k}\Omega$) with $10\,\mu\text{F}$ filtering.
  - Output feeds ADS1115 analog input `A1`.

---

### 3.7 Dual Optocoupled Relay Drivers (`K1`, `K2`)
- **Relays**: Songle SRD-05VDC-SL-C ($5\,\text{V}$ coil, $10\,\text{A } 250\,\text{V AC}$ contacts).
- **Optoisolation**: PC817 optocoupler per channel.
- **Driver Circuitry**:
  - Raspberry Pi GPIO (3.3V logic) drives the PC817 IR LED through a $330\,\Omega$ resistor.
  - Phototransistor output drives the base/gate of an NPN switching transistor (e.g. MMBT3904 / 2N2222) with a $10\,\text{k}\Omega$ pull-down resistor.
  - Eliminates the 3.3V/5V threshold leakage issue documented in Section 4 of the hardware guide.
  - Flyback protection diode: 1N4007 / SS14 placed in reverse parallel across each relay coil.
  - Contact configuration: Normally Open (`NO`) wired in series with the AC live conductor, guaranteeing fail-safe open circuit on complete power loss.

---

### 3.8 Manual Controls & Visual Feedback
- **Tactile Push Buttons**:
  - `SW1` (Force ON): Momentary switch pulling GPIO 22 to GND with a $10\,\text{k}\Omega$ pull-up to 3.3V and a $100\,\text{nF}$ debouncing capacitor.
  - `SW2` (Force OFF): Momentary switch pulling GPIO 5 to GND with a $10\,\text{k}\Omega$ pull-up to 3.3V and a $100\,\text{nF}$ debouncing capacitor.
- **LED Indicators**:
  - `LED_PUMP`: $3\,\text{mm}$ Green LED on GPIO 6 through $330\,\Omega$ resistor.
  - `LED_5V`: Green LED indicating primary $5\,\text{V}$ power active.
  - `LED_3V3`: Blue LED indicating regulated $3.3\,\text{V}$ radio rail active.

---

## 4. PCB Layout, Mechanical & Isolation Guidelines

1. **Board Dimensions**: $85\,\text{mm} \times 65\,\text{mm}$, 2-layer FR-4, $1.6\,\text{mm}$ thickness, 1 oz or 2 oz copper.
2. **Dual-Zone Partitioning**:
   - **Zone 1 (Low-Voltage DC)**: Located on the left side of the PCB, housing the RPi Zero 2W header, SX1278 module, ADS1115 ADC, LDO, push buttons, and LEDs.
   - **Zone 2 (High-Voltage AC Mains)**: Located on the right side of the PCB, housing the AC screw terminal blocks, ZMPT101B transformer, ACS712 primary traces, and relay contacts.
3. **High-Voltage Creepage Slots**:
   - $1.5\,\text{mm}$ to $2.0\,\text{mm}$ wide non-plated through-slots routed into the PCB under the optocouplers, ZMPT101B, ACS712, and relays.
   - Creepage distance exceeding $6.0\,\text{mm}$ between AC Live/Neutral traces and low-voltage DC planes.
4. **Current Trace Sizing**:
   - AC Live feed and pump output traces sized to at least $120\,\text{mil}$ ($3.0\,\text{mm}$) on 1 oz copper with exposed solder mask for optional solder tinning to safely conduct up to $10\,\text{A}$ continuously.
5. **RF Routing**:
   - $50\,\Omega$ coplanar waveguide or microstrip with unbroken ground reference plane beneath the trace to the SMA antenna connector.

---

## 5. Bill of Materials (BOM)

| Designator | Component / Part | Value / Description | Package | Quantity |
| :--- | :--- | :--- | :--- | :---: |
| `J1` | 40-Pin GPIO Header | $2\times 20$ Female Socket Header, $2.54\,\text{mm}$ | Through-hole | 1 |
| `U_LORA` | Semtech SX1278 Transceiver | Ra-02 433 MHz LoRa Module | SMD 16-pin Castellated | 1 |
| `J_SMA` | Antenna Connector | Edge-mount SMA Female $50\,\Omega$ | SMA End-launch | 1 |
| `U1` | LDO Voltage Regulator | AMS1117-3.3 or AP2112K-3.3 (3.3V 1A) | SOT-223 / SOT-23-5 | 1 |
| `U2` | ADS1115 ADC | 16-bit 4-Channel I2C ADC IC | MSOP-10 | 1 |
| `U3` | ACS712T-30A Sensor | Hall-effect AC current sensor IC | SOIC-8 | 1 |
| `T1` | ZMPT101B | Galvanic AC Voltage Transformer | Through-hole 4-pin | 1 |
| `U4` | LM358 / MCP6002 | Dual Operational Amplifier | SOIC-8 | 1 |
| `U5, U6` | PC817 Optocouplers | 4-Pin Phototransistor Optocoupler | DIP-4 / SOP-4 | 2 |
| `K1, K2` | Power Relays | Songle SRD-05VDC-SL-C (5V coil, 10A 250VAC) | THT Relay | 2 |
| `Q1, Q2` | NPN Transistors | MMBT3904 or 2N2222 | SOT-23 / TO-92 | 2 |
| `D1` | Schottky Diode | SS34 (3A 40V) | SMC / SMA | 1 |
| `D2, D3` | Flyback Diodes | 1N4007 or SS14 (1A 1000V / 40V) | SMA / DO-41 | 2 |
| `SW1, SW2`| Tactile Switches | Momentary Push Button (6x6mm) | THT 4-pin | 2 |
| `LED1..3` | LEDs | Green (5V, Pump Active), Blue (3.3V) | 0805 / 3mm | 3 |
| `R_HV1,2`| High-Voltage Resistors | $41.2\,\text{k}\Omega$ 1W metal film (or $82\,\text{k}\Omega$ 2W) | Axial / 2512 | 2 |
| `R_PULL` | Pull-up Resistors | $4.7\,\text{k}\Omega$ (I2C), $10\,\text{k}\Omega$ (Buttons, Bases) | 0805 | 6 |
| `R_LED` | Current Limiting Resistors | $330\,\Omega$ (LEDs) | 0805 | 5 |
| `RV1` | Trimmer Potentiometer | $50\,\text{k}\Omega$ Multi-turn Trimmer (ZMPT101B Gain) | 3296W THT | 1 |
| `C_BULK` | Electrolytic Capacitor | $100\,\mu\text{F}$ 16V | Radial THT | 1 |
| `C_DEC` | Ceramic Capacitors | $100\,\text{nF}$, $10\,\mu\text{F}$, $22\,\mu\text{F}$ | 0805 | 10 |
| `TB1..3` | Screw Terminal Blocks | 2-Pin and 3-Pin $5.08\,\text{mm}$ pitch high-current terminals | THT $5.08\,\text{mm}$ | 3 |

---

## 6. Implementation & Verification Plan

1. **SKiDL Circuit Script**:
   - Write a self-contained Python SKiDL script (`scripts/generate_receiver_pcb.py`) modeling all nets, parts, and electrical rules.
   - Utilize standard KiCad symbols (`Connector:Conn_02x20_Odd_Even`, `Sensor:ACS712`, `Relay:Relay_SPDT`, `Amplifier_Operational:LM358`, etc.).
2. **Netlist & Schematic Generation**:
   - Compile SKiDL script to produce:
     - KiCad schematic (`.sch` / `.kicad_sch`)
     - Electrical Rules Check report (`.erc`)
     - Netlist (`.net`)
     - SVG schematic preview (`.svg`)
     - KiCad PCB layout file (`.kicad_pcb`)
3. **Safety & Verification**:
   - Run SKiDL ERC to verify zero unattached pins, zero power-pin conflicts, and correct net connectivity.
   - Review high-voltage isolation clearances on the generated PCB layout.
