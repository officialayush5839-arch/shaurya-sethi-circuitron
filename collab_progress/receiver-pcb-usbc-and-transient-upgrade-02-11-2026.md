# Receiver Station PCB Implementation, Component Audit & Transient Protection Upgrade

- **Date:** 02-11-2026
- **Status:** Complete & 100% Verified

## Summary
Completed an exhaustive audit and enhancement of the Receiver Station PCB per hardware requirements:
1. **EMI & Transient Protection Architecture (Optocouplers vs. Snubber Circuit)**:
   - Evaluated best engineering practices for EMI and transient suppression. Both methods are essential as they protect different sides of the system:
     - **Optocouplers (`U5`, `U6` PC817)** provide **galvanic isolation** on the low-voltage control side, completely isolating the sensitive 3.3V Raspberry Pi Zero 2W GPIOs from relay coil transients, inductive switching kicks, and ground loops. Added dedicated 470 Ω input series current-limiting resistors (`R_OPT1`, `R_OPT2`), 1 kΩ NPN base drive resistors (`R_DRV1`, `R_DRV2`), and 10 kΩ pull-down resistors (`R_PD1`, `R_PD2`).
     - **RC Snubber Circuit (`R_SNUB1` 100 Ω 1W flameproof + `C_SNUB1` 0.1 µF 630V X2 film cap) + MOV (`MOV1` 14D471K / 275VAC)** protects the **high-voltage AC contact side** (230V mains switching). Absorbs high-frequency inductive kickback when the 230V contactor / pump coil is interrupted, preventing contact arcing, contact welding, and electromagnetic interference.
     - **Flyback Diodes (`D2`, `D3` 1N4007)** protect the driver transistors from DC relay coil discharge.
2. **Component Verification & Enhancements**:
   - **AC Voltage Sensor**: ZMPT101B potential transformer (`T1`) with 82 kΩ 1W high-voltage limiting resistors (`R_HV1`, `R_HV2`) and LM358 op-amp conditioner (`U4`) connected to ADS1115 Channel A1.
   - **Dual Relay Module**: 5V 10A Songle SPDT relays (`K1` for Wilo pump, `K2` for auxiliary valve).
   - **CT Sensor Socket**: 3.5 mm audio jack (`J_CT`, CUI SJ1-3513N) with 33 Ω burden resistor (`R_BURDEN`) and DC bias divider (`R_BIAS1`, `R_BIAS2` 10 kΩ + `C_BIAS` 10 µF) providing a 2.5V DC virtual ground to ADS1115 Channel A0.
   - **USB Type-C Female Connector**: `J_USBC` with 5.1 kΩ CC1/CC2 pull-down resistors (`R_CC1`, `R_CC2`) serving as the sole 5V DC power input. Removed auxiliary DC screw terminal.
   - **LED Current Limiting**: Added `R_LED2` (470 Ω) for `LED_5V` and `R_LED3` (330 Ω) for `LED_3V3`, alongside `R_LED1` (330 Ω) for `LED_PUMP`.
   - **ACS712 Decoupling**: Added 0.1 µF ceramic decoupling capacitor `C_ACS` on the ACS712 VCC line.
3. **Dual-Zone Layout & 5mm Isolation Slots**:
   - Maintained 120 mm × 85 mm form factor with 5 mm milled creepage isolation slots between Zone 1 (DC Logic) and Zone 2 (230V AC Mains).
4. **Artifacts & Packaging**:
   - Re-compiled KiCad netlist, PCB layout, schematic, BOM CSV, 2D composite layout PNG, matplotlib 3D render, KiCad 10 raytraced isometric/top 3D renders, and self-contained project zip.

## Files Changed
- `circuitron/circuits/wilo_receiver.py`: Updated SKiDL circuit with optocoupler resistors, LED resistors, ACS712 decoupling capacitor, and validated ERC.
- `scripts/generate_wilo_pcb.py`: Added component placement coordinates and BOM categorizations.
- `scripts/generate_board_png.py`: Updated 2D composite photorealistic render with new components.
- `scripts/render_board_3d.py`: Updated 3D perspective visualization.
- `scripts/package_kicad_project.py`: Packaged all design files and footprints into zip.
- `tests/test_wilo_receiver.py`: Added assertions for all new components and signal paths.
- `tests/test_artifact_generation.py`: Updated BOM verification assertions.
- `output/wilo_receiver/`: Regenerated all design deliverables.

## Verification
- Unit & Artifact test suite: `pytest -q` passed 100% (4 passed in 9.82s).
- SKiDL Electrical Rules Check (ERC): 0 errors reported.
- KiCad 10 Raytracing: Rendered 3D board isometric (`wilo_receiver_3d_iso.png`) and top (`wilo_receiver_3d_top.png`) views via `kicad-cli.exe`.
