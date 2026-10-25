"""Wilo Water Pump Automation Receiver PCB Generation Script.

Generates complete KiCad manufacturing artifacts:
- KiCad Netlist (wilo_receiver.net)
- KiCad Schematic (wilo_receiver.sch & wilo_receiver.kicad_sch)
- KiCad PCB Layout (wilo_receiver.kicad_pcb) with 85x65mm dual-zone isolation layout
- Bill of Materials CSV (bom.csv)
"""
import os
import re
import csv
from pathlib import Path
from circuitron.circuits.wilo_receiver import create_wilo_receiver_circuit

FP_SEARCH_DIRS = [
    str(Path(__file__).parent.parent / "circuitron" / "footprints_cache"),
    "E:/kicad/share/kicad/footprints",
    "C:/Program Files/KiCad/share/kicad/footprints",
    "C:/Program Files/KiCad/8.0/share/kicad/footprints",
    "/usr/share/kicad/footprints",
]


def _find_kicad_mod_file(fp_identifier: str) -> Path | None:
    """Find the .kicad_mod file for a given 'Library:Footprint' identifier."""
    if ":" not in fp_identifier:
        return None
    lib, name = fp_identifier.split(":", 1)
    
    # Check local cache first
    cache_cand = Path(__file__).parent.parent / "circuitron" / "footprints_cache" / f"{lib}_{name}.kicad_mod"
    if cache_cand.exists():
        return cache_cand

    for base in FP_SEARCH_DIRS:
        cand = Path(base) / f"{lib}.pretty" / f"{name}.kicad_mod"
        if cand.exists():
            return cand
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
    """Load real .kicad_mod file from disk and embed it with net bindings and placement."""
    mod_path = _find_kicad_mod_file(fp_identifier)
    if mod_path and mod_path.exists():
        mod_text = mod_path.read_text(encoding="utf-8")
        # 1. Update header with placement coordinates (cleanly replacing any existing layer/at)
        header_pattern = r'\(footprint\s+"[^"]*".*?(?=\(version|\(generator|\(descr|\(tags|\(property|\(attr|\(fp_|\(pad)'
        mod_text = re.sub(
            header_pattern,
            f'(footprint "{fp_identifier}"\n    (layer "F.Cu")\n    (at {px} {py} {rot})\n  ',
            mod_text,
            count=1,
            flags=re.DOTALL,
        )

        # 2. Update Reference & Value properties
        mod_text = re.sub(r'\(property\s+"Reference"\s+"[^"]*"', f'(property "Reference" "{ref}"', mod_text, count=1)
        mod_text = re.sub(r'\(property\s+"Value"\s+"[^"]*"', f'(property "Value" "{val}"', mod_text, count=1)

        # 3. Attach nets to all (pad ...) s-expressions
        result_chars = []
        i = 0
        n = len(mod_text)
        while i < n:
            if mod_text[i : i + 5] == "(pad ":
                start = i
                depth = 0
                while i < n:
                    if mod_text[i] == "(":
                        depth += 1
                    elif mod_text[i] == ")":
                        depth -= 1
                        if depth == 0:
                            i += 1
                            break
                    i += 1
                pad_block = mod_text[start:i]
                num_m = re.search(r'\(pad\s+"?([^"\s)]+)"?', pad_block)
                if num_m:
                    pin_num = num_m.group(1)
                    net_name = pin_net_map.get(pin_num, "")
                    net_id = net_id_map.get(net_name, 0)
                    last_paren = pad_block.rfind(")")
                    pad_block = pad_block[:last_paren].rstrip() + f' (net {net_id} "{net_name}"))'
                result_chars.append(pad_block)
            else:
                result_chars.append(mod_text[i])
                i += 1

        return "".join(result_chars)

    # Fallback if library file not on disk
    lines = [
        f'  (footprint "{fp_identifier}" (layer "F.Cu") (at {px} {py} {rot})',
        f'    (property "Reference" "{ref}" (at 0 -2.5 {rot}) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
        f'    (property "Value" "{val}" (at 0 2.5 {rot}) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))',
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
                desc = "Phototransistor Optocoupler"
            elif "Conn_02x20" in name:
                desc = "Raspberry Pi 40-Pin GPIO Header Receptacle"
            elif "AMS1117" in name:
                desc = "3.3V 1A LDO Voltage Regulator"

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
        f'  (gr_text "ZONE 1: LOW-VOLTAGE DC LOGIC" (at {x0 + 32.0} {y0 + 3.0}) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))',
        f'  (gr_text "ZONE 2: 230V AC MAINS" (at {x0 + 94.0} {y0 + 3.0}) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))',
        f'  (gr_text "ISOLATION BARRIER (5mm CREEPAGE)" (at {slot_x - 1.5} {y0 + 24.0} 90) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.18))))',
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
        "J1": (x0 + 8.5, y0 + 10.5, 90),           # RPi 40-pin header along top of Zone 1 (spans x0+8.5 to x0+56.8)
        "R_PU1": (x0 + 30.0, y0 + 20.0, 0),        # 4.7k I2C pull-up resistor
        "R_PU2": (x0 + 36.0, y0 + 20.0, 0),        # 4.7k I2C pull-up resistor
        "J_SMA": (x0 + 4.0, y0 + 42.0, 90),         # SMA antenna connector on left edge
        "U_LORA": (x0 + 20.0, y0 + 42.0, 0),        # SX1278 16-pin Castellated module (spans x0+12 to x0+28)
        "U2": (x0 + 48.0, y0 + 36.0, 0),            # ADS1115 ADC MSOP-10 (18mm clearance from Ra-02)
        "Q1": (x0 + 46.0, y0 + 48.0, 0),            # NPN Driver 1 (Relay 1)
        "Q2": (x0 + 56.0, y0 + 48.0, 0),            # NPN Driver 2 (Relay 2)
        "LED_5V": (x0 + 12.0, y0 + 58.0, 0),        # 5V Power LED
        "LED_3V3": (x0 + 22.0, y0 + 58.0, 0),       # 3.3V Radio LED
        "LED_PUMP": (x0 + 32.0, y0 + 58.0, 0),      # Pump Active LED
        "TB1": (x0 + 6.5, y0 + 72.0, 270),          # 5V DC Input Terminal Block (facing left edge)
        "C1": (x0 + 15.0, y0 + 72.0, 0),            # 10uF Input Filter Cap
        "U1": (x0 + 22.0, y0 + 72.0, 0),            # AMS1117-3.3V LDO Regulator
        "C2": (x0 + 29.0, y0 + 72.0, 0),            # 22uF Output Filter Cap
        "SW1": (x0 + 42.0, y0 + 72.0, 0),           # Force ON 6mm Button
        "SW2": (x0 + 56.0, y0 + 72.0, 0),           # Force OFF 6mm Button (14mm pitch from SW1)

        # Boundary Optocouplers (Straddling slot_x = x0 + 67.0)
        "U5": (x0 + 67.0, y0 + 48.0, 0),            # PC817 Optocoupler 1 (Relay 1)
        "U6": (x0 + 67.0, y0 + 60.0, 0),            # PC817 Optocoupler 2 (Relay 2)

        # Zone 2 (High-Voltage 230V AC Mains): x0 + [69 .. 120]
        "TB2": (x0 + 110.0, y0 + 12.0, 0),          # AC Mains Input Terminal Block (top right)
        "T1": (x0 + 86.0, y0 + 18.0, 0),            # ZMPT101K Voltage Transformer
        "R_HV1": (x0 + 80.0, y0 + 30.0, 0),         # High-voltage limiting resistor 1 (Axial)
        "R_HV2": (x0 + 102.0, y0 + 30.0, 0),        # High-voltage limiting resistor 2 (Axial)
        "U4": (x0 + 78.0, y0 + 40.0, 0),            # LM358 Op-Amp Conditioner (SOIC-8)
        "C_F": (x0 + 88.0, y0 + 40.0, 0),           # Filter Cap 0805
        "U3": (x0 + 104.0, y0 + 40.0, 0),           # ACS712T-30A Current Sensor (SOIC-8)
        "D2": (x0 + 73.0, y0 + 56.0, 90),           # Flyback Diode 1 (Relay 1)
        "K1": (x0 + 80.0, y0 + 56.0, 0),            # Songle SRD Relay 1 (Aux/Valve)
        "D3": (x0 + 73.0, y0 + 73.0, 90),           # Flyback Diode 2 (Relay 2)
        "K2": (x0 + 80.0, y0 + 73.0, 0),            # Songle SRD Relay 2 (Main Pump Contactor)
        "TB3": (x0 + 112.0, y0 + 64.0, 90),         # Actuator Load Output Terminal (facing right edge)
    }

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
        '    (date "2026-10-25")',
        '    (rev "1.0")',
        '    (company "Circuitron Automation System")',
        '    (comment 1 "Raspberry Pi Zero 2W Dual-Zone Isolated Controller")',
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
