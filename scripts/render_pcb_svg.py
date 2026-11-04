"""High-fidelity 2D Vector SVG Renderer for KiCad PCB layouts."""
import re
import math
from pathlib import Path


def render_kicad_pcb_to_svg(pcb_path: Path, svg_output_path: Path) -> None:
    pcb_text = pcb_path.read_text(encoding="utf-8")

    # Board dimensions from Edge.Cuts lines
    lines = re.findall(r'\(gr_line\s+\(start\s+([\d\.\-]+)\s+([\d\.\-]+)\)\s+\(end\s+([\d\.\-]+)\s+([\d\.\-]+)\).*?\(layer\s+"Edge\.Cuts"\)\)', pcb_text)
    pts = []
    for x1, y1, x2, y2 in lines:
        pts.extend([(float(x1), float(y1)), (float(x2), float(y2))])

    if pts:
        min_x = min(p[0] for p in pts) - 5
        max_x = max(p[0] for p in pts) + 5
        min_y = min(p[1] for p in pts) - 5
        max_y = max(p[1] for p in pts) + 5
    else:
        min_x, min_y, max_x, max_y = 40, 40, 180, 145

    width = max_x - min_x
    height = max_y - min_y
    scale = 10.0  # 10px per mm

    svg_w = width * scale
    svg_h = height * scale

    def tx(x: float) -> float:
        return (x - min_x) * scale

    def ty(y: float) -> float:
        return (y - min_y) * scale

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w:.1f} {svg_h:.1f}" width="{svg_w:.1f}" height="{svg_h:.1f}" style="background:#121815; font-family:Consolas, monospace;">',
        '<defs>',
        '  <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%"><feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.5"/></filter>',
        '</defs>',
    ]

    # Draw board outline
    if pts:
        bx0 = min(p[0] for p in pts)
        by0 = min(p[1] for p in pts)
        bw = max(p[0] for p in pts) - bx0
        bh = max(p[1] for p in pts) - by0
        out.append(f'  <rect x="{tx(bx0):.1f}" y="{ty(by0):.1f}" width="{bw*scale:.1f}" height="{bh*scale:.1f}" rx="{3*scale}" fill="#1B4D3E" stroke="#2D6A4F" stroke-width="2" filter="url(#shadow)"/>')

    # Draw creepage slots
    slots = re.findall(r'\(gr_rect\s+\(start\s+([\d\.\-]+)\s+([\d\.\-]+)\)\s+\(end\s+([\d\.\-]+)\s+([\d\.\-]+)\).*?\(layer\s+"Edge\.Cuts"\)\)', pcb_text)
    for sx1, sy1, sx2, sy2 in slots:
        sx1, sy1, sx2, sy2 = float(sx1), float(sy1), float(sx2), float(sy2)
        rx = min(sx1, sx2)
        ry = min(sy1, sy2)
        rw = abs(sx2 - sx1)
        rh = abs(sy2 - sy1)
        out.append(f'  <rect x="{tx(rx):.1f}" y="{ty(ry):.1f}" width="{rw*scale:.1f}" height="{rh*scale:.1f}" rx="{scale*0.5}" fill="#121815" stroke="#E63946" stroke-width="1.5" stroke-dasharray="4,2"/>')

    # Draw Silkscreen text
    texts = re.findall(r'\(gr_text\s+"([^"]+)"\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\).*?\(layer\s+"F\.SilkS"\)', pcb_text)
    for txt, gx, gy, rot in texts:
        gx, gy = float(gx), float(gy)
        r = float(rot) if rot else 0.0
        transform = f' transform="rotate({r} {tx(gx):.1f} {ty(gy):.1f})"' if r != 0 else ''
        color = "#FFD166" if "ZONE" in txt or "ISOLATION" in txt else "#FFFFFF"
        weight = "bold" if "ZONE" in txt else "normal"
        out.append(f'  <text x="{tx(gx):.1f}" y="{ty(gy):.1f}" fill="{color}" font-size="{scale*1.4:.1f}" font-weight="{weight}" text-anchor="middle" dominant-baseline="middle"{transform}>{txt}</text>')

    # Parse and draw footprints
    # Footprint regex
    fp_pattern = re.compile(
        r'\(footprint\s+"([^"]+)".*?\(layer\s+"F\.Cu"\)\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)(.*?)(?=\n\s*\(footprint|\n\s*\)$)',
        re.DOTALL
    )

    for m in fp_pattern.finditer(pcb_text):
        fp_id = m.group(1)
        fx, fy = float(m.group(2)), float(m.group(3))
        f_rot = float(m.group(4)) if m.group(4) else 0.0
        body = m.group(5)

        ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', body)
        ref = ref_m.group(1) if ref_m else ""
        val_m = re.search(r'\(property\s+"Value"\s+"([^"]+)"', body)
        val = val_m.group(1) if val_m else ""

        # Draw mounting holes
        if "MountingHole" in fp_id:
            out.append(f'  <circle cx="{tx(fx):.1f}" cy="{ty(fy):.1f}" r="{1.35*scale:.1f}" fill="#121815" stroke="#C0C0C0" stroke-width="2"/>')
            continue

        # Draw Component Body representation
        # Transform group for footprint
        out.append(f'  <g transform="translate({tx(fx):.1f}, {ty(fy):.1f}) rotate({f_rot})">')

        # Specific component visuals
        if "SRD_Series" in fp_id or "Relay" in fp_id:
            # Relay body (19mm x 15.5mm)
            out.append(f'    <rect x="0" y="{-7.75*scale:.1f}" width="{19*scale:.1f}" height="{15.5*scale:.1f}" rx="{1*scale}" fill="#1E88E5" stroke="#1565C0" stroke-width="2"/>')
            out.append(f'    <text x="{9.5*scale:.1f}" y="0" fill="#FFFFFF" font-size="{scale*1.5:.1f}" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{ref}</text>')
            out.append(f'    <text x="{9.5*scale:.1f}" y="{3*scale:.1f}" fill="#BBDEFB" font-size="{scale*1.0:.1f}" text-anchor="middle">{val}</text>')
        elif "Ai-Thinker-Ra-01" in fp_id or "Ra-0" in fp_id:
            # LoRa Module (16mm x 16mm)
            out.append(f'    <rect x="{-8*scale:.1f}" y="{-8*scale:.1f}" width="{16*scale:.1f}" height="{16*scale:.1f}" rx="{1*scale}" fill="#263238" stroke="#78909C" stroke-width="2"/>')
            out.append(f'    <rect x="{-6*scale:.1f}" y="{-6*scale:.1f}" width="{12*scale:.1f}" height="{10*scale:.1f}" rx="{0.5*scale}" fill="#37474F" stroke="#90A4AE" stroke-width="1"/>')
            out.append(f'    <text x="0" y="{-1*scale:.1f}" fill="#ECEFF1" font-size="{scale*1.3:.1f}" font-weight="bold" text-anchor="middle">{ref}</text>')
            out.append(f'    <text x="0" y="{2*scale:.1f}" fill="#80CBC4" font-size="{scale*0.9:.1f}" text-anchor="middle">433MHz LoRa</text>')
        elif "PinSocket_2x20" in fp_id:
            # 40-pin header (2.54mm x 20, ~51mm x 5mm)
            out.append(f'    <rect x="{-3.87*scale:.1f}" y="{-1.33*scale:.1f}" width="{5.2*scale:.1f}" height="{51*scale:.1f}" rx="{1*scale}" fill="#212121" stroke="#FFB703" stroke-width="1.5"/>')
            out.append(f'    <text x="{7*scale:.1f}" y="{25*scale:.1f}" fill="#FFD166" font-size="{scale*1.3:.1f}" font-weight="bold" text-anchor="start">{ref} (Raspberry Pi Zero 2W HAT)</text>')
        elif "ZMPT101" in fp_id:
            # Voltage Transformer (~18mm x 18mm)
            out.append(f'    <rect x="{-9*scale:.1f}" y="{-9*scale:.1f}" width="{18*scale:.1f}" height="{18*scale:.1f}" rx="{2*scale}" fill="#1B263B" stroke="#415A77" stroke-width="2"/>')
            out.append(f'    <circle cx="0" cy="0" r="{6*scale:.1f}" fill="#0D1B2A" stroke="#778DA9" stroke-width="1.5"/>')
            out.append(f'    <text x="0" y="0" fill="#E0E1DD" font-size="{scale*1.3:.1f}" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{ref}</text>')
            out.append(f'    <text x="0" y="{12*scale:.1f}" fill="#E0E1DD" font-size="{scale*0.9:.1f}" text-anchor="middle">ZMPT101B</text>')
        elif "TerminalBlock" in fp_id:
            # Terminal block
            tb_pins = 3 if "1x03" in fp_id else 2
            tb_w = tb_pins * 5.08
            tb_h = 8.0
            out.append(f'    <rect x="{-tb_w*0.5*scale:.1f}" y="{-tb_h*0.5*scale:.1f}" width="{tb_w*scale:.1f}" height="{tb_h*scale:.1f}" rx="{1*scale}" fill="#2E7D32" stroke="#4CAF50" stroke-width="2"/>')
            for p_idx in range(tb_pins):
                px_pos = (-tb_w * 0.5 + 2.54 + p_idx * 5.08) * scale
                out.append(f'    <circle cx="{px_pos:.1f}" cy="0" r="{1.5*scale:.1f}" fill="#E0E0E0" stroke="#757575" stroke-width="1"/>')
            out.append(f'    <text x="0" y="{-6*scale:.1f}" fill="#A5D6A7" font-size="{scale*1.1:.1f}" font-weight="bold" text-anchor="middle">{ref} ({val})</text>')
        elif "SW_PUSH" in fp_id:
            # 6mm button
            out.append(f'    <rect x="{-3*scale:.1f}" y="{-3*scale:.1f}" width="{6*scale:.1f}" height="{6*scale:.1f}" rx="{0.5*scale}" fill="#424242" stroke="#9E9E9E" stroke-width="1.5"/>')
            out.append(f'    <circle cx="0" cy="0" r="{1.7*scale:.1f}" fill="#D32F2F" stroke="#B71C1C" stroke-width="1"/>')
            out.append(f'    <text x="0" y="{-5*scale:.1f}" fill="#EF9A9A" font-size="{scale*1.0:.1f}" font-weight="bold" text-anchor="middle">{ref} ({val})</text>')
        elif "SOIC-8" in fp_id or "MSOP-10" in fp_id or "DIP-4" in fp_id or "SOT-223" in fp_id or "SOT-23" in fp_id:
            # IC Chip
            ic_w = 4.0 if "MSOP" in fp_id else (5.0 if "SOIC" in fp_id else (6.5 if "SOT-223" in fp_id else 3.0))
            ic_h = 4.0 if "MSOP" in fp_id else (5.0 if "SOIC" in fp_id else (3.5 if "SOT-223" in fp_id else 3.0))
            out.append(f'    <rect x="{-ic_w*0.5*scale:.1f}" y="{-ic_h*0.5*scale:.1f}" width="{ic_w*scale:.1f}" height="{ic_h*scale:.1f}" rx="{0.5*scale}" fill="#111111" stroke="#616161" stroke-width="1.2"/>')
            out.append(f'    <circle cx="{-ic_w*0.5*scale + 1*scale:.1f}" cy="{-ic_h*0.5*scale + 1*scale:.1f}" r="{0.4*scale:.1f}" fill="#FFFFFF"/>')
            out.append(f'    <text x="0" y="{-ic_h*0.5*scale - 1.5*scale:.1f}" fill="#E0E0E0" font-size="{scale*1.0:.1f}" font-weight="bold" text-anchor="middle">{ref}</text>')
            out.append(f'    <text x="0" y="{ic_h*0.5*scale + 2.5*scale:.1f}" fill="#9E9E9E" font-size="{scale*0.8:.1f}" text-anchor="middle">{val}</text>')
        elif "SMA" in fp_id:
            out.append(f'    <circle cx="0" cy="0" r="{3*scale:.1f}" fill="#F59E0B" stroke="#B45309" stroke-width="1.5"/>')
            out.append(f'    <circle cx="0" cy="0" r="{1*scale:.1f}" fill="#FFFFFF"/>')
            out.append(f'    <text x="0" y="{-5*scale:.1f}" fill="#FCD34D" font-size="{scale*1.0:.1f}" font-weight="bold" text-anchor="middle">{ref} (ANT)</text>')
        elif "LED" in fp_id:
            led_col = "#22C55E" if "PUMP" in ref or "5V" in ref else "#3B82F6"
            out.append(f'    <rect x="{-1*scale:.1f}" y="{-0.6*scale:.1f}" width="{2*scale:.1f}" height="{1.2*scale:.1f}" fill="{led_col}" stroke="#FFFFFF" stroke-width="0.8"/>')
            out.append(f'    <text x="0" y="{-2*scale:.1f}" fill="{led_col}" font-size="{scale*0.85:.1f}" font-weight="bold" text-anchor="middle">{ref}</text>')
        else:
            # Generic 0805 or axial
            out.append(f'    <rect x="{-1*scale:.1f}" y="{-0.5*scale:.1f}" width="{2*scale:.1f}" height="{1*scale:.1f}" fill="#424242" stroke="#9E9E9E" stroke-width="0.8"/>')
            out.append(f'    <text x="0" y="{-1.8*scale:.1f}" fill="#B0BEC5" font-size="{scale*0.85:.1f}" text-anchor="middle">{ref}</text>')

        # Draw footprint pads
        pads = re.findall(r'\(pad\s+"?([^"\s)]+)"?\s+(smd|thru_hole)\s+([^\s]+)\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)\s+\(size\s+([\d\.\-]+)\s+([\d\.\-]+)\)', body)
        for p_num, p_type, p_shape, px, py, p_rot, pw, ph in pads:
            px, py, pw, ph = float(px), float(py), float(pw), float(ph)
            pad_fill = "#D4AF37" if p_type == "smd" else "#F4D03F"
            if p_shape == "circle":
                out.append(f'    <circle cx="{px*scale:.1f}" cy="{py*scale:.1f}" r="{pw*0.5*scale:.1f}" fill="{pad_fill}" stroke="#B7950B" stroke-width="0.5"/>')
                if p_type == "thru_hole":
                    out.append(f'    <circle cx="{px*scale:.1f}" cy="{py*scale:.1f}" r="{pw*0.25*scale:.1f}" fill="#121815"/>')
            else:
                out.append(f'    <rect x="{(px - pw*0.5)*scale:.1f}" y="{(py - ph*0.5)*scale:.1f}" width="{pw*scale:.1f}" height="{ph*scale:.1f}" rx="{0.2*scale}" fill="{pad_fill}" stroke="#B7950B" stroke-width="0.5"/>')

        out.append('  </g>')

    out.append('</svg>')

    svg_output_path.parent.mkdir(parents=True, exist_ok=True)
    svg_output_path.write_text("\n".join(out), encoding="utf-8")
    print(f"Rendered PCB SVG to {svg_output_path} ({len(out)} elements).")


if __name__ == "__main__":
    pcb_file = Path("output/wilo_receiver/wilo_receiver.kicad_pcb")
    svg_file = Path("output/wilo_receiver/wilo_receiver_2d_layout.svg")
    render_kicad_pcb_to_svg(pcb_file, svg_file)
