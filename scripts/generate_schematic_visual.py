"""Generate high-resolution visual schematic diagram (PNG) for Wilo Receiver Station.

Renders an A3 engineering schematic diagram with 7 cleanly framed functional circuit blocks,
standard schematic symbols, net labels, power rails, wire connections, and a professional title block.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def create_schematic_diagram(png_output: Path) -> None:
    # A3 dimensions at 200 DPI: 3508 x 2480
    W, H = 3508, 2480
    img = Image.new("RGB", (W, H), color="#FFFFFF")
    draw = ImageDraw.Draw(img)

    # Load system fonts
    try:
        font_title = ImageFont.truetype("segoeuib.ttf", 32)
        font_subtitle = ImageFont.truetype("segoeui.ttf", 18)
        font_sec_hdr = ImageFont.truetype("segoeuib.ttf", 20)
        font_ref = ImageFont.truetype("segoeuib.ttf", 16)
        font_val = ImageFont.truetype("segoeui.ttf", 14)
        font_pin = ImageFont.truetype("consola.ttf", 12)
        font_net = ImageFont.truetype("consolab.ttf", 13)
        font_small = ImageFont.truetype("segoeui.ttf", 12)
    except Exception:
        font_title = ImageFont.load_default()
        font_subtitle = font_title
        font_sec_hdr = font_title
        font_ref = font_title
        font_val = font_title
        font_pin = font_title
        font_net = font_title
        font_small = font_title

    # Palette
    BORDER_CLR = "#7B1113"       # Classic dark red / burgundy schematic border
    FRAME_CLR = "#0B3C5D"        # Engineering navy for block frames
    HEADER_BG = "#E8EEF5"        # Soft blue-grey header background
    WIRE_CLR = "#005500"         # Traditional schematic wire dark green
    NET_CLR = "#003366"          # Net label text
    POWER_CLR = "#B22222"        # Crimson power rails (+5V, +3V3)
    GND_CLR = "#222222"          # Dark grey ground
    SYM_BODY = "#FFFDF2"         # IC box warm cream fill
    SYM_BORDER = "#111111"       # Clean black lines
    PIN_CLR = "#333333"          # Pin numbers / text
    JUNCTION_CLR = "#005500"     # Wire junctions

    # -------------------------------------------------------------
    # 1. OUTER A3 BORDER & GRID
    # -------------------------------------------------------------
    margin = 40
    draw.rectangle([margin, margin, W - margin, H - margin], outline=BORDER_CLR, width=4)
    inner_m = margin + 14
    draw.rectangle([inner_m, inner_m, W - inner_m, H - inner_m], outline=BORDER_CLR, width=2)

    # Grid tick marks & labels
    cols = 8
    rows = 6
    col_w = (W - 2 * inner_m) / cols
    row_h = (H - 2 * inner_m) / rows
    for i in range(1, cols):
        x = inner_m + i * col_w
        draw.line([x, margin, x, inner_m], fill=BORDER_CLR, width=1)
        draw.line([x, H - inner_m, x, H - margin], fill=BORDER_CLR, width=1)
        draw.text((x - col_w / 2, margin + 2), str(i), fill=BORDER_CLR, font=font_small, anchor="mm")
        draw.text((x - col_w / 2, H - margin - 6), str(i), fill=BORDER_CLR, font=font_small, anchor="mm")
    draw.text((W - inner_m - col_w / 2, margin + 2), str(cols), fill=BORDER_CLR, font=font_small, anchor="mm")
    draw.text((W - inner_m - col_w / 2, H - margin - 6), str(cols), fill=BORDER_CLR, font=font_small, anchor="mm")

    row_labels = ["A", "B", "C", "D", "E", "F"]
    for j in range(1, rows):
        y = inner_m + j * row_h
        draw.line([margin, y, inner_m, y], fill=BORDER_CLR, width=1)
        draw.line([W - inner_m, y, W - margin, y], fill=BORDER_CLR, width=1)
        draw.text((margin + 6, y - row_h / 2), row_labels[j - 1], fill=BORDER_CLR, font=font_small, anchor="mm")
        draw.text((W - margin - 6, y - row_h / 2), row_labels[j - 1], fill=BORDER_CLR, font=font_small, anchor="mm")
    draw.text((margin + 6, H - inner_m - row_h / 2), row_labels[-1], fill=BORDER_CLR, font=font_small, anchor="mm")
    draw.text((W - margin - 6, H - inner_m - row_h / 2), row_labels[-1], fill=BORDER_CLR, font=font_small, anchor="mm")

    # -------------------------------------------------------------
    # 2. TITLE BLOCK (Bottom-Right) & NOTES (Bottom-Left)
    # -------------------------------------------------------------
    tb_w = 840
    tb_h = 160
    tb_x1 = W - inner_m - tb_w
    tb_y1 = H - inner_m - tb_h
    tb_x2 = W - inner_m
    tb_y2 = H - inner_m

    draw.rectangle([tb_x1, tb_y1, tb_x2, tb_y2], fill="#FAFAFA", outline=BORDER_CLR, width=2)
    draw.line([tb_x1, tb_y1 + 50, tb_x2, tb_y1 + 50], fill=BORDER_CLR, width=2)
    draw.line([tb_x1, tb_y1 + 105, tb_x2, tb_y1 + 105], fill=BORDER_CLR, width=1)
    draw.line([tb_x1 + 580, tb_y1 + 50, tb_x1 + 580, tb_y2], fill=BORDER_CLR, width=1)

    draw.text((tb_x1 + 20, tb_y1 + 25), "WILO WATER PUMP AUTOMATION — RECEIVER STATION", fill="#111111", font=font_title, anchor="lm")
    draw.text((tb_x1 + 20, tb_y1 + 75), "Hardware: Raspberry Pi Zero 2W HAT • Dimensions: 140 mm × 95 mm", fill="#333333", font=font_subtitle, anchor="lm")
    draw.text((tb_x1 + 20, tb_y1 + 130), "Power: 100% 5V DC via USB-C • TB2: Voltage Sense Only • Single Ground Plane", fill="#444444", font=font_val, anchor="lm")

    draw.text((tb_x1 + 600, tb_y1 + 75), "Rev: 3.0", fill="#B22222", font=font_subtitle, anchor="lm")
    draw.text((tb_x1 + 600, tb_y1 + 130), "Sheet: 1 / 1 (A3) • 2026-11-07", fill="#444444", font=font_val, anchor="lm")

    # Bottom Notes Banner
    notes_x1 = inner_m + 15
    notes_y1 = tb_y1
    notes_x2 = tb_x1 - 15
    notes_y2 = tb_y2
    draw.rectangle([notes_x1, notes_y1, notes_x2, notes_y2], fill="#F8FAFC", outline=FRAME_CLR, width=1)
    draw.text((notes_x1 + 20, notes_y1 + 30), "SYSTEM ARCHITECTURE & DESIGN NOTES:", fill=FRAME_CLR, font=font_ref, anchor="lm")
    draw.text((notes_x1 + 20, notes_y1 + 65),
              "1. MAIN POWER: System logic, RPi Zero 2W, relays, sensors & LoRa are powered strictly via 5V DC USB-C (J_USBC). No onboard AC-DC supply.",
              fill="#333333", font=font_val, anchor="lm")
    draw.text((notes_x1 + 20, notes_y1 + 95),
              "2. AC VOLTAGE SENSING: TB2 is strictly for AC line voltage sampling via ZMPT101B potential transformer. Never use TB2 as a power source.",
              fill="#900C3F", font=font_val, anchor="lm")
    draw.text((notes_x1 + 20, notes_y1 + 125),
              "3. GROUNDING & ISOLATION: Single unified ground plane layout with >6.0mm creepage clearance for high-voltage sensor & relay traces.",
              fill="#333333", font=font_val, anchor="lm")

    # Graphic Helper Functions
    def draw_junction(x: float, y: float) -> None:
        r = 3.5
        draw.ellipse([x - r, y - r, x + r, y + r], fill=JUNCTION_CLR, outline=JUNCTION_CLR)

    def draw_gnd(x: float, y: float) -> None:
        draw.line([x, y, x, y + 12], fill=GND_CLR, width=2)
        draw.line([x - 14, y + 12, x + 14, y + 12], fill=GND_CLR, width=3)
        draw.line([x - 9, y + 17, x + 9, y + 17], fill=GND_CLR, width=2)
        draw.line([x - 4, y + 22, x + 4, y + 22], fill=GND_CLR, width=2)

    def draw_pwr(x: float, y: float, label: str) -> None:
        draw.line([x, y, x, y - 10], fill=POWER_CLR, width=2)
        draw.polygon([(x, y - 20), (x - 7, y - 10), (x + 7, y - 10)], fill=POWER_CLR)
        draw.text((x, y - 32), label, fill=POWER_CLR, font=font_net, anchor="mm")

    def draw_net_label(x: float, y: float, name: str, align: str = "lm", bg: str = "#EBF5FB") -> None:
        bbox = draw.textbbox((x, y), name, font=font_net, anchor=align)
        pad = 3
        draw.rectangle([bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad], fill=bg, outline="#A9CCE3", width=1)
        draw.text((x, y), name, fill=NET_CLR, font=font_net, anchor=align)

    def draw_resistor(x: float, y: float, ref: str, val: str, horiz: bool = True) -> None:
        rw, rh = (44, 16) if horiz else (16, 44)
        x1, y1 = x - rw / 2, y - rh / 2
        x2, y2 = x + rw / 2, y + rh / 2
        draw.rectangle([x1, y1, x2, y2], fill="#FFFFFF", outline=SYM_BORDER, width=2)
        if horiz:
            draw.line([x - rw / 2 - 14, y, x - rw / 2, y], fill=WIRE_CLR, width=2)
            draw.line([x + rw / 2, y, x + rw / 2 + 14, y], fill=WIRE_CLR, width=2)
            draw.text((x, y - 16), ref, fill="#000088", font=font_ref, anchor="mm")
            draw.text((x, y + 16), val, fill="#333333", font=font_val, anchor="mm")
        else:
            draw.line([x, y - rh / 2 - 14, x, y - rh / 2], fill=WIRE_CLR, width=2)
            draw.line([x, y + rh / 2, x, y + rh / 2 + 14], fill=WIRE_CLR, width=2)
            draw.text((x - 18, y), ref, fill="#000088", font=font_ref, anchor="rm")
            draw.text((x + 18, y), val, fill="#333333", font=font_val, anchor="lm")

    def draw_capacitor(x: float, y: float, ref: str, val: str, horiz: bool = False, polarized: bool = False) -> None:
        if horiz:
            draw.line([x - 20, y, x - 3, y], fill=WIRE_CLR, width=2)
            draw.line([x - 3, y - 14, x - 3, y + 14], fill=SYM_BORDER, width=3)
            draw.line([x + 3, y - 14, x + 3, y + 14], fill=SYM_BORDER, width=3)
            draw.line([x + 3, y, x + 20, y], fill=WIRE_CLR, width=2)
            draw.text((x, y - 22), ref, fill="#000088", font=font_ref, anchor="mm")
            draw.text((x, y + 22), val, fill="#333333", font=font_val, anchor="mm")
            if polarized:
                draw.text((x - 12, y - 12), "+", fill="#B22222", font=font_ref, anchor="mm")
        else:
            draw.line([x, y - 20, x, y - 3], fill=WIRE_CLR, width=2)
            draw.line([x - 14, y - 3, x + 14, y - 3], fill=SYM_BORDER, width=3)
            draw.line([x - 14, y + 3, x + 14, y + 3], fill=SYM_BORDER, width=3)
            draw.line([x, y + 3, x, y + 20], fill=WIRE_CLR, width=2)
            draw.text((x - 22, y), ref, fill="#000088", font=font_ref, anchor="rm")
            draw.text((x + 22, y), val, fill="#333333", font=font_val, anchor="lm")
            if polarized:
                draw.text((x - 14, y - 12), "+", fill="#B22222", font=font_ref, anchor="mm")

    def draw_diode(x: float, y: float, ref: str, val: str, direction: str = "down") -> None:
        dw = 20
        if direction == "down":
            draw.line([x, y - 20, x, y - 8], fill=WIRE_CLR, width=2)
            draw.polygon([(x - dw / 2, y - 8), (x + dw / 2, y - 8), (x, y + 8)], fill="#FFFFFF", outline=SYM_BORDER)
            draw.line([x - dw / 2, y + 8, x + dw / 2, y + 8], fill=SYM_BORDER, width=3)
            draw.line([x, y + 8, x, y + 20], fill=WIRE_CLR, width=2)
            draw.text((x + 18, y - 2), ref, fill="#000088", font=font_ref, anchor="lm")
            draw.text((x + 18, y + 14), val, fill="#333333", font=font_val, anchor="lm")
        elif direction == "up":
            # Cathode at top (bar at y - 8), Anode at bottom (base at y + 8, tip at y - 8)
            draw.line([x, y - 20, x, y - 8], fill=WIRE_CLR, width=2)
            draw.line([x - dw / 2, y - 8, x + dw / 2, y - 8], fill=SYM_BORDER, width=3)
            draw.polygon([(x - dw / 2, y + 8), (x + dw / 2, y + 8), (x, y - 8)], fill="#FFFFFF", outline=SYM_BORDER)
            draw.line([x, y + 8, x, y + 20], fill=WIRE_CLR, width=2)
            draw.text((x + 18, y - 6), ref, fill="#000088", font=font_ref, anchor="lm")
            draw.text((x + 18, y + 10), val, fill="#333333", font=font_val, anchor="lm")
        else:  # right
            draw.line([x - 20, y, x - 8, y], fill=WIRE_CLR, width=2)
            draw.polygon([(x - 8, y - dw / 2), (x - 8, y + dw / 2), (x + 8, y)], fill="#FFFFFF", outline=SYM_BORDER)
            draw.line([x + 8, y - dw / 2, x + 8, y + dw / 2], fill=SYM_BORDER, width=3)
            draw.line([x + 8, y, x + 20, y], fill=WIRE_CLR, width=2)
            draw.text((x, y - 18), ref, fill="#000088", font=font_ref, anchor="mm")
            draw.text((x, y + 18), val, fill="#333333", font=font_val, anchor="mm")

    def draw_led(x: float, y: float, ref: str, color_name: str, points_down: bool = True) -> None:
        draw_diode(x, y, ref, f"LED ({color_name})", direction="down" if points_down else "right")
        draw.line([x + 10, y - 6, x + 22, y - 18], fill="#FF8C00", width=2)
        draw.line([x + 16, y - 2, x + 28, y - 14], fill="#FF8C00", width=2)

    def draw_transistor_npn(x: float, y: float, ref: str, val: str) -> None:
        draw.line([x - 14, y, x - 6, y], fill=WIRE_CLR, width=2)
        draw.line([x - 6, y - 16, x - 6, y + 16], fill=SYM_BORDER, width=3)
        draw.line([x - 6, y - 8, x + 12, y - 20], fill=SYM_BORDER, width=2)
        draw.line([x + 12, y - 20, x + 12, y - 32], fill=WIRE_CLR, width=2)
        draw.line([x - 6, y + 8, x + 12, y + 20], fill=SYM_BORDER, width=2)
        draw.polygon([(x + 12, y + 20), (x + 3, y + 16), (x + 8, y + 11)], fill=SYM_BORDER)
        draw.line([x + 12, y + 20, x + 12, y + 32], fill=WIRE_CLR, width=2)
        draw.text((x + 22, y - 8), ref, fill="#000088", font=font_ref, anchor="lm")
        draw.text((x + 22, y + 8), val, fill="#333333", font=font_val, anchor="lm")

    def draw_block_frame(x1: float, y1: float, x2: float, y2: float, title: str) -> None:
        draw.rectangle([x1, y1, x2, y2], fill="#FAFDFF", outline=FRAME_CLR, width=2)
        hdr_h = 32
        draw.rectangle([x1, y1, x2, y1 + hdr_h], fill=HEADER_BG, outline=FRAME_CLR, width=1)
        draw.text((x1 + 14, y1 + hdr_h / 2), title, fill=FRAME_CLR, font=font_sec_hdr, anchor="lm")

    # Layout Coordinates:
    # Row 1 (y: 75 to 780): Block 1, Block 2, Block 3
    # Row 2 (y: 800 to 1500): Block 4, Block 5, Block 6
    # Row 3 (y: 1520 to 2220): Block 7

    # -------------------------------------------------------------
    # 3. BLOCK 1: RASPBERRY PI ZERO 2W & UI
    # -------------------------------------------------------------
    b1_x1, b1_y1, b1_x2, b1_y2 = inner_m + 15, 75, 1160, 780
    draw_block_frame(b1_x1, b1_y1, b1_x2, b1_y2, "BLOCK 1: RASPBERRY PI ZERO 2W INTERFACE (J1 40-PIN HEADER) & UI")

    # J1 Header Box (shifted right so left labels fit with generous margin)
    j1_x, j1_y = b1_x1 + 130, 130
    j1_w, j1_h = 430, 620
    draw.rectangle([j1_x, j1_y, j1_x + j1_w, j1_y + j1_h], fill=SYM_BODY, outline=SYM_BORDER, width=2)
    draw.text((j1_x + j1_w / 2, j1_y + 18), "J1: RASPBERRY PI ZERO 2W", fill="#000088", font=font_sec_hdr, anchor="mm")
    draw.text((j1_x + j1_w / 2, j1_y + 38), "40-Pin GPIO Expansion Socket", fill="#555555", font=font_small, anchor="mm")

    left_pins = [
        ("1", "+3V3_RPI", "3.3V Power"),
        ("3", "I2C_SDA", "GPIO 2 (SDA)"),
        ("5", "I2C_SCL", "GPIO 3 (SCL)"),
        ("7", "NC", "GPIO 4"),
        ("9", "GND", "Ground"),
        ("11", "RELAY1_CTRL", "GPIO 17"),
        ("13", "RELAY2_CTRL", "GPIO 27"),
        ("15", "LED_PUMP_RUN", "GPIO 22"),
        ("17", "+3V3_RPI", "3.3V Power"),
        ("19", "SPI0_MOSI", "GPIO 10"),
        ("21", "SPI0_MISO", "GPIO 9"),
        ("23", "SPI0_SCLK", "GPIO 11"),
        ("25", "GND", "Ground"),
        ("27", "NC", "ID_SD"),
        ("29", "BTN_FORCE_ON", "GPIO 5"),
        ("31", "BTN_FORCE_OFF", "GPIO 6"),
        ("33", "NC", "GPIO 13"),
        ("35", "NC", "GPIO 19"),
        ("37", "NC", "GPIO 26"),
        ("39", "GND", "Ground"),
    ]
    right_pins = [
        ("2", "+5V", "5V Power"),
        ("4", "+5V", "5V Power"),
        ("6", "GND", "Ground"),
        ("8", "NC", "GPIO 14 (TX)"),
        ("10", "NC", "GPIO 15 (RX)"),
        ("12", "NC", "GPIO 18"),
        ("14", "GND", "Ground"),
        ("16", "NC", "GPIO 23"),
        ("18", "LORA_RST", "GPIO 24"),
        ("20", "GND", "Ground"),
        ("22", "LORA_DIO0", "GPIO 25"),
        ("24", "SPI0_CE0", "GPIO 8"),
        ("26", "NC", "GPIO 7"),
        ("28", "NC", "ID_SC"),
        ("30", "GND", "Ground"),
        ("32", "NC", "GPIO 12"),
        ("34", "GND", "Ground"),
        ("36", "NC", "GPIO 16"),
        ("38", "NC", "GPIO 20"),
        ("40", "NC", "GPIO 21"),
    ]

    p_y_start = j1_y + 60
    p_dy = 27
    for idx, (pnum, net, desc) in enumerate(left_pins):
        py = p_y_start + idx * p_dy
        draw.line([j1_x - 20, py, j1_x, py], fill=WIRE_CLR, width=2)
        draw.text((j1_x + 8, py), f"[{pnum:>2}]", fill=PIN_CLR, font=font_pin, anchor="lm")
        draw.text((j1_x + 40, py), net, fill=NET_CLR, font=font_net, anchor="lm")
        draw.text((j1_x + 140, py), desc, fill="#777777", font=font_small, anchor="lm")
        if net not in ("NC", "GND"):
            draw_net_label(j1_x - 24, py, net, align="rm")
        elif net == "GND":
            draw_gnd(j1_x - 20, py)

    for idx, (pnum, net, desc) in enumerate(right_pins):
        py = p_y_start + idx * p_dy
        draw.line([j1_x + j1_w, py, j1_x + j1_w + 20, py], fill=WIRE_CLR, width=2)
        draw.text((j1_x + j1_w - 8, py), f"[{pnum:>2}]", fill=PIN_CLR, font=font_pin, anchor="rm")
        draw.text((j1_x + j1_w - 40, py), net, fill=NET_CLR, font=font_net, anchor="rm")
        draw.text((j1_x + j1_w - 140, py), desc, fill="#777777", font=font_small, anchor="rm")
        if net not in ("NC", "GND"):
            draw_net_label(j1_x + j1_w + 24, py, net, align="lm")
        elif net == "GND":
            draw_gnd(j1_x + j1_w + 20, py)

    # Push buttons SW1 (Force ON) and SW2 (Force OFF)
    sw_x = 760
    for sw_name, sw_label, net_name, sw_y in [
        ("SW1", "FORCE ON", "BTN_FORCE_ON", 180),
        ("SW2", "FORCE OFF", "BTN_FORCE_OFF", 300)
    ]:
        draw.rectangle([sw_x, sw_y, sw_x + 120, sw_y + 70], fill="#FFFFFF", outline=SYM_BORDER, width=2)
        draw.text((sw_x + 60, sw_y + 18), sw_name, fill="#000088", font=font_ref, anchor="mm")
        draw.text((sw_x + 60, sw_y + 36), sw_label, fill="#222222", font=font_val, anchor="mm")
        draw.text((sw_x + 60, sw_y + 54), "Tactile 6x6mm", fill="#666666", font=font_small, anchor="mm")
        draw.line([sw_x - 30, sw_y + 36, sw_x, sw_y + 36], fill=WIRE_CLR, width=2)
        draw_net_label(sw_x - 34, sw_y + 36, net_name, align="rm")
        draw.line([sw_x + 120, sw_y + 36, sw_x + 150, sw_y + 36], fill=WIRE_CLR, width=2)
        draw_gnd(sw_x + 150, sw_y + 36)

    # Status LEDs: 5V PWR, 3V3 RF, PUMP RUN
    led_x = 940
    draw_pwr(led_x, 150, "+5V")
    draw_resistor(led_x, 215, "R_LED2", "1kΩ", horiz=False)
    draw_led(led_x, 290, "LED_5V", "Green", points_down=True)
    draw_gnd(led_x, 325)

    draw_pwr(led_x + 90, 150, "+3V3_RPI")
    draw_resistor(led_x + 90, 215, "R_LED3", "1kΩ", horiz=False)
    draw_led(led_x + 90, 290, "LED_3V3", "Blue", points_down=True)
    draw_gnd(led_x + 90, 325)

    draw_net_label(sw_x - 34, 460, "LED_PUMP_RUN", align="rm")
    draw.line([sw_x - 30, 460, sw_x + 10, 460], fill=WIRE_CLR, width=2)
    draw_resistor(sw_x + 40, 460, "R_LED1", "330Ω", horiz=True)
    draw.line([sw_x + 70, 460, sw_x + 110, 460], fill=WIRE_CLR, width=2)
    draw_led(sw_x + 145, 460, "LED_PUMP", "Amber", points_down=False)
    draw.line([sw_x + 175, 460, sw_x + 210, 460], fill=WIRE_CLR, width=2)
    draw_gnd(sw_x + 210, 460)

    # -------------------------------------------------------------
    # 4. BLOCK 2: SX1278 Ra-02 LoRa TRANSCEIVER & RF
    # -------------------------------------------------------------
    b2_x1, b2_y1, b2_x2, b2_y2 = 1185, 75, 2300, 780
    draw_block_frame(b2_x1, b2_y1, b2_x2, b2_y2, "BLOCK 2: Ai-Thinker Ra-02 (SX1278 433MHz LoRa TRANSCEIVER) & 50Ω RF")

    lora_x, lora_y, lora_w, lora_h = 1460, 160, 420, 520
    draw.rectangle([lora_x, lora_y, lora_x + lora_w, lora_y + lora_h], fill=SYM_BODY, outline=SYM_BORDER, width=2)
    draw.text((lora_x + lora_w / 2, lora_y + 25), "U_LORA: Ai-Thinker Ra-02", fill="#000088", font=font_sec_hdr, anchor="mm")
    draw.text((lora_x + lora_w / 2, lora_y + 55), "Semtech SX1278 433MHz Transceiver", fill="#555555", font=font_val, anchor="mm")

    lora_pins = [
        ("GND", "GND", 110),
        ("+3V3_LORA", "3.3V Power", 160),
        ("LORA_RST", "RESET", 210),
        ("LORA_DIO0", "DIO0 (IRQ)", 260),
        ("SPI0_SCLK", "SCK", 310),
        ("SPI0_MISO", "MISO", 360),
        ("SPI0_MOSI", "MOSI", 410),
        ("SPI0_CE0", "NSS (CS)", 460),
    ]
    for net, pname, py_rel in lora_pins:
        py = lora_y + py_rel
        draw.line([lora_x - 30, py, lora_x, py], fill=WIRE_CLR, width=2)
        draw.text((lora_x + 12, py), pname, fill=PIN_CLR, font=font_pin, anchor="lm")
        if net == "GND":
            draw_gnd(lora_x - 30, py)
        elif net == "+3V3_LORA":
            draw_pwr(lora_x - 30, py, "+3V3_LORA")
        else:
            draw_net_label(lora_x - 34, py, net, align="rm")

    # Decoupling Caps for LoRa (placed horizontally at bottom left of Block 2)
    draw_pwr(1260, 520, "+3V3_LORA")
    draw.line([1260, 520, 1260, 580], fill=WIRE_CLR, width=2)
    draw_capacitor(1260, 610, "C_LORA1", "10µF", horiz=False, polarized=True)
    draw_gnd(1260, 645)

    draw_pwr(1340, 520, "+3V3_LORA")
    draw.line([1340, 520, 1340, 580], fill=WIRE_CLR, width=2)
    draw_capacitor(1340, 610, "C_LORA2", "0.1µF", horiz=False)
    draw_gnd(1340, 645)

    # Antenna output on right
    ant_y = lora_y + 260
    draw.line([lora_x + lora_w, ant_y, lora_x + lora_w + 120, ant_y], fill="#B22222", width=4)
    draw.text((lora_x + lora_w - 12, ant_y), "ANT", fill=PIN_CLR, font=font_pin, anchor="rm")
    draw.text((lora_x + lora_w + 60, ant_y - 14), "50Ω Microstrip Trace", fill="#B22222", font=font_small, anchor="mm")

    # SMA Connector Symbol
    sma_x, sma_y = lora_x + lora_w + 120, ant_y
    draw.rectangle([sma_x, sma_y - 45, sma_x + 80, sma_y + 45], fill="#FFFFFF", outline=SYM_BORDER, width=2)
    draw.text((sma_x + 40, sma_y - 20), "J_SMA", fill="#000088", font=font_ref, anchor="mm")
    draw.text((sma_x + 40, sma_y), "SMA-F", fill="#222222", font=font_val, anchor="mm")
    draw.text((sma_x + 40, sma_y + 20), "50Ω Edge", fill="#666666", font=font_small, anchor="mm")
    draw.line([sma_x + 40, sma_y + 45, sma_x + 40, sma_y + 70], fill=WIRE_CLR, width=2)
    draw_gnd(sma_x + 40, sma_y + 70)

    # -------------------------------------------------------------
    # 5. BLOCK 3: AC MAINS VOLTAGE SAMPLING ONLY (ZMPT101B)
    # -------------------------------------------------------------
    b3_x1, b3_y1, b3_x2, b3_y2 = 2325, 75, W - inner_m - 15, 780
    draw_block_frame(b3_x1, b3_y1, b3_x2, b3_y2, "BLOCK 3: AC MAINS VOLTAGE SAMPLING ONLY (ZMPT101B - SENSE ONLY NOT POWER)")

    # Warning Notice
    draw.rectangle([b3_x1 + 25, b3_y1 + 45, b3_x2 - 25, b3_y1 + 80], fill="#FADBD8", outline="#C0392B", width=2)
    draw.text((b3_x1 + (b3_x2 - b3_x1) / 2, b3_y1 + 62),
              "TB2 IS STRICTLY VOLTAGE SENSE ONLY (SAMPLING GRID VOLTAGE). NO INTERNAL AC-DC POWER CONVERSION.",
              fill="#900C3F", font=font_val, anchor="mm")

    # TB2 Terminal Block
    tb2_x, tb2_y = 2380, 240
    draw.rectangle([tb2_x, tb2_y, tb2_x + 110, tb2_y + 150], fill="#FFFFFF", outline=SYM_BORDER, width=2)
    draw.text((tb2_x + 55, tb2_y + 22), "TB2", fill="#000088", font=font_ref, anchor="mm")
    draw.text((tb2_x + 55, tb2_y + 44), "5.08mm 2-Pin", fill="#555555", font=font_small, anchor="mm")
    draw.text((tb2_x + 25, tb2_y + 80), "1 (L)", fill="#B22222", font=font_pin, anchor="mm")
    draw.text((tb2_x + 25, tb2_y + 120), "2 (N)", fill="#000088", font=font_pin, anchor="mm")
    draw_net_label(tb2_x - 10, tb2_y + 80, "AC_L_IN", align="rm", bg="#FADBD8")
    draw_net_label(tb2_x - 10, tb2_y + 120, "AC_N_IN", align="rm", bg="#EBF5FB")

    # High Voltage Resistors
    draw.line([tb2_x + 110, tb2_y + 80, tb2_x + 160, tb2_y + 80], fill=WIRE_CLR, width=2)
    draw_resistor(tb2_x + 200, tb2_y + 80, "R_HV1", "41.2kΩ 1W", horiz=True)
    draw.line([tb2_x + 230, tb2_y + 80, tb2_x + 270, tb2_y + 80], fill=WIRE_CLR, width=2)
    draw_resistor(tb2_x + 310, tb2_y + 80, "R_HV2", "41.2kΩ 1W", horiz=True)

    # ZMPT101B Transformer Symbol
    t1_x, t1_y = 2800, 220
    draw.rectangle([t1_x, t1_y, t1_x + 170, t1_y + 170], fill=SYM_BODY, outline=SYM_BORDER, width=2)
    draw.text((t1_x + 85, t1_y + 22), "T1: ZMPT101B", fill="#000088", font=font_ref, anchor="mm")
    draw.text((t1_x + 85, t1_y + 44), "2mA:2mA Precision PT", fill="#555555", font=font_small, anchor="mm")
    draw.text((t1_x + 25, t1_y + 85), "PRI 1", fill=PIN_CLR, font=font_pin, anchor="lm")
    draw.text((t1_x + 25, t1_y + 130), "PRI 2", fill=PIN_CLR, font=font_pin, anchor="lm")
    draw.line([t1_x + 80, t1_y + 70, t1_x + 80, t1_y + 150], fill="#333333", width=2)
    draw.line([t1_x + 90, t1_y + 70, t1_x + 90, t1_y + 150], fill="#333333", width=2)
    draw.text((t1_x + 145, t1_y + 85), "SEC 1", fill=PIN_CLR, font=font_pin, anchor="rm")
    draw.text((t1_x + 145, t1_y + 130), "SEC 2", fill=PIN_CLR, font=font_pin, anchor="rm")

    draw.line([tb2_x + 340, tb2_y + 80, t1_x, t1_y + 85], fill=WIRE_CLR, width=2)
    draw.line([tb2_x + 110, tb2_y + 120, t1_x, t1_y + 130], fill=WIRE_CLR, width=2)

    # Secondary to Op-Amp Filter
    draw.line([t1_x + 170, t1_y + 85, t1_x + 230, t1_y + 85], fill=WIRE_CLR, width=2)
    draw.line([t1_x + 170, t1_y + 130, t1_x + 230, t1_y + 130], fill=WIRE_CLR, width=2)
    draw_gnd(t1_x + 230, t1_y + 130)

    # LM358 Conditioning Op-Amp
    u4_x, u4_y = 3120, 260
    draw.polygon([(u4_x, u4_y - 45), (u4_x + 75, u4_y), (u4_x, u4_y + 45)], fill=SYM_BODY, outline=SYM_BORDER)
    draw.text((u4_x + 15, u4_y - 18), "-", fill=PIN_CLR, font=font_ref, anchor="mm")
    draw.text((u4_x + 15, u4_y + 18), "+", fill=PIN_CLR, font=font_ref, anchor="mm")
    draw.text((u4_x + 38, u4_y), "U4\nLM358", fill="#000088", font=font_small, anchor="mm")

    draw.line([t1_x + 230, t1_y + 85, u4_x, u4_y + 18], fill=WIRE_CLR, width=2)
    draw_pwr(u4_x + 38, u4_y - 45, "+5V")
    draw_gnd(u4_x + 38, u4_y + 45)

    # Output to ADC_A1
    draw.line([u4_x + 75, u4_y, u4_x + 140, u4_y], fill=WIRE_CLR, width=2)
    draw_net_label(u4_x + 144, u4_y, "ADC_A1", align="lm")

    # -------------------------------------------------------------
    # 6. BLOCK 4: 5V DC USB-C POWER & AMS1117-3.3V LDO
    # -------------------------------------------------------------
    b4_x1, b4_y1, b4_x2, b4_y2 = inner_m + 15, 805, 1160, 1500
    draw_block_frame(b4_x1, b4_y1, b4_x2, b4_y2, "BLOCK 4: MAIN SYSTEM POWER: 5V DC USB-C & AMS1117-3.3V LDO REGULATOR")

    # USB Type-C Receptacle Box (placed with ample margin)
    usbc_x, usbc_y = b4_x1 + 60, 890
    usbc_w, usbc_h = 240, 360
    draw.rectangle([usbc_x, usbc_y, usbc_x + usbc_w, usbc_y + usbc_h], fill=SYM_BODY, outline=SYM_BORDER, width=2)
    draw.text((usbc_x + usbc_w / 2, usbc_y + 25), "J_USBC: USB Type-C", fill="#000088", font=font_sec_hdr, anchor="mm")
    draw.text((usbc_x + usbc_w / 2, usbc_y + 50), "16-Pin Power Receptacle", fill="#555555", font=font_small, anchor="mm")

    usbc_pins = [
        ("VBUS", "VBUS (Pins A4,A9,B4,B9)", 110),
        ("CC1", "CC1 (Pin A5)", 180),
        ("CC2", "CC2 (Pin B5)", 250),
        ("GND", "GND (Pins A1,A12,B1,B12)", 310),
    ]
    for pname, pdesc, py_rel in usbc_pins:
        py = usbc_y + py_rel
        draw.line([usbc_x + usbc_w, py, usbc_x + usbc_w + 30, py], fill=WIRE_CLR, width=2)
        draw.text((usbc_x + usbc_w - 10, py), pname, fill=PIN_CLR, font=font_pin, anchor="rm")
        draw.text((usbc_x + 12, py), pdesc, fill="#666666", font=font_small, anchor="lm")

    # VBUS Line
    vbus_y = usbc_y + 110
    draw.line([usbc_x + usbc_w + 30, vbus_y, usbc_x + usbc_w + 120, vbus_y], fill=POWER_CLR, width=3)
    draw_junction(usbc_x + usbc_w + 120, vbus_y)
    draw_pwr(usbc_x + usbc_w + 120, vbus_y, "+5V")

    # CC1 and CC2 Pull-Downs
    cc1_y = usbc_y + 180
    draw_resistor(usbc_x + usbc_w + 90, cc1_y, "R_CC1", "5.1kΩ", horiz=True)
    draw.line([usbc_x + usbc_w + 120, cc1_y, usbc_x + usbc_w + 150, cc1_y], fill=WIRE_CLR, width=2)
    draw_gnd(usbc_x + usbc_w + 150, cc1_y)

    cc2_y = usbc_y + 250
    draw_resistor(usbc_x + usbc_w + 90, cc2_y, "R_CC2", "5.1kΩ", horiz=True)
    draw.line([usbc_x + usbc_w + 120, cc2_y, usbc_x + usbc_w + 150, cc2_y], fill=WIRE_CLR, width=2)
    draw_gnd(usbc_x + usbc_w + 150, cc2_y)

    gnd_y = usbc_y + 310
    draw_gnd(usbc_x + usbc_w + 30, gnd_y)

    # AMS1117-3.3 LDO Circuit
    ldo_x, ldo_y = 660, 960
    ldo_w, ldo_h = 240, 220
    draw.rectangle([ldo_x, ldo_y, ldo_x + ldo_w, ldo_y + ldo_h], fill=SYM_BODY, outline=SYM_BORDER, width=2)
    draw.text((ldo_x + ldo_w / 2, ldo_y + 25), "U1: AMS1117-3.3", fill="#000088", font=font_sec_hdr, anchor="mm")
    draw.text((ldo_x + ldo_w / 2, ldo_y + 50), "1.0A Low-Dropout LDO", fill="#555555", font=font_small, anchor="mm")

    draw.text((ldo_x + 12, ldo_y + 110), "VIN [3]", fill=PIN_CLR, font=font_pin, anchor="lm")
    draw.text((ldo_x + ldo_w / 2, ldo_y + ldo_h - 15), "GND [1]", fill=PIN_CLR, font=font_pin, anchor="mm")
    draw.text((ldo_x + ldo_w - 12, ldo_y + 110), "VOUT [2]", fill=PIN_CLR, font=font_pin, anchor="rm")

    # LDO VIN wiring + C1
    draw_pwr(ldo_x - 110, ldo_y + 110, "+5V")
    draw.line([ldo_x - 110, ldo_y + 110, ldo_x, ldo_y + 110], fill=WIRE_CLR, width=2)
    draw_junction(ldo_x - 55, ldo_y + 110)
    draw_capacitor(ldo_x - 55, ldo_y + 160, "C1", "10µF", horiz=False, polarized=True)
    draw_gnd(ldo_x - 55, ldo_y + 190)

    # LDO GND wiring
    draw.line([ldo_x + ldo_w / 2, ldo_y + ldo_h, ldo_x + ldo_w / 2, ldo_y + ldo_h + 30], fill=WIRE_CLR, width=2)
    draw_gnd(ldo_x + ldo_w / 2, ldo_y + ldo_h + 30)

    # LDO VOUT wiring + C2
    draw.line([ldo_x + ldo_w, ldo_y + 110, ldo_x + ldo_w + 140, ldo_y + 110], fill=POWER_CLR, width=3)
    draw_junction(ldo_x + ldo_w + 60, ldo_y + 110)
    draw_capacitor(ldo_x + ldo_w + 60, ldo_y + 160, "C2", "22µF", horiz=False, polarized=True)
    draw_gnd(ldo_x + ldo_w + 60, ldo_y + 190)

    draw_pwr(ldo_x + ldo_w + 140, ldo_y + 110, "+3V3_LORA")

    # -------------------------------------------------------------
    # 7. BLOCK 5: TI ADS1115 16-BIT 4-CH I2C ADC & EXPANSION
    # -------------------------------------------------------------
    b5_x1, b5_y1, b5_x2, b5_y2 = 1185, 805, 2300, 1500
    draw_block_frame(b5_x1, b5_y1, b5_x2, b5_y2, "BLOCK 5: TI ADS1115 16-BIT 4-CHANNEL I2C ADC & ANALOG EXPANSION")

    ads_x, ads_y = 1420, 930
    ads_w, ads_h = 390, 480
    draw.rectangle([ads_x, ads_y, ads_x + ads_w, ads_y + ads_h], fill=SYM_BODY, outline=SYM_BORDER, width=2)
    draw.text((ads_x + ads_w / 2, ads_y + 25), "U2: ADS1115IDGSR", fill="#000088", font=font_sec_hdr, anchor="mm")
    draw.text((ads_x + ads_w / 2, ads_y + 50), "16-Bit Ultra-Compact Precision I2C ADC", fill="#555555", font=font_small, anchor="mm")

    ads_left = [
        ("ADDR (-> 0x48)", 110, "GND"),
        ("ALERT / RDY", 170, "NC"),
        ("GND", 230, "GND"),
        ("VDD (+3.3V)", 290, "+3V3_RPI"),
        ("SDA (I2C)", 360, "I2C_SDA"),
        ("SCL (I2C)", 420, "I2C_SCL"),
    ]
    for pname, py_rel, net in ads_left:
        py = ads_y + py_rel
        draw.line([ads_x - 30, py, ads_x, py], fill=WIRE_CLR, width=2)
        draw.text((ads_x + 12, py), pname, fill=PIN_CLR, font=font_pin, anchor="lm")
        if net == "GND":
            draw_gnd(ads_x - 30, py)
        elif net == "+3V3_RPI":
            draw_pwr(ads_x - 30, py, "+3V3_RPI")
        elif net == "NC":
            pass
        else:
            draw_net_label(ads_x - 34, py, net, align="rm")

    ads_right = [
        ("AIN0: Motor Current", 130, "ADC_A0"),
        ("AIN1: Grid Voltage", 210, "ADC_A1"),
        ("AIN2: Aux Expansion", 290, "ADC_A2"),
        ("AIN3: Aux Expansion", 370, "ADC_A3"),
    ]
    for pname, py_rel, net in ads_right:
        py = ads_y + py_rel
        draw.line([ads_x + ads_w, py, ads_x + ads_w + 30, py], fill=WIRE_CLR, width=2)
        draw.text((ads_x + ads_w - 12, py), pname, fill=PIN_CLR, font=font_pin, anchor="rm")
        draw_net_label(ads_x + ads_w + 34, py, net, align="lm")

    # Decoupling Cap for ADS1115
    draw_pwr(1230, 950, "+3V3_RPI")
    draw.line([1230, 950, 1230, 1030], fill=WIRE_CLR, width=2)
    draw_capacitor(1230, 1060, "C_ADS", "0.1µF", horiz=False)
    draw_gnd(1230, 1100)

    # I2C Pull-Up Resistors (spaced 90px apart with clear branch wires)
    pu_x = 1260
    draw_pwr(pu_x, 1160, "+3V3_RPI")
    draw_resistor(pu_x, 1220, "R_PU1", "4.7kΩ", horiz=False)
    draw.line([pu_x, 1250, pu_x + 60, 1250], fill=WIRE_CLR, width=2)
    draw.line([pu_x + 60, 1250, pu_x + 60, ads_y + 360], fill=WIRE_CLR, width=2)
    draw.line([pu_x + 60, ads_y + 360, ads_x - 30, ads_y + 360], fill=WIRE_CLR, width=2)
    draw_junction(ads_x - 30, ads_y + 360)

    draw_pwr(pu_x + 90, 1160, "+3V3_RPI")
    draw_resistor(pu_x + 90, 1220, "R_PU2", "4.7kΩ", horiz=False)
    draw.line([pu_x + 90, 1250, pu_x + 110, 1250], fill=WIRE_CLR, width=2)
    draw.line([pu_x + 110, 1250, pu_x + 110, ads_y + 420], fill=WIRE_CLR, width=2)
    draw.line([pu_x + 110, ads_y + 420, ads_x - 30, ads_y + 420], fill=WIRE_CLR, width=2)
    draw_junction(ads_x - 30, ads_y + 420)

    # TB_EXP Expansion Connector Box
    exp_x, exp_y = 2050, 1160
    draw.rectangle([exp_x, exp_y, exp_x + 170, exp_y + 140], fill="#FFFFFF", outline=SYM_BORDER, width=2)
    draw.text((exp_x + 85, exp_y + 22), "TB_EXP", fill="#000088", font=font_ref, anchor="mm")
    draw.text((exp_x + 85, exp_y + 44), "5.08mm 2-Pin Screw", fill="#555555", font=font_small, anchor="mm")
    draw.text((exp_x + 35, exp_y + 80), "Pin 1", fill=PIN_CLR, font=font_pin, anchor="lm")
    draw.text((exp_x + 35, exp_y + 115), "Pin 2", fill=PIN_CLR, font=font_pin, anchor="lm")
    draw_net_label(exp_x - 15, exp_y + 80, "ADC_A2", align="rm")
    draw_net_label(exp_x - 15, exp_y + 115, "ADC_A3", align="rm")
    draw.line([exp_x - 15, exp_y + 80, exp_x, exp_y + 80], fill=WIRE_CLR, width=2)
    draw.line([exp_x - 15, exp_y + 115, exp_x, exp_y + 115], fill=WIRE_CLR, width=2)

    # -------------------------------------------------------------
    # 8. BLOCK 6: CURRENT SENSING (ACS712 & 3.5mm CT CLAMP)
    # -------------------------------------------------------------
    b6_x1, b6_y1, b6_x2, b6_y2 = 2325, 805, W - inner_m - 15, 1500
    draw_block_frame(b6_x1, b6_y1, b6_x2, b6_y2, "BLOCK 6: PUMP MOTOR CURRENT SENSING (ACS712-30A & 3.5mm CT CLAMP)")

    # 3.5mm CT Clamp Jack (J_CT) & Bias Network
    ct_x, ct_y = 2360, 930
    draw.rectangle([ct_x, ct_y, ct_x + 140, ct_y + 130], fill="#FFFFFF", outline=SYM_BORDER, width=2)
    draw.text((ct_x + 70, ct_y + 22), "J_CT: 3.5mm Jack", fill="#000088", font=font_ref, anchor="mm")
    draw.text((ct_x + 70, ct_y + 44), "SCT-013-000 Input", fill="#555555", font=font_small, anchor="mm")
    draw.text((ct_x + 25, ct_y + 75), "Tip", fill=PIN_CLR, font=font_pin, anchor="lm")
    draw.text((ct_x + 25, ct_y + 105), "Sleeve", fill=PIN_CLR, font=font_pin, anchor="lm")

    # Burden resistor across CT clamp
    draw.line([ct_x + 140, ct_y + 75, ct_x + 210, ct_y + 75], fill=WIRE_CLR, width=2)
    draw.line([ct_x + 140, ct_y + 105, ct_x + 210, ct_y + 105], fill=WIRE_CLR, width=2)
    draw_resistor(ct_x + 210, ct_y + 90, "R_BURDEN", "33Ω 1%", horiz=False)

    # DC Bias Network
    bias_x = ct_x + 320
    draw_pwr(bias_x, ct_y + 20, "+3V3_RPI")
    draw_resistor(bias_x, ct_y + 60, "R_BIAS1", "10kΩ", horiz=False)
    draw.line([bias_x, ct_y + 90, ct_x + 210, ct_y + 105], fill=WIRE_CLR, width=2)
    draw_resistor(bias_x, ct_y + 120, "R_BIAS2", "10kΩ", horiz=False)
    draw_gnd(bias_x, ct_y + 150)
    draw_capacitor(bias_x + 50, ct_y + 90, "C_BIAS", "10µF", horiz=False, polarized=True)
    draw_gnd(bias_x + 50, ct_y + 130)

    # ACS712T-30A Hall-Effect Sensor
    acs_x, acs_y = 2860, 960
    acs_w, acs_h = 320, 420
    draw.rectangle([acs_x, acs_y, acs_x + acs_w, acs_y + acs_h], fill=SYM_BODY, outline=SYM_BORDER, width=2)
    draw.text((acs_x + acs_w / 2, acs_y + 25), "U3: ACS712T-30A", fill="#000088", font=font_sec_hdr, anchor="mm")
    draw.text((acs_x + acs_w / 2, acs_y + 50), "Fully-Isolated Current Sensor", fill="#555555", font=font_small, anchor="mm")

    draw.text((acs_x + 15, acs_y + 140), "IP+ [1,2]", fill=PIN_CLR, font=font_pin, anchor="lm")
    draw.text((acs_x + 15, acs_y + 240), "IP- [3,4]", fill=PIN_CLR, font=font_pin, anchor="lm")
    draw_net_label(acs_x - 10, acs_y + 140, "AC_L_IN", align="rm", bg="#FADBD8")
    draw_net_label(acs_x - 10, acs_y + 240, "AC_L_PUMP", align="rm", bg="#FADBD8")
    draw.line([acs_x - 10, acs_y + 140, acs_x, acs_y + 140], fill=WIRE_CLR, width=3)
    draw.line([acs_x - 10, acs_y + 240, acs_x, acs_y + 240], fill=WIRE_CLR, width=3)

    acs_sec = [
        ("VCC [Pin 8]", 120, "+5V"),
        ("VOUT [Pin 7]", 190, "ADC_A0"),
        ("FILTER [Pin 6]", 260, "FILTER"),
        ("GND [Pin 5]", 330, "GND"),
    ]
    for pname, py_rel, net in acs_sec:
        py = acs_y + py_rel
        draw.line([acs_x + acs_w, py, acs_x + acs_w + 30, py], fill=WIRE_CLR, width=2)
        draw.text((acs_x + acs_w - 12, py), pname, fill=PIN_CLR, font=font_pin, anchor="rm")
        if net == "+5V":
            draw_pwr(acs_x + acs_w + 30, py, "+5V")
        elif net == "GND":
            draw_gnd(acs_x + acs_w + 30, py)
        elif net == "ADC_A0":
            draw_net_label(acs_x + acs_w + 34, py, "ADC_A0", align="lm")
        elif net == "FILTER":
            draw_capacitor(acs_x + acs_w + 80, py, "C_F", "4.7nF", horiz=False)
            draw_gnd(acs_x + acs_w + 80, py + 30)

    # -------------------------------------------------------------
    # 9. BLOCK 7: DUAL 10A RELAYS, OPTOCOUPLERS & SNUBBER
    # -------------------------------------------------------------
    b7_x1, b7_y1, b7_x2, b7_y2 = inner_m + 15, 1525, W - inner_m - 15, 2180
    draw_block_frame(b7_x1, b7_y1, b7_x2, b7_y2, "BLOCK 7: DUAL 10A 250VAC RELAYS, OPTOCOUPLERS & SNUBBER TRANSIENT PROTECTION")

    def draw_relay_channel(ch_num: int, name: str, ctrl_net: str, load_net: str, base_x: float, base_y: float) -> None:
        draw_net_label(base_x - 30, base_y + 40, ctrl_net, align="rm")
        draw.line([base_x - 30, base_y + 40, base_x + 10, base_y + 40], fill=WIRE_CLR, width=2)
        draw_resistor(base_x + 40, base_y + 40, f"R_OPT{ch_num}", "470Ω", horiz=True)
        draw.line([base_x + 70, base_y + 40, base_x + 100, base_y + 40], fill=WIRE_CLR, width=2)

        opto_x, opto_y = base_x + 100, base_y
        draw.rectangle([opto_x, opto_y, opto_x + 140, opto_y + 110], fill=SYM_BODY, outline=SYM_BORDER, width=2)
        draw.text((opto_x + 70, opto_y + 18), f"U{ch_num + 4}: PC817", fill="#000088", font=font_ref, anchor="mm")
        draw.text((opto_x + 70, opto_y + 36), "Optocoupler", fill="#555555", font=font_small, anchor="mm")
        draw.text((opto_x + 15, opto_y + 65), "Anode", fill=PIN_CLR, font=font_small, anchor="lm")
        draw.text((opto_x + 15, opto_y + 92), "Cathode", fill=PIN_CLR, font=font_small, anchor="lm")
        draw.text((opto_x + 125, opto_y + 65), "Col", fill=PIN_CLR, font=font_small, anchor="rm")
        draw.text((opto_x + 125, opto_y + 92), "Emit", fill=PIN_CLR, font=font_small, anchor="rm")

        draw.line([opto_x - 10, opto_y + 92, opto_x, opto_y + 92], fill=WIRE_CLR, width=2)
        draw_gnd(opto_x - 10, opto_y + 92)

        draw_pwr(opto_x + 160, opto_y + 65, "+5V")
        draw.line([opto_x + 140, opto_y + 65, opto_x + 160, opto_y + 65], fill=WIRE_CLR, width=2)

        draw.line([opto_x + 140, opto_y + 92, opto_x + 180, opto_y + 92], fill=WIRE_CLR, width=2)
        draw_resistor(opto_x + 210, opto_y + 92, f"R_DRV{ch_num}", "1kΩ", horiz=True)
        draw.line([opto_x + 240, opto_y + 92, opto_x + 280, opto_y + 92], fill=WIRE_CLR, width=2)

        # MMBT3904 NPN Transistor
        q_x, q_y = opto_x + 280, opto_y + 92
        draw_transistor_npn(q_x, q_y, f"Q{ch_num}", "MMBT3904")
        draw_resistor(q_x - 50, q_y + 45, f"R_PD{ch_num}", "10kΩ", horiz=False)
        draw_gnd(q_x - 50, q_y + 80)
        draw_gnd(q_x + 12, q_y + 32)

        # Relay Coil & Flyback Diode (Songle SRD-05VDC-SL-C)
        relay_x, relay_y = q_x + 230, opto_y - 20
        draw.rectangle([relay_x, relay_y, relay_x + 240, relay_y + 170], fill=SYM_BODY, outline=SYM_BORDER, width=2)
        draw.text((relay_x + 120, relay_y + 22), f"K{ch_num}: SONGLE", fill="#000088", font=font_sec_hdr, anchor="mm")
        draw.text((relay_x + 120, relay_y + 46), f"{name} (10A 250VAC)", fill="#555555", font=font_val, anchor="mm")

        # Coil pins
        draw.text((relay_x + 20, relay_y + 85), "Coil (+)", fill=PIN_CLR, font=font_pin, anchor="lm")
        draw.text((relay_x + 20, relay_y + 130), "Coil (-)", fill=PIN_CLR, font=font_pin, anchor="lm")
        draw_pwr(relay_x - 70, relay_y + 85, "+5V")
        draw.line([relay_x - 70, relay_y + 85, relay_x, relay_y + 85], fill=WIRE_CLR, width=2)

        # Orthogonal wire from Q collector to Coil (-)
        draw.line([q_x + 12, q_y - 32, q_x + 12, relay_y + 130], fill=WIRE_CLR, width=2)
        draw.line([q_x + 12, relay_y + 130, relay_x, relay_y + 130], fill=WIRE_CLR, width=2)

        # Flyback Diode across coil (placed vertically between +5V and Coil -)
        diode_x = relay_x - 35
        draw.line([diode_x, relay_y + 85, diode_x, relay_y + 92], fill=WIRE_CLR, width=2)
        draw_junction(diode_x, relay_y + 85)
        draw_diode(diode_x, relay_y + 107, f"D{ch_num + 1}", "1N4007", direction="up")
        draw.line([diode_x, relay_y + 122, diode_x, relay_y + 130], fill=WIRE_CLR, width=2)
        draw_junction(diode_x, relay_y + 130)

        # Contact Pins: COM, NO
        draw.text((relay_x + 220, relay_y + 75), "COM", fill=PIN_CLR, font=font_pin, anchor="rm")
        draw.text((relay_x + 220, relay_y + 125), "NO", fill=PIN_CLR, font=font_pin, anchor="rm")
        draw_net_label(relay_x + 240, relay_y + 75, "AC_L_PUMP", align="lm", bg="#FADBD8")
        draw_net_label(relay_x + 240, relay_y + 125, load_net, align="lm", bg="#FADBD8")

    # Draw Relay 1 (Wilo Pump)
    draw_relay_channel(1, "WILO PUMP RELAY", "RELAY1_CTRL", "AC_PUMP_OUT", 220, 1720)

    # Draw Relay 2 (Aux / Valve)
    draw_relay_channel(2, "AUX / VALVE RELAY", "RELAY2_CTRL", "AC_VALVE_OUT", 1250, 1720)

    # Protection & Snubber Section (MOV, Snubber, TB3)
    prot_x, prot_y = 2280, 1660
    draw.rectangle([prot_x, prot_y, prot_x + 480, prot_y + 360], fill="#FAFAFA", outline=SYM_BORDER, width=2)
    draw.text((prot_x + 240, prot_y + 25), "TRANSIENT & SNUBBER NETWORK", fill="#000088", font=font_sec_hdr, anchor="mm")

    # MOV1 Varistor (14D471K)
    draw_net_label(prot_x + 80, prot_y + 80, "AC_L_PUMP", align="rm", bg="#FADBD8")
    draw_resistor(prot_x + 130, prot_y + 140, "MOV1", "14D471K (470V)", horiz=False)
    draw_net_label(prot_x + 80, prot_y + 200, "AC_N_IN", align="rm", bg="#EBF5FB")
    draw.line([prot_x + 80, prot_y + 80, prot_x + 130, prot_y + 110], fill=WIRE_CLR, width=2)
    draw.line([prot_x + 80, prot_y + 200, prot_x + 130, prot_y + 170], fill=WIRE_CLR, width=2)

    # RC Snubber (100Ω 1W + 0.1µF 275VAC X2)
    draw_resistor(prot_x + 280, prot_y + 110, "R_SNUB1", "100Ω 1W", horiz=False)
    draw_capacitor(prot_x + 280, prot_y + 170, "C_SNUB1", "0.1µF 275V X2", horiz=False)
    draw.line([prot_x + 180, prot_y + 80, prot_x + 280, prot_y + 80], fill=WIRE_CLR, width=2)
    draw.line([prot_x + 180, prot_y + 200, prot_x + 280, prot_y + 200], fill=WIRE_CLR, width=2)

    # TB3 3-Pin High Current Screw Terminal Block
    tb3_x, tb3_y = 2860, 1720
    draw.rectangle([tb3_x, tb3_y, tb3_x + 240, tb3_y + 260], fill="#FFFFFF", outline=SYM_BORDER, width=3)
    draw.text((tb3_x + 120, tb3_y + 28), "TB3: LOAD OUT", fill="#B22222", font=font_sec_hdr, anchor="mm")
    draw.text((tb3_x + 120, tb3_y + 55), "10A 250VAC Screw Terminal", fill="#555555", font=font_small, anchor="mm")

    tb3_pins = [
        ("Pin 1: PUMP", 110, "AC_PUMP_OUT"),
        ("Pin 2: VALVE", 170, "AC_VALVE_OUT"),
        ("Pin 3: NEUT", 230, "AC_N_IN"),
    ]
    for pname, py_rel, net in tb3_pins:
        py = tb3_y + py_rel
        draw.line([tb3_x - 30, py, tb3_x, py], fill=WIRE_CLR, width=3)
        draw.text((tb3_x + 20, py), pname, fill=PIN_CLR, font=font_sec_hdr, anchor="lm")
        draw_net_label(tb3_x - 35, py, net, align="rm", bg="#FADBD8" if "OUT" in net else "#EBF5FB")

    # Save PNG
    png_output.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(png_output), format="PNG", dpi=(200, 200))
    print(f"Generated clean schematic PNG: {png_output}")


if __name__ == "__main__":
    out_png = Path("output/wilo_receiver/wilo_receiver_schematic.png")
    create_schematic_diagram(out_png)
