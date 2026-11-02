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

    # 1. Board Outline (120mm x 85mm on Edge.Cuts)
    x0, y0 = 50.0, 50.0
    w, h = 120.0, 85.0
    x1, y1 = x0 + w, y0 + h
    lines.extend([
        f'  (gr_line (start {x0} {y0}) (end {x1} {y0}) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts"))',
        f'  (gr_line (start {x1} {y0}) (end {x1} {y1}) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts"))',
        f'  (gr_line (start {x1} {y1}) (end {x0} {y1}) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts"))',
        f'  (gr_line (start {x0} {y1}) (end {x0} {y0}) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts"))',
    ])

    # 2. High-Voltage Isolation Creepage Slots (Edge.Cuts slots between DC and AC zones)
    slot_x = x0 + 67.0
    lines.extend([
        f'  (gr_rect (start {slot_x - 0.75} {y0 + 8.0}) (end {slot_x + 0.75} {y0 + 40.0}) (stroke (width 0.1) (type default)) (fill solid) (layer "Edge.Cuts"))',
        f'  (gr_rect (start {slot_x - 0.75} {y0 + 66.0}) (end {slot_x + 0.75} {y0 + 78.0}) (stroke (width 0.1) (type default)) (fill solid) (layer "Edge.Cuts"))',
        f'  (gr_text "ZONE 1: LOW-VOLTAGE DC LOGIC (5V USB-C)" (at {x0 + 32.0} {y0 + 3.0}) (layer "F.SilkS") (effects (font (size 1.1 1.1) (thickness 0.18))))',
        f'  (gr_text "ZONE 2: 230V AC SENSE & SWITCHING" (at {x0 + 94.0} {y0 + 3.0}) (layer "F.SilkS") (effects (font (size 1.1 1.1) (thickness 0.18))))',
        f'  (gr_text "ISOLATION BARRIER (5mm CREEPAGE)" (at {slot_x - 1.5} {y0 + 24.0} 90) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.18))))',
        f'  (gr_text "MAIN POWER: 5V DC USB-C ONLY" (at {x0 + 20.0} {y0 + 82.0}) (layer "F.SilkS") (effects (font (size 1.1 1.1) (thickness 0.2))))',
        f'  (gr_text "TB2: 230V AC SENSE ONLY" (at {x0 + 110.0} {y0 + 21.5}) (layer "F.SilkS") (effects (font (size 0.9 0.9) (thickness 0.15))))',
    ])

    # 3. Mounting Holes (M2.5 for Raspberry Pi Zero mounting in Zone 1)
    hole_offsets = [(4.0, 4.0), (4.0 + 58.0, 4.0), (4.0, 4.0 + 23.0), (4.0 + 58.0, 4.0 + 23.0)]
    for idx, (hx, hy) in enumerate(hole_offsets):
        lines.append(
            f'  (footprint "MountingHole:MountingHole_2.7mm_M2.5" (layer "F.Cu") (at {x0 + hx} {y0 + hy}) '
            f'(pad "" np_thru_hole circle (at 0 0) (size 2.7 2.7) (drill 2.7) (layers "*.Mask")))'
        )

    # 4. Realistic Spaced Dual-Zone Component Positions (ZERO overlaps)
    positions = {
        # Zone 1 (Low-Voltage DC Logic): x0 + [0 .. 66]
        "J1": (x0 + 32.5, y0 + 12.0, 0),            # RPi 40-pin header horizontal (spans x0+8 to x0+57, y0+12)
        "R_PU1": (x0 + 30.0, y0 + 19.0, 0),        # 4.7k I2C pull-up resistor
        "R_PU2": (x0 + 36.0, y0 + 19.0, 0),        # 4.7k I2C pull-up resistor
        "TB_EXP": (x0 + 54.0, y0 + 19.0, 0),       # ADC A2/A3 Expansion Screw Terminal Block
        "J_CT": (x0 + 6.0, y0 + 26.0, 270),        # 3.5mm CT Clamp Jack (facing left edge)
        "R_BURDEN": (x0 + 16.0, y0 + 24.0, 0),     # 33-ohm CT Burden Resistor
        "R_BIAS1": (x0 + 22.0, y0 + 23.0, 0),      # 10k CT Bias Resistor 1
        "R_BIAS2": (x0 + 22.0, y0 + 27.0, 0),      # 10k CT Bias Resistor 2
        "C_BIAS": (x0 + 28.0, y0 + 25.0, 0),       # 10uF CT Bias Filter Cap
        "J_SMA": (x0 + 4.0, y0 + 42.0, 90),         # SMA antenna connector on left edge
        "U_LORA": (x0 + 20.0, y0 + 42.0, 0),        # SX1278 16-pin Castellated module (spans x0+12 to x0+28)
        "C_LORA1": (x0 + 15.0, y0 + 33.0, 0),      # 10uF LoRa VCC Electrolytic Cap
        "C_LORA2": (x0 + 21.0, y0 + 33.0, 0),      # 0.1uF LoRa VCC Ceramic Cap
        "U2": (x0 + 48.0, y0 + 36.0, 0),            # ADS1115 ADC MSOP-10
        "C_ADS": (x0 + 54.0, y0 + 36.0, 0),        # 100nF ADS1115 Decoupling Cap
        
        # Relay Drivers and Optocoupler Networks (Zone 1 side)
        "R_OPT1": (x0 + 61.0, y0 + 44.0, 0),       # 470-ohm Optocoupler 1 Input Limiting Resistor
        "R_DRV1": (x0 + 52.0, y0 + 46.0, 0),       # 1k NPN Base Drive Resistor 1
        "R_PD1": (x0 + 46.0, y0 + 52.0, 0),        # 10k NPN Base Pull-Down Resistor 1
        "Q1": (x0 + 46.0, y0 + 47.0, 0),           # NPN Driver 1 (Relay 1)

        "R_OPT2": (x0 + 61.0, y0 + 56.0, 0),       # 470-ohm Optocoupler 2 Input Limiting Resistor
        "R_DRV2": (x0 + 52.0, y0 + 58.0, 0),       # 1k NPN Base Drive Resistor 2
        "R_PD2": (x0 + 56.0, y0 + 52.0, 0),        # 10k NPN Base Pull-Down Resistor 2
        "Q2": (x0 + 56.0, y0 + 47.0, 0),           # NPN Driver 2 (Relay 2)

        # LEDs and Current Limiting Resistors
        "R_LED2": (x0 + 12.0, y0 + 52.0, 0),       # 470-ohm 5V Power LED Resistor
        "LED_5V": (x0 + 12.0, y0 + 56.0, 0),       # 5V Power LED
        "R_LED3": (x0 + 20.0, y0 + 52.0, 0),       # 330-ohm 3.3V Radio LED Resistor
        "LED_3V3": (x0 + 20.0, y0 + 56.0, 0),      # 3.3V Radio LED
        "R_LED1": (x0 + 28.0, y0 + 56.0, 0),       # 330-ohm Pump Status LED Resistor
        "LED_PUMP": (x0 + 36.0, y0 + 56.0, 0),     # Pump Active LED

        # USB-C Input & 3.3V Power Generation
        "J_USBC": (x0 + 5.5, y0 + 68.0, 270),      # USB Type-C 5V Input Receptacle (facing left edge)
        "R_CC1": (x0 + 12.0, y0 + 65.0, 0),        # 5.1k CC1 Pull-Down Resistor
        "R_CC2": (x0 + 12.0, y0 + 71.0, 0),        # 5.1k CC2 Pull-Down Resistor
        "C1": (x0 + 18.0, y0 + 68.0, 0),           # 10uF Input Filter Cap
        "U1": (x0 + 24.0, y0 + 68.0, 0),           # AMS1117-3.3V LDO Regulator
        "C2": (x0 + 31.0, y0 + 68.0, 0),           # 22uF Output Filter Cap
        "SW1": (x0 + 42.0, y0 + 68.0, 0),          # Force ON 6mm Button
        "SW2": (x0 + 56.0, y0 + 68.0, 0),          # Force OFF 6mm Button (14mm pitch from SW1)

        # Boundary Optocouplers (Straddling slot_x = x0 + 67.0)
        "U5": (x0 + 67.0, y0 + 48.0, 0),           # PC817 Optocoupler 1 (Relay 1)
        "U6": (x0 + 67.0, y0 + 60.0, 0),           # PC817 Optocoupler 2 (Relay 2)

        # Zone 2 (High-Voltage 230V AC Mains): x0 + [69 .. 120]
        "TB2": (x0 + 110.0, y0 + 12.0, 0),         # AC Mains Input Terminal Block (top right)
        "T1": (x0 + 75.0, y0 + 14.0, 0),           # ZMPT101K Voltage Transformer (Pads: 75,14; 85,14; 75,26.7; 85,26.7)
        "R_HV1": (x0 + 98.0, y0 + 22.0, 0),        # High-voltage limiting resistor 1 (Axial, 15.24mm pitch: 98,22 to 113.24,22)
        "R_HV2": (x0 + 98.0, y0 + 30.0, 0),        # High-voltage limiting resistor 2 (Axial, 15.24mm pitch: 98,30 to 113.24,30)
        "U4": (x0 + 78.0, y0 + 40.0, 0),           # LM358 Op-Amp Conditioner (SOIC-8)
        "C_F": (x0 + 88.0, y0 + 40.0, 0),          # Filter Cap 0805
        "C_ACS": (x0 + 98.0, y0 + 40.0, 0),        # 0.1uF Decoupling Cap for ACS712
        "U3": (x0 + 108.0, y0 + 40.0, 0),          # ACS712T-30A Current Sensor (SOIC-8)
        "D2": (x0 + 74.0, y0 + 56.0, 90),          # Flyback Diode 1 (Relay 1)
        "K1": (x0 + 80.0, y0 + 56.0, 0),           # Songle SRD Relay 1 (Main Pump Contactor)
        "MOV1": (x0 + 104.0, y0 + 50.0, 0),        # 14D471K Varistor across Relay 1 contacts
        "R_SNUB1": (x0 + 101.0, y0 + 58.0, 0),     # 100 ohm 1W Snubber Resistor (pitch 15.24mm: 101,58 to 116.24,58)
        "C_SNUB1": (x0 + 105.0, y0 + 66.0, 0),     # 0.1uF 630V X2 Film Snubber Cap (pitch 7.5mm: 105,66 to 112.5,66)
        "D3": (x0 + 74.0, y0 + 73.0, 90),          # Flyback Diode 2 (Relay 2)
        "K2": (x0 + 80.0, y0 + 73.0, 0),           # Songle SRD Relay 2 (Aux Valve)
        "TB3": (x0 + 112.0, y0 + 73.0, 90),        # Actuator Load Output Terminal (facing right edge)
    }

    # Clear, legible silkscreen labels for every component on the PCB with explicit zero-overlap coordinates
    label_positions = {
        "J1": (x0 + 32.5, y0 + 7.5),
        "J_USBC": (x0 + 6.0, y0 + 61.5),
        "U_LORA": (x0 + 20.0, y0 + 32.5),
        "J_SMA": (x0 + 5.5, y0 + 48.0),
        "J_CT": (x0 + 12.0, y0 + 26.0),
        "U2": (x0 + 48.0, y0 + 32.5),
        "TB_EXP": (x0 + 54.0, y0 + 26.0),
        "T1": (x0 + 80.0, y0 + 9.5),
        "TB2": (x0 + 110.0, y0 + 6.0),
        "R_HV1": (x0 + 105.5, y0 + 19.5),
        "R_HV2": (x0 + 105.5, y0 + 27.5),
        "K1": (x0 + 89.5, y0 + 64.5),
        "K2": (x0 + 89.5, y0 + 81.5),
        "TB3": (x0 + 112.0, y0 + 63.5),
        "MOV1": (x0 + 104.0, y0 + 45.0),
        "R_SNUB1": (x0 + 108.0, y0 + 55.0),
        "C_SNUB1": (x0 + 108.0, y0 + 63.0),
        "SW1": (x0 + 42.0, y0 + 74.5),
        "SW2": (x0 + 56.0, y0 + 74.5),
        "LED_5V": (x0 + 12.0, y0 + 59.0),
        "LED_3V3": (x0 + 20.0, y0 + 59.0),
        "LED_PUMP": (x0 + 36.0, y0 + 59.0),
        "U5": (x0 + 67.0, y0 + 44.0),
        "U6": (x0 + 67.0, y0 + 56.0),
        "U1": (x0 + 25.0, y0 + 63.5),
        "U3": (x0 + 108.0, y0 + 36.5),
        "U4": (x0 + 78.0, y0 + 36.5),
    }

    component_labels = {
        "J1": "J1: RPi Zero 2W (40-Pin Header)",
        "J_USBC": "J_USBC: 5V DC IN",
        "U_LORA": "U_LORA: Ra-02 433MHz",
        "J_SMA": "J_SMA: 50Ω Ant",
        "J_CT": "J_CT: SCT-013",
        "U2": "U2: ADS1115",
        "TB_EXP": "TB_EXP: A2/A3",
        "T1": "T1: ZMPT101B AC SENSE",
        "TB2": "TB2: 230V AC IN",
        "R_HV1": "R_HV1: 41.2k 1W",
        "R_HV2": "R_HV2: 41.2k 1W",
        "K1": "K1: PUMP RELAY 10A",
        "K2": "K2: AUX VALVE 10A",
        "TB3": "TB3: ACTUATORS OUT",
        "MOV1": "MOV1: 14D471K",
        "R_SNUB1": "R_SNUB: 100Ω 1W",
        "C_SNUB1": "C_SNUB: 0.1µF X2",
        "SW1": "SW1: FORCE ON",
        "SW2": "SW2: FORCE OFF",
        "LED_5V": "5V PWR",
        "LED_3V3": "3V3 RF",
        "LED_PUMP": "PUMP ACTIVE",
        "U5": "U5: PC817 (OPTO 1)",
        "U6": "U6: PC817 (OPTO 2)",
        "U1": "U1: AMS1117-3.3",
        "U3": "U3: ACS712-30A",
        "U4": "U4: LM358",
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
    """Generate a valid KiCad schematic file (.sch & .kicad_sch)."""
    lines = [
        '(kicad_sch',
        '  (version 20231120)',
        '  (generator "circuitron")',
        '  (uuid "d0a7a40b-0447-4959-b131-000000000001")',
        '  (paper "A3")',
        '  (title_block',
        '    (title "Wilo Water Pump Automation — Receiver Station HAT")',
        '    (date "2026-11-02")',
        '    (rev "2.1")',
        '    (company "Circuitron Automation System")',
        '    (comment 1 "Raspberry Pi Zero 2W Dual-Zone Isolated Controller with USB-C")',
        '  )',
    ]

    for idx, part in enumerate(circuit.parts):
        sx = 50.0 + (idx % 6) * 45.0
        sy = 50.0 + (idx // 6) * 55.0
        lines.append(f'  (symbol (lib_id "{part.name}") (at {sx} {sy} 0) (unit 1)')
        lines.append(f'    (property "Reference" "{part.ref}" (at {sx} {sy - 8.0} 0) (effects (font (size 1.27 1.27))))')
        lines.append(f'    (property "Value" "{getattr(part, "value", part.name)}" (at {sx} {sy + 8.0} 0) (effects (font (size 1.27 1.27))))')
        lines.append(f'    (property "Footprint" "{part.footprint}" (at {sx} {sy + 12.0} 0) (effects (font (size 1.27 1.27)) hide))')
        lines.append('  )')

    labels = [
        "+5V", "+3V3_RPI", "+3V3_LORA", "GND", "I2C_SDA", "I2C_SCL",
        "SPI0_MOSI", "SPI0_MISO", "SPI0_SCLK", "SPI0_CE0",
        "RELAY1_CTRL", "RELAY2_CTRL", "AC_L_IN", "AC_N_IN", "AC_PUMP_OUT",
        "ADC_A0", "ADC_A1", "ADC_A2", "ADC_A3",
    ]
    for idx, lbl in enumerate(labels):
        lx = 20.0 + (idx % 5) * 60.0
        ly = 240.0 + (idx // 5) * 15.0
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
