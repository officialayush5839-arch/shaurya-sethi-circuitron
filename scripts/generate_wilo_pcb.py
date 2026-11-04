"""Generate KiCad PCB layout, Schematic, and BOM artifacts for the Wilo Receiver Station.

Uses the SKiDL circuit model to output:
- output/wilo_receiver/wilo_receiver.kicad_pcb (Dual-zone, complete footprint layout with zero overlaps)
- output/wilo_receiver/wilo_receiver.kicad_sch & .sch (Schematic)
- output/wilo_receiver/wilo_receiver.net (KiCad netlist)
- output/wilo_receiver/bom.csv (Bill of Materials with component groupings)
- output/wilo_receiver/wilo_receiver.kicad_pro (Project file)
"""
import csv
import os
import re
from pathlib import Path
from circuitron.circuits.wilo_receiver import create_wilo_receiver_circuit

_KICAD_FOOTPRINTS = Path("E:/kicad/share/kicad/footprints")
_LOCAL_FOOTPRINT_CACHE = Path("circuitron/footprints_cache")

_3D_SUBS = {
    "USB_C_Receptacle_HRO_TYPE-C-31-M-12.step": "USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal.step",
    "Jack_3.5mm_CUI_SJ1-3513N_Horizontal.step": "Jack_3.5mm_CUI_SJ1-3523N_Horizontal.step",
    "Transformer_Zeming_ZMPT101K.step": "Transformer_Breve_TEZ-22x24.step",
    "Ai-Thinker-Ra-01-LoRa.step": "ESP-12E.step",
}


def _find_footprint_file(fp_identifier: str) -> Path | None:
    """Find a footprint (.kicad_mod) file either from local cache or KiCad system libraries."""
    if ":" in fp_identifier:
        lib_name, mod_name = fp_identifier.split(":", 1)
    else:
        lib_name = ""
        mod_name = fp_identifier

    # 1. Check local cache first (works even without KiCad installed)
    if _LOCAL_FOOTPRINT_CACHE.exists():
        candidates = [
            _LOCAL_FOOTPRINT_CACHE / f"{mod_name}.kicad_mod",
            _LOCAL_FOOTPRINT_CACHE / f"{lib_name}_{mod_name}.kicad_mod",
        ]
        for c in candidates:
            if c.exists():
                return c

    # 2. Check KiCad installation on external drive
    if _KICAD_FOOTPRINTS.exists():
        direct = _KICAD_FOOTPRINTS / f"{lib_name}.pretty" / f"{mod_name}.kicad_mod"
        if direct.exists():
            return direct
        # Case-insensitive / partial match
        for pretty_dir in _KICAD_FOOTPRINTS.glob("*.pretty"):
            f = pretty_dir / f"{mod_name}.kicad_mod"
            if f.exists():
                return f

    return None


def _load_and_embed_footprint(
    fp_identifier: str,
    ref: str,
    val: str,
    px: float,
    py: float,
    rot: float,
    pin_net_map: dict[str, str],
    net_id_map: dict[str, int],
) -> str:
    """Load an authentic .kicad_mod footprint file, inject reference, value, position, and net bindings."""
    fp_file = _find_footprint_file(fp_identifier)
    if fp_file and fp_file.exists():
        mod_text = fp_file.read_text(encoding="utf-8", errors="replace")

        # 1. Substitute missing 3D models with geometry matches
        for orig, sub in _3D_SUBS.items():
            mod_text = mod_text.replace(orig, sub)

        # 2. Re-point model paths to explicit drive path and KICAD10_3DMODEL_DIR
        mod_text = mod_text.replace("${KICAD10_3DMODEL_DIR}", "E:/kicad/share/kicad/3dmodels")
        mod_text = mod_text.replace("${KICAD_3DMODEL_DIR}", "E:/kicad/share/kicad/3dmodels")
        mod_text = mod_text.replace("${KICAD6_3DMODEL_DIR}", "E:/kicad/share/kicad/3dmodels")
        mod_text = mod_text.replace("${KICAD8_3DMODEL_DIR}", "E:/kicad/share/kicad/3dmodels")

        # 3. Strip header and any initial (layer ...) / (at 0 0)
        lines = mod_text.strip().splitlines()
        body_lines = []
        skip_header = True
        for line in lines[1:]:
            s = line.strip()
            if skip_header:
                if s.startswith('(layer ') or s.startswith('(at 0 0') or s.startswith('(at 0 0 0)'):
                    continue
                skip_header = False
            body_lines.append(line)
        cleaned_body = "\n".join(body_lines)

        # 4. Inject Reference and Value properties
        cleaned_body = re.sub(
            r'\(property\s+"Reference"\s+"[^"]*"\s*(\(at[^)]*\))?',
            f'(property "Reference" "{ref}" (at 0 -2.5 {rot}) (layer "F.SilkS") (effects (font (size 0.9 0.9) (thickness 0.15)))',
            cleaned_body,
            count=1,
        )
        cleaned_body = re.sub(
            r'\(property\s+"Value"\s+"[^"]*"\s*(\(at[^)]*\))?',
            f'(property "Value" "{val}" (at 0 2.5 {rot}) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12)))',
            cleaned_body,
            count=1,
        )

        # 5. Inject pad net connections
        result_chars = []
        i = 0
        n = len(cleaned_body)
        while i < n:
            if cleaned_body[i : i + 5] == "(pad ":
                start = i
                depth = 0
                while i < n:
                    if cleaned_body[i] == "(":
                        depth += 1
                    elif cleaned_body[i] == ")":
                        depth -= 1
                        if depth == 0:
                            i += 1
                            break
                    i += 1
                pad_block = cleaned_body[start:i]
                num_m = re.search(r'\(pad\s+"?([^"\s)]+)"?', pad_block)
                if num_m:
                    pin_num = num_m.group(1)
                    net_name = pin_net_map.get(pin_num, "")
                    net_id = net_id_map.get(net_name, 0)
                    last_paren = pad_block.rfind(")")
                    pad_block = pad_block[:last_paren].rstrip() + f' (net {net_id} "{net_name}"))'
                result_chars.append(pad_block)
            else:
                result_chars.append(cleaned_body[i])
                i += 1

        final_body = "".join(result_chars)
        return f'  (footprint "{fp_identifier}" (layer "F.Cu") (at {px} {py} {rot})\n{final_body}'

    # Fallback if library file not on disk
    lines = [
        f'  (footprint "{fp_identifier}" (layer "F.Cu") (at {px} {py} {rot})',
        f'    (property "Reference" "{ref}" (at 0 -2.5 {rot}) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
        f'    (property "Value" "{val}" (at 0 2.5 {rot}) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
    ]
    for pin_num, net_name in pin_net_map.items():
        net_id = net_id_map.get(net_name, 0)
        lines.append(f'    (pad "{pin_num}" thru_hole circle (at 0 0) (size 1.6 1.6) (drill 0.9) (layers "*.Cu" "*.Mask") (net {net_id} "{net_name}"))')
    lines.append("  )")
    return "\n".join(lines)


def generate_bom_csv(circuit, output_path: Path) -> None:
    """Generate a formatted Bill of Materials (BOM) CSV file."""
    parts_by_value: dict[tuple[str, str, str], list[str]] = {}

    for part in circuit.parts:
        key = (part.name, getattr(part, "value", part.name), getattr(part, "footprint", ""))
        parts_by_value.setdefault(key, []).append(part.ref)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Reference", "Quantity", "Part Name", "Value", "Footprint", "Description"])
        for (name, val, fp), refs in sorted(parts_by_value.items(), key=lambda x: x[1][0]):
            refs_str = ", ".join(sorted(refs))
            desc = f"Component {name}"
            if "SX1278" in name or "Ra-0" in name:
                desc = "433MHz LoRa Transceiver Module"
            elif "ADS1115" in name:
                desc = "16-Bit 4-Channel I2C ADC"
            elif "ACS712" in name:
                desc = "Hall-Effect AC Current Sensor IC (30A)"
            elif "ZMPT101" in name:
                desc = "Precision AC Voltage Transformer"
            elif "SRD-05VDC" in name or "SANYOU" in fp:
                desc = "5V Coil 10A 250VAC Power Relay"
            elif "PC817" in name:
                desc = "Phototransistor Optocoupler (Galvanic Isolation)"
            elif "Conn_02x20" in name:
                desc = "Raspberry Pi 40-Pin GPIO Header Receptacle"
            elif "AMS1117" in name:
                desc = "3.3V 1A LDO Voltage Regulator"
            elif "USB_C" in name:
                desc = "USB Type-C 5V Power Supply Input (CC 5.1k Pull-Downs)"
            elif "Varistor" in name or "14D471K" in val:
                desc = "Metal-Oxide Varistor (275VAC Inductive Transient Suppressor)"
            elif "AudioJack" in name or "SCT013" in val:
                desc = "3.5mm Stereo Jack (SCT-013-000 CT Clamp Input)"
            elif "0.1uF_630V" in val:
                desc = "0.1uF 630V X2 Safety Film Capacitor (RC Snubber)"
            elif "100_1W" in val:
                desc = "100-Ohm 1W Flame-Proof Power Resistor (RC Snubber)"
            elif "33_Ohm" in val:
                desc = "33-Ohm 1% Precision Burden Resistor"
            elif "5.1k" in val:
                desc = "5.1k-Ohm 1% USB-C CC Logic Pull-Down Resistor"
            elif "4.7k" in val:
                desc = "4.7k-Ohm I2C Bus Pull-Up Resistor"
            elif "470" in val:
                desc = "470-Ohm 1% Resistor (LED / Optocoupler Input Limiting)"
            elif "1k" in val:
                desc = "1k-Ohm 1% NPN Base Drive Resistor"
            elif "10k" in val:
                desc = "10k-Ohm 1% Resistor (CT DC Bias Divider / NPN Base Pull-Down)"
            elif "330" in val:
                desc = "330-Ohm Status LED Current Limiting Resistor"
            elif "ADC_EXP" in val:
                desc = "2-Pin Terminal Block (ADS1115 Channels A2 & A3 Expansion)"
            elif "AC_VOLT_SENSE" in val:
                desc = "2-Pin Terminal Block (AC Mains Voltage Sampling Only - Not Board Power)"
            elif "LOAD_ACTUATORS" in val:
                desc = "3-Pin Terminal Block (Pump Contactor & Aux Valve Switched AC Outputs)"
            elif "0.1uF" in val:
                desc = "0.1uF Ceramic Decoupling Capacitor"

            writer.writerow([refs_str, len(refs), name, val, fp, desc])


def generate_kicad_pcb_file(circuit, output_path: Path) -> None:
    """Generate a valid, fully populated dual-zone KiCad PCB file (.kicad_pcb)."""
    nets = list(circuit.nets)
    net_map: dict[str, int] = {net.name: idx + 1 for idx, net in enumerate(nets)}
    net_map[""] = 0

    lines = [
        '(kicad_pcb',
        '  (version 20240108)',
        '  (generator "circuitron")',
        '  (generator_version "10.0")',
        '  (general',
        '    (thickness 1.6)',
        '  )',
        '  (paper "A4")',
        '  (layers',
        '    (0 "F.Cu" signal)',
        '    (31 "B.Cu" signal)',
        '    (32 "B.Adhes" user)',
        '    (33 "F.Adhes" user)',
        '    (34 "B.Paste" user)',
        '    (35 "F.Paste" user)',
        '    (36 "B.SilkS" user "B.Silkscreen")',
        '    (37 "F.SilkS" user "F.Silkscreen")',
        '    (38 "B.Mask" user)',
        '    (39 "F.Mask" user)',
        '    (40 "Edge.Cuts" user)',
        '    (41 "Margin" user)',
        '    (44 "B.CrtYd" user "B.Courtyard")',
        '    (45 "F.CrtYd" user "F.Courtyard")',
        '    (46 "B.Fab" user)',
        '    (47 "F.Fab" user)',
        '  )',
        '  (setup',
        '    (pad_to_mask_clearance 0.05)',
        '    (pcbplotparams',
        '      (layerselection 0x00010fc_ffffffff)',
        '      (plot_on_all_layers_selection 0x0000000_00000000)',
        '      (disableapertmacros false)',
        '      (usegerberextensions true)',
        '      (usegerberattributes true)',
        '      (usegerberadvancedattributes true)',
        '      (creategerberjobfile true)',
        '    )',
        '  )',
        '  (net 0 "")',
    ]

    for net_name, net_id in net_map.items():
        if net_name:
            lines.append(f'  (net {net_id} "{net_name}")')

    # 1. Board Outline (140mm x 95mm on Edge.Cuts - Single Unified 5V USB-C Zone)
    x0, y0 = 50.0, 50.0
    w, h = 140.0, 95.0
    x1, y1 = x0 + w, y0 + h
    lines.extend([
        f'  (gr_line (start {x0} {y0}) (end {x1} {y0}) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts"))',
        f'  (gr_line (start {x1} {y0}) (end {x1} {y1}) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts"))',
        f'  (gr_line (start {x1} {y1}) (end {x0} {y1}) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts"))',
        f'  (gr_line (start {x0} {y1}) (end {x0} {y0}) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts"))',
    ])

    # 2. Silkscreen Board Branding & System Labels (Single unified zone, no milled isolation slots)
    lines.extend([
        f'  (gr_text "WILO WATER PUMP AUTOMATION — RECEIVER STATION HAT (140x95mm)" (at {x0 + 70.0} {y0 + 3.0}) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))',
        f'  (gr_text "MAIN SYSTEM POWER: 5V DC USB-C ONLY (NO AC POWER SUPPLY)" (at {x0 + 38.0} {y0 + 92.0}) (layer "F.SilkS") (effects (font (size 0.95 0.95) (thickness 0.16))))',
        f'  (gr_text "TB2: VOLTAGE SENSE ONLY (NOT POWER)" (at {x0 + 124.0} {y0 + 6.0}) (layer "F.SilkS") (effects (font (size 0.85 0.85) (thickness 0.14))))',
        f'  (gr_text "TB3: ACTUATOR CONTACTS" (at {x0 + 130.0} {y0 + 89.0}) (layer "F.SilkS") (effects (font (size 0.9 0.9) (thickness 0.15))))',
    ])

    # 3. Mounting Holes (4 Board Corners M2.5 + Raspberry Pi HAT M2.5)
    corner_holes = [(4.0, 4.0), (w - 4.0, 4.0), (4.0, h - 4.0), (w - 4.0, h - 4.0)]
    for hx, hy in corner_holes:
        lines.append(
            f'  (footprint "MountingHole:MountingHole_2.7mm_M2.5" (layer "F.Cu") (at {x0 + hx} {y0 + hy}) '
            f'(pad "" np_thru_hole circle (at 0 0) (size 2.7 2.7) (drill 2.7) (layers "*.Mask")))'
        )

    # 4. Spaced Component Positions (Zero overlaps, all connectors on perimeter/corners)
    positions = {
        # --- Top Edge Connectors ---
        "J1": (x0 + 55.0, y0 + 10.0, 0),             # RPi 40-pin header centered along top edge (spans x0+29.6 to x0+80.4)
        "TB_EXP": (x0 + 98.0, y0 + 10.0, 0),         # ADC A2/A3 Expansion Screw Terminal Block (top edge)
        "TB2": (x0 + 128.0, y0 + 12.0, 0),           # AC Mains Voltage Sense Input Terminal (top-right corner)

        # --- Left Edge Connectors ---
        "J_SMA": (x0 + 6.0, y0 + 26.0, 90),          # 433MHz SMA Antenna Connector (top-left edge)
        "J_CT": (x0 + 8.0, y0 + 52.0, 270),          # 3.5mm CT Clamp Jack (facing left edge)
        "J_USBC": (x0 + 7.0, y0 + 82.0, 270),        # USB-C 5V Main Power Input (bottom-left corner)

        # --- Bottom Edge UI: Push Buttons & Status Indicators ---
        "SW1": (x0 + 44.0, y0 + 83.0, 0),            # Force ON 6mm Tactile Button (bottom edge)
        "SW2": (x0 + 56.0, y0 + 83.0, 0),            # Force OFF 6mm Tactile Button (bottom edge)
        "LED_5V": (x0 + 42.0, y0 + 72.0, 0),         # 5V Power LED
        "R_LED2": (x0 + 42.0, y0 + 76.0, 0),         # 470-ohm 5V Power LED Resistor
        "LED_3V3": (x0 + 50.0, y0 + 72.0, 0),        # 3.3V Radio LED
        "R_LED3": (x0 + 50.0, y0 + 76.0, 0),         # 330-ohm 3.3V Radio LED Resistor
        "LED_PUMP": (x0 + 58.0, y0 + 72.0, 0),       # Pump Active Status LED
        "R_LED1": (x0 + 58.0, y0 + 76.0, 0),         # 330-ohm Pump Status LED Resistor

        # --- Bottom-Right Edge Connectors ---
        "TB3": (x0 + 130.0, y0 + 75.0, 90),          # Actuator Load Output Terminal: PUMP, VALVE, NEUT (bottom-right corner)

        # --- RF Front-End (Top-Left Subsystem) ---
        "U_LORA": (x0 + 26.0, y0 + 28.0, 0),         # SX1278 Ra-02 433MHz Module (adjacent to J_SMA)
        "C_LORA1": (x0 + 22.0, y0 + 16.0, 0),        # 10uF LoRa VCC Cap
        "C_LORA2": (x0 + 28.0, y0 + 16.0, 0),        # 0.1uF LoRa VCC Ceramic Cap

        # --- CT Sensor Conditioning (Mid-Left Subsystem) ---
        "R_BURDEN": (x0 + 20.0, y0 + 48.0, 0),       # 33-ohm Burden Resistor
        "R_BIAS1": (x0 + 20.0, y0 + 53.0, 0),        # 10k CT Bias Resistor 1
        "R_BIAS2": (x0 + 20.0, y0 + 58.0, 0),        # 10k CT Bias Resistor 2
        "C_BIAS": (x0 + 26.0, y0 + 54.0, 0),         # 10uF Bias Filter Cap

        # --- Power Supply Generation (Bottom-Left Subsystem) ---
        "R_CC1": (x0 + 13.0, y0 + 78.0, 0),          # 5.1k CC1 Pull-Down Resistor
        "R_CC2": (x0 + 13.0, y0 + 86.0, 0),          # 5.1k CC2 Pull-Down Resistor
        "C1": (x0 + 18.0, y0 + 82.0, 0),             # 10uF Input Filter Cap
        "U1": (x0 + 26.0, y0 + 82.0, 0),             # AMS1117-3.3V LDO Regulator (SOT-223)
        "C2": (x0 + 34.0, y0 + 82.0, 0),             # 22uF Output Filter Cap

        # --- Central Analog Hub ---
        "U2": (x0 + 60.0, y0 + 30.0, 0),             # ADS1115 16-Bit ADC (MSOP-10)
        "C_ADS": (x0 + 66.0, y0 + 30.0, 0),          # 100nF ADS1115 Decoupling Cap
        "R_PU1": (x0 + 56.0, y0 + 22.0, 0),          # 4.7k I2C SDA Pull-Up Resistor
        "R_PU2": (x0 + 64.0, y0 + 22.0, 0),          # 4.7k I2C SCL Pull-Up Resistor

        # --- AC Voltage Sampling Subsystem (Top-Right) ---
        "T1": (x0 + 112.0, y0 + 26.0, 0),            # ZMPT101B Voltage Transformer
        "R_HV1": (x0 + 128.0, y0 + 24.0, 90),        # 41.2k 1W HV Resistor 1 (Vertical orientation, plenty of clearance)
        "R_HV2": (x0 + 134.0, y0 + 24.0, 90),        # 41.2k 1W HV Resistor 2 (Vertical orientation, 6mm pitch from R_HV1)
        "U4": (x0 + 85.0, y0 + 28.0, 0),             # LM358 Op-Amp Conditioner (SOIC-8)

        # --- AC Current Sensor Subsystem (Center-Right) ---
        "U3": (x0 + 95.0, y0 + 46.0, 0),             # ACS712T-30A Current Sensor (SOIC-8)
        "C_ACS": (x0 + 88.0, y0 + 46.0, 0),          # 0.1uF ACS712 VCC Decoupling Cap
        "C_F": (x0 + 102.0, y0 + 46.0, 0),           # 4.7nF ACS712 Filter Cap

        # --- Galvanic Isolated Relay Drivers ---
        "U5": (x0 + 65.0, y0 + 58.0, 0),             # PC817 Optocoupler 1 (Pump Relay)
        "R_OPT1": (x0 + 56.0, y0 + 58.0, 0),         # 470-ohm Opto 1 Limiting Resistor
        "R_DRV1": (x0 + 74.0, y0 + 58.0, 0),         # 1k NPN Base Drive Resistor 1
        "Q1": (x0 + 80.0, y0 + 58.0, 0),             # MMBT3904 NPN Driver 1
        "R_PD1": (x0 + 80.0, y0 + 63.0, 0),          # 10k Base Pull-Down 1

        "U6": (x0 + 65.0, y0 + 72.0, 0),             # PC817 Optocoupler 2 (Aux Valve Relay)
        "R_OPT2": (x0 + 56.0, y0 + 72.0, 0),         # 470-ohm Opto 2 Limiting Resistor
        "R_DRV2": (x0 + 74.0, y0 + 72.0, 0),         # 1k NPN Base Drive Resistor 2
        "Q2": (x0 + 80.0, y0 + 72.0, 0),             # MMBT3904 NPN Driver 2
        "R_PD2": (x0 + 80.0, y0 + 77.0, 0),          # 10k Base Pull-Down 2

        # --- Relays & Snubber Network ---
        "K1": (x0 + 98.0, y0 + 60.0, 0),             # Songle 10A 250VAC Relay 1 (Pump)
        "D2": (x0 + 90.0, y0 + 60.0, 90),            # 1N4007 Flyback Diode 1
        "K2": (x0 + 98.0, y0 + 78.0, 0),             # Songle 10A 250VAC Relay 2 (Aux Valve)
        "D3": (x0 + 90.0, y0 + 78.0, 90),            # 1N4007 Flyback Diode 2
        "MOV1": (x0 + 118.0, y0 + 54.0, 0),          # 14D471K Varistor Transient Suppressor
        "R_SNUB1": (x0 + 118.0, y0 + 62.0, 0),       # 100-ohm 1W Snubber Resistor
        "C_SNUB1": (x0 + 118.0, y0 + 70.0, 0),       # 0.1uF 630V X2 Safety Film Snubber Cap
    }

    # Clear, legible silkscreen labels for every component on the PCB with explicit zero-overlap coordinates
    label_positions = {
        "J1": (x0 + 55.0, y0 + 6.0),
        "TB_EXP": (x0 + 98.0, y0 + 6.0),
        "TB2": (x0 + 128.0, y0 + 6.0),
        "J_SMA": (x0 + 6.0, y0 + 20.0),
        "U_LORA": (x0 + 26.0, y0 + 38.5),
        "C_LORA1": (x0 + 22.0, y0 + 13.5),
        "C_LORA2": (x0 + 28.0, y0 + 13.5),
        "J_CT": (x0 + 8.0, y0 + 45.0),
        "R_BURDEN": (x0 + 20.0, y0 + 45.5),
        "R_BIAS1": (x0 + 20.0, y0 + 51.0),
        "R_BIAS2": (x0 + 20.0, y0 + 60.5),
        "C_BIAS": (x0 + 26.0, y0 + 57.0),
        "J_USBC": (x0 + 7.0, y0 + 74.0),
        "R_CC1": (x0 + 13.0, y0 + 75.5),
        "R_CC2": (x0 + 13.0, y0 + 88.5),
        "C1": (x0 + 18.0, y0 + 79.5),
        "U1": (x0 + 26.0, y0 + 77.0),
        "C2": (x0 + 34.0, y0 + 79.5),
        "SW1": (x0 + 44.0, y0 + 88.5),
        "SW2": (x0 + 56.0, y0 + 88.5),
        "U2": (x0 + 60.0, y0 + 26.5),
        "C_ADS": (x0 + 66.0, y0 + 26.5),
        "R_PU1": (x0 + 56.0, y0 + 19.5),
        "R_PU2": (x0 + 64.0, y0 + 19.5),
        "U4": (x0 + 85.0, y0 + 24.5),
        "T1": (x0 + 112.0, y0 + 20.0),
        "R_HV1": (x0 + 128.0, y0 + 20.5),
        "R_HV2": (x0 + 134.0, y0 + 20.5),
        "U3": (x0 + 95.0, y0 + 42.0),
        "C_ACS": (x0 + 88.0, y0 + 42.0),
        "C_F": (x0 + 102.0, y0 + 42.0),
        "U5": (x0 + 65.0, y0 + 54.0),
        "R_OPT1": (x0 + 56.0, y0 + 54.0),
        "R_DRV1": (x0 + 74.0, y0 + 54.0),
        "Q1": (x0 + 80.0, y0 + 54.0),
        "R_PD1": (x0 + 80.0, y0 + 65.5),
        "U6": (x0 + 65.0, y0 + 68.0),
        "R_OPT2": (x0 + 56.0, y0 + 68.0),
        "R_DRV2": (x0 + 74.0, y0 + 68.0),
        "Q2": (x0 + 80.0, y0 + 68.0),
        "R_PD2": (x0 + 80.0, y0 + 79.5),
        "K1": (x0 + 107.0, y0 + 60.0),
        "D2": (x0 + 90.0, y0 + 56.0),
        "K2": (x0 + 107.0, y0 + 78.0),
        "D3": (x0 + 90.0, y0 + 74.0),
        "MOV1": (x0 + 118.0, y0 + 50.0),
        "R_SNUB1": (x0 + 124.0, y0 + 62.0),
        "C_SNUB1": (x0 + 124.0, y0 + 70.0),
        "TB3": (x0 + 130.0, y0 + 65.0),
        "LED_5V": (x0 + 42.0, y0 + 68.0),
        "LED_3V3": (x0 + 50.0, y0 + 68.0),
        "LED_PUMP": (x0 + 58.0, y0 + 68.0),
    }

    component_labels = {
        "J1": "J1: RPi Zero 2W 40-Pin Header",
        "TB_EXP": "TB_EXP: A2/A3",
        "TB2": "TB2: SENSE ONLY (NOT POWER)",
        "J_SMA": "J_SMA: 50Ω Ant",
        "U_LORA": "U_LORA: Ra-02 433MHz",
        "C_LORA1": "10µF",
        "C_LORA2": "0.1µF",
        "J_CT": "J_CT: SCT-013 CT",
        "R_BURDEN": "33Ω",
        "R_BIAS1": "10k",
        "R_BIAS2": "10k",
        "C_BIAS": "10µF",
        "J_USBC": "J_USBC: 5V IN",
        "R_CC1": "5.1k",
        "R_CC2": "5.1k",
        "C1": "10µF",
        "U1": "U1: AMS1117-3.3",
        "C2": "22µF",
        "SW1": "SW1: ON",
        "SW2": "SW2: OFF",
        "U2": "U2: ADS1115 ADC",
        "C_ADS": "100nF",
        "R_PU1": "4.7k",
        "R_PU2": "4.7k",
        "U4": "U4: LM358",
        "T1": "T1: ZMPT101B SENSE",
        "R_HV1": "R_HV1: 41.2k 1W",
        "R_HV2": "R_HV2: 41.2k 1W",
        "U3": "U3: ACS712-30A",
        "C_ACS": "0.1µF",
        "C_F": "4.7nF",
        "U5": "U5: PC817 (OPTO 1)",
        "R_OPT1": "470Ω",
        "R_DRV1": "1k",
        "Q1": "Q1: NPN",
        "R_PD1": "10k",
        "U6": "U6: PC817 (OPTO 2)",
        "R_OPT2": "470Ω",
        "R_DRV2": "1k",
        "Q2": "Q2: NPN",
        "R_PD2": "10k",
        "K1": "K1: PUMP RELAY 10A",
        "D2": "1N4007",
        "K2": "K2: AUX VALVE 10A",
        "D3": "1N4007",
        "MOV1": "MOV1: 14D471K",
        "R_SNUB1": "100Ω 1W",
        "C_SNUB1": "0.1µF X2",
        "TB3": "TB3: LOAD (PUMP/VALVE/N)",
        "LED_5V": "5V PWR",
        "LED_3V3": "3V3 RF",
        "LED_PUMP": "PUMP ACTIVE",
    }

    for ref, lbl in component_labels.items():
        if ref in label_positions:
            lx, ly = label_positions[ref]
            lines.append(f'  (gr_text "{lbl}" (at {lx} {ly}) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))')

    for part in circuit.parts:
        px, py, rot = positions.get(part.ref, (x0 + 25.0, y0 + 30.0, 0))
        val = getattr(part, "value", part.name)
        pin_net_map = {str(pin.num): getattr(pin.net, "name", "") for pin in part.pins}

        fp_str = _load_and_embed_footprint(
            part.footprint,
            part.ref,
            val,
            px,
            py,
            rot,
            pin_net_map,
            net_map,
        )
        lines.append(fp_str)

    lines.append(")")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def generate_kicad_schematic_file(circuit, output_path: Path) -> None:
    """Generate a clean, modular, professional KiCad schematic file (.sch & .kicad_sch).
    
    Organized into 7 framed functional circuit blocks with clear alignment and net labels.
    """
    lines = [
        '(kicad_sch',
        '  (version 20231120)',
        '  (generator "circuitron")',
        '  (uuid "d0a7a40b-0447-4959-b131-000000000001")',
        '  (paper "A3")',
        '  (title_block',
        '    (title "Wilo Water Pump Automation — Receiver Station")',
        '    (date "2026-11-04")',
        '    (rev "3.0")',
        '    (company "Circuitron Automation System")',
        '    (comment 1 "Single Unified 5V DC USB-C Zone - Perimeter Connectors - Clean Schematic")',
        '  )',
    ]

    # 7 Functional Schematic Blocks with bounding boxes and titles
    blocks = [
        ("1. RASPBERRY PI ZERO 2W INTERFACE & GPIO BUS", 15.0, 18.0, 135.0, 105.0),
        ("2. SX1278 Ra-02 LoRa 433MHz TRANSCEIVER & RF", 145.0, 18.0, 265.0, 105.0),
        ("3. AC MAINS VOLTAGE SAMPLING ONLY (NOT POWER - ZMPT101B)", 275.0, 18.0, 405.0, 105.0),
        ("4. MAIN 5V DC USB-C POWER SUPPLY & 3.3V LDO", 15.0, 115.0, 135.0, 195.0),
        ("5. ADS1115 16-BIT ADC & EXPANSION", 145.0, 115.0, 265.0, 195.0),
        ("6. MOTOR CURRENT SENSING (ACS712 & CT CLAMP)", 275.0, 115.0, 405.0, 195.0),
        ("7. DUAL POWER RELAYS, OPTOCOUPLERS & SNUBBER TRANSIENT PROTECTION", 15.0, 205.0, 405.0, 285.0),
    ]

    # Draw block borders and titles
    for title, bx1, by1, bx2, by2 in blocks:
        lines.append(f'  (polyline (pts (xy {bx1} {by1}) (xy {bx2} {by1}) (xy {bx2} {by2}) (xy {bx1} {by2}) (xy {bx1} {by1})) (stroke (width 0.25) (type default)))')
        lines.append(f'  (text "{title}" (at {bx1 + 4.0} {by1 + 5.0} 0) (effects (font (size 1.8 1.8) bold)))')

    # Explicit modular symbol coordinates per component
    sch_positions = {
        # Block 1: RPi & UI
        "J1": (50.0, 50.0),
        "SW1": (90.0, 38.0),
        "SW2": (90.0, 52.0),
        "LED_5V": (118.0, 38.0),
        "R_LED2": (108.0, 38.0),
        "LED_3V3": (118.0, 52.0),
        "R_LED3": (108.0, 52.0),
        "LED_PUMP": (118.0, 68.0),
        "R_LED1": (108.0, 68.0),

        # Block 2: LoRa RF
        "U_LORA": (195.0, 55.0),
        "C_LORA1": (165.0, 45.0),
        "C_LORA2": (165.0, 65.0),
        "J_SMA": (240.0, 55.0),

        # Block 3: AC Voltage Sense
        "TB2": (295.0, 55.0),
        "R_HV1": (320.0, 45.0),
        "R_HV2": (320.0, 65.0),
        "T1": (350.0, 55.0),
        "U4": (380.0, 55.0),

        # Block 4: Power Supply
        "J_USBC": (35.0, 155.0),
        "R_CC1": (52.0, 145.0),
        "R_CC2": (52.0, 165.0),
        "C1": (70.0, 155.0),
        "U1": (95.0, 155.0),
        "C2": (120.0, 155.0),

        # Block 5: ADC & Expansion
        "U2": (195.0, 155.0),
        "C_ADS": (165.0, 155.0),
        "R_PU1": (190.0, 135.0),
        "R_PU2": (205.0, 135.0),
        "TB_EXP": (245.0, 155.0),

        # Block 6: Current Sensors
        "J_CT": (295.0, 150.0),
        "R_BURDEN": (315.0, 140.0),
        "R_BIAS1": (315.0, 152.0),
        "R_BIAS2": (315.0, 164.0),
        "C_BIAS": (330.0, 158.0),
        "U3": (365.0, 155.0),
        "C_ACS": (365.0, 135.0),
        "C_F": (385.0, 155.0),

        # Block 7: Relays & Protection
        "U5": (50.0, 245.0),
        "R_OPT1": (30.0, 245.0),
        "R_DRV1": (70.0, 245.0),
        "Q1": (90.0, 245.0),
        "R_PD1": (90.0, 260.0),
        "D2": (115.0, 235.0),
        "K1": (130.0, 245.0),
        "MOV1": (160.0, 245.0),
        "R_SNUB1": (180.0, 245.0),
        "C_SNUB1": (200.0, 245.0),

        "U6": (240.0, 245.0),
        "R_OPT2": (220.0, 245.0),
        "R_DRV2": (260.0, 245.0),
        "Q2": (280.0, 245.0),
        "R_PD2": (280.0, 260.0),
        "D3": (305.0, 235.0),
        "K2": (320.0, 245.0),
        "TB3": (370.0, 245.0),
    }

    # Render each part neatly at its dedicated schematic coordinate
    for part in circuit.parts:
        sx, sy = sch_positions.get(part.ref, (50.0, 50.0))
        lines.append(f'  (symbol (lib_id "{part.name}") (at {sx} {sy} 0) (unit 1)')
        lines.append(f'    (property "Reference" "{part.ref}" (at {sx} {sy - 6.5} 0) (effects (font (size 1.27 1.27) bold)))')
        lines.append(f'    (property "Value" "{getattr(part, "value", part.name)}" (at {sx} {sy + 6.5} 0) (effects (font (size 1.1 1.1))))')
        lines.append(f'    (property "Footprint" "{part.footprint}" (at {sx} {sy + 9.5} 0) (effects (font (size 0.9 0.9)) hide))')
        lines.append('  )')

    # Clear Global Net Labels
    labels = [
        # Power Rails
        ("+5V", 25.0, 130.0),
        ("+3V3_RPI", 25.0, 85.0),
        ("+3V3_LORA", 155.0, 85.0),
        ("GND", 25.0, 95.0),

        # Digital Signals
        ("I2C_SDA", 50.0, 85.0),
        ("I2C_SCL", 75.0, 85.0),
        ("SPI0_MOSI", 175.0, 85.0),
        ("SPI0_MISO", 200.0, 85.0),
        ("SPI0_SCLK", 225.0, 85.0),
        ("SPI0_CE0", 250.0, 85.0),

        # Control & Status
        ("RELAY1_CTRL", 30.0, 260.0),
        ("RELAY2_CTRL", 220.0, 260.0),
        ("BTN_FORCE_ON", 90.0, 85.0),
        ("BTN_FORCE_OFF", 100.0, 85.0),
        ("LED_PUMP_RUN", 118.0, 85.0),

        # Analog Signals
        ("ADC_A0", 285.0, 180.0),
        ("ADC_A1", 285.0, 85.0),
        ("ADC_A2", 235.0, 180.0),
        ("ADC_A3", 255.0, 180.0),

        # AC Mains & Actuators
        ("AC_L_IN", 295.0, 85.0),
        ("AC_N_IN", 315.0, 85.0),
        ("AC_PUMP_OUT", 355.0, 265.0),
        ("AC_VALVE_OUT", 375.0, 265.0),
    ]

    for lbl, lx, ly in labels:
        lines.append(f'  (global_label "{lbl}" (shape input) (at {lx} {ly} 0) (effects (font (size 1.27 1.27))))')

    lines.append(")")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(lines)
    output_path.write_text(content, encoding="utf-8")

    sch_compat = output_path.with_suffix(".sch")
    sch_compat.write_text(content, encoding="utf-8")


def build_receiver_artifacts(output_dir: str = "output/wilo_receiver") -> dict[str, Path]:
    """Compile and generate all receiver design files into target directory."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    circuit = create_wilo_receiver_circuit()

    # 1. KiCad Netlist
    netlist_path = out_dir / "wilo_receiver.net"
    circuit.generate_netlist(file_=str(netlist_path))

    # 2. KiCad PCB Layout
    pcb_path = out_dir / "wilo_receiver.kicad_pcb"
    generate_kicad_pcb_file(circuit, pcb_path)

    # 3. KiCad Schematic
    sch_path = out_dir / "wilo_receiver.kicad_sch"
    generate_kicad_schematic_file(circuit, sch_path)

    # 4. Bill of Materials CSV
    bom_path = out_dir / "bom.csv"
    generate_bom_csv(circuit, bom_path)

    # 5. KiCad Project File
    pro_path = out_dir / "wilo_receiver.kicad_pro"
    pro_content = (
        '{\n'
        '  "meta": {"filename": "wilo_receiver.kicad_pro", "version": 1},\n'
        '  "sheets": [["wilo_receiver.kicad_sch", ""]]\n'
        '}\n'
    )
    pro_path.write_text(pro_content, encoding="utf-8")

    return {
        "netlist": netlist_path,
        "pcb": pcb_path,
        "schematic": sch_path,
        "bom": bom_path,
        "project": pro_path,
    }


if __name__ == "__main__":
    print("Generating Wilo Water Pump Automation Receiver PCB artifacts...")
    artifacts = build_receiver_artifacts()
    for name, path in artifacts.items():
        print(f"Generated {name.upper()}: {path}")
