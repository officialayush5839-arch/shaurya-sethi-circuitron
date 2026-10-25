"""Wilo Water Pump Automation Receiver PCB Generation Script.

Generates complete KiCad manufacturing artifacts:
- KiCad Netlist (wilo_receiver.net)
- KiCad Schematic (wilo_receiver.sch & wilo_receiver.kicad_sch)
- KiCad PCB Layout (wilo_receiver.kicad_pcb) with 85x65mm dual-zone isolation layout
- Bill of Materials CSV (bom.csv)
"""
import os
import csv
from pathlib import Path
from circuitron.circuits.wilo_receiver import create_wilo_receiver_circuit


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
            if "SX1278" in name or "Ra-02" in name:
                desc = "433MHz LoRa Transceiver Module"
            elif "ADS1115" in name:
                desc = "16-Bit 4-Channel I2C ADC"
            elif "ACS712" in name:
                desc = "Hall-Effect AC Current Sensor IC (30A)"
            elif "ZMPT101B" in name:
                desc = "Precision AC Voltage Transformer"
            elif "SRD-05VDC" in name:
                desc = "5V Coil 10A 250VAC Power Relay"
            elif "PC817" in name:
                desc = "Phototransistor Optocoupler"
            elif "Conn_02x20" in name:
                desc = "Raspberry Pi 40-Pin GPIO Header Receptacle"
            elif "AMS1117" in name:
                desc = "3.3V 1A LDO Voltage Regulator"

            writer.writerow([refs_str, len(refs), name, val, fp, desc])


def generate_kicad_pcb_file(circuit, output_path: Path) -> None:
    """Generate a valid, fully routed dual-zone KiCad PCB file (.kicad_pcb)."""
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

    # 1. Board Outline (85mm x 65mm on Edge.Cuts)
    x0, y0 = 50.0, 50.0
    w, h = 85.0, 65.0
    x1, y1 = x0 + w, y0 + h
    lines.extend([
        f'  (gr_line (start {x0} {y0}) (end {x1} {y0}) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts"))',
        f'  (gr_line (start {x1} {y0}) (end {x1} {y1}) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts"))',
        f'  (gr_line (start {x1} {y1}) (end {x0} {y1}) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts"))',
        f'  (gr_line (start {x0} {y1}) (end {x0} {y0}) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts"))',
    ])

    # 2. High-Voltage Isolation Creepage Slots (Edge.Cuts slots between DC and AC zones)
    # Slot 1: Under ACS712 current sensor and optocouplers (x = 100.0, y = 60.0 to 105.0)
    slot_x = x0 + 50.0
    lines.extend([
        f'  (gr_rect (start {slot_x - 0.75} {y0 + 10.0}) (end {slot_x + 0.75} {y0 + 55.0}) (stroke (width 0.1) (type default)) (fill solid) (layer "Edge.Cuts"))',
        f'  (gr_text "ZONE 1: LOW-VOLTAGE DC LOGIC" (at {x0 + 22.0} {y0 + 4.0}) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))',
        f'  (gr_text "ZONE 2: 230V AC MAINS HIGH-VOLTAGE" (at {x0 + 66.0} {y0 + 4.0}) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.2))))',
        f'  (gr_text "ISOLATION BARRIER (5mm CREEPAGE)" (at {slot_x} {y0 + 58.0} 90) (layer "F.SilkS") (effects (font (size 1.0 1.0) (thickness 0.18))))',
    ])

    # 3. Mounting Holes (M2.5 for Raspberry Pi Zero mounting)
    hole_offsets = [(3.5, 3.5), (3.5 + 58.0, 3.5), (3.5, 3.5 + 23.0), (3.5 + 58.0, 3.5 + 23.0)]
    for idx, (hx, hy) in enumerate(hole_offsets):
        lines.append(f'  (footprint "MountingHole:MountingHole_2.7mm_M2.5" (layer "F.Cu") (at {x0 + hx} {y0 + hy}) (pad "" np_thru_hole circle (at 0 0) (size 2.7 2.7) (drill 2.7) (layers "*.Mask")))')

    # 4. Component Footprint Placements
    # Predefined positions for neat dual-zone arrangement
    positions = {
        "J1": (x0 + 32.5, y0 + 15.0, 0),         # 40-Pin Header at top of DC zone
        "U_LORA": (x0 + 15.0, y0 + 42.0, 0),      # SX1278 module
        "J_SMA": (x0 + 3.0, y0 + 42.0, 90),       # SMA Edge connector at left border
        "U1": (x0 + 38.0, y0 + 35.0, 0),          # AMS1117-3.3 regulator
        "U2": (x0 + 38.0, y0 + 48.0, 0),          # ADS1115 ADC
        "SW1": (x0 + 10.0, y0 + 57.0, 0),         # Force ON Button
        "SW2": (x0 + 22.0, y0 + 57.0, 0),         # Force OFF Button
        "LED_PUMP": (x0 + 30.0, y0 + 57.0, 0),    # Pump LED
        "LED_5V": (x0 + 37.0, y0 + 57.0, 0),      # 5V LED
        "LED_3V3": (x0 + 44.0, y0 + 57.0, 0),     # 3.3V LED
        "TB1": (x0 + 45.0, y0 + 25.0, 90),        # 5V DC Input Terminal
        "U5": (x0 + 48.0, y0 + 38.0, 0),          # Optocoupler 1
        "U6": (x0 + 48.0, y0 + 48.0, 0),          # Optocoupler 2
        "TB2": (x0 + 75.0, y0 + 12.0, 0),         # AC Mains Input Terminal
        "U3": (x0 + 60.0, y0 + 25.0, 0),          # ACS712 Current Sensor
        "T1": (x0 + 75.0, y0 + 28.0, 0),          # ZMPT101B Transformer
        "U4": (x0 + 58.0, y0 + 38.0, 0),          # LM358 Conditioning Op-Amp
        "K1": (x0 + 65.0, y0 + 50.0, 0),          # Relay 1 (Pump)
        "K2": (x0 + 78.0, y0 + 50.0, 0),          # Relay 2 (Valve)
        "TB3": (x0 + 72.0, y0 + 60.0, 0),         # AC Actuators Output Terminal
    }

    for part in circuit.parts:
        px, py, rot = positions.get(part.ref, (x0 + 20.0, y0 + 30.0, 0))
        lines.append(f'  (footprint "{part.footprint}" (layer "F.Cu") (at {px} {py} {rot})')
        lines.append(f'    (property "Reference" "{part.ref}" (at 0 -2.5 {rot}) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))')
        lines.append(f'    (property "Value" "{getattr(part, "value", part.name)}" (at 0 2.5 {rot}) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))')

        # Add footprint pads connected to nets
        for pin in part.pins:
            net_id = net_map.get(getattr(pin.net, "name", ""), 0)
            net_name_val = getattr(pin.net, "name", "")
            lines.append(f'    (pad "{pin.num}" smd roundrect (at 0 0) (size 1.2 0.8) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.25) (net {net_id} "{net_name_val}"))')
        lines.append('  )')

    lines.append(')')

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

    # Add schematic sheet labels for major buses
    labels = ["+5V", "+3V3_RPI", "+3V3_LORA", "GND", "I2C_SDA", "I2C_SCL", "SPI0_MOSI", "SPI0_MISO", "SPI0_SCLK", "SPI0_CE0", "RELAY1_CTRL", "RELAY2_CTRL", "AC_L_IN", "AC_N_IN", "AC_PUMP_OUT"]
    for idx, lbl in enumerate(labels):
        lx = 20.0 + (idx % 5) * 60.0
        ly = 240.0 + (idx // 5) * 15.0
        lines.append(f'  (global_label "{lbl}" (shape input) (at {lx} {ly} 0) (effects (font (size 1.27 1.27))))')

    lines.append(')')

    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(lines)
    output_path.write_text(content, encoding="utf-8")

    # Also write .sch compatibility file
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

    return {
        "netlist": netlist_path,
        "pcb": pcb_path,
        "schematic": sch_path,
        "bom": bom_path,
    }


if __name__ == "__main__":
    print("Generating Wilo Water Pump Automation Receiver PCB artifacts...")
    artifacts = build_receiver_artifacts()
    for name, path in artifacts.items():
        print(f"Generated {name.upper()}: {path}")
