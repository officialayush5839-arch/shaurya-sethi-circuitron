"""Generate a high-resolution, photorealistic 2D composite rendering of the Wilo Receiver PCB."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path


def render_board_png(output_png: Path) -> None:
    # Board dimensions in mm
    # Origin: (50.0, 50.0), Width: 120.0, Height: 85.0
    x0, y0 = 50.0, 50.0
    w, h = 120.0, 85.0

    fig, ax = plt.subplots(figsize=(16, 11.3), dpi=200)
    fig.patch.set_facecolor('#111315')
    ax.set_facecolor('#111315')

    # Draw dark green FR4 PCB substrate with soldermask
    pcb_rect = patches.FancyBboxPatch(
        (x0, y0), w, h,
        boxstyle="round,pad=0,rounding_size=3.0",
        facecolor="#1A472A",
        edgecolor="#2D6A4F",
        linewidth=3.0,
        zorder=1
    )
    ax.add_patch(pcb_rect)

    # High-Voltage Isolation Milling Slots (Edge.Cuts)
    slot_x = x0 + 67.0
    for sy_start, sy_end in [(y0 + 8.0, y0 + 40.0), (y0 + 66.0, y0 + 78.0)]:
        slot = patches.Rectangle(
            (slot_x - 0.8, sy_start), 1.6, sy_end - sy_start,
            facecolor="#111315", edgecolor="#E63946", linewidth=1.5,
            linestyle="--", zorder=2
        )
        ax.add_patch(slot)

    # Silkscreen Zone Dividers and Text
    ax.text(x0 + 32.0, y0 + 4.0, "ZONE 1: LOW-VOLTAGE DC LOGIC (5V USB-C MAIN POWER)", color="#F1FAEE", fontsize=12, fontweight='bold', ha='center', va='center', zorder=3)
    ax.text(x0 + 94.0, y0 + 4.0, "ZONE 2: 230V AC SENSE & SWITCHING", color="#E63946", fontsize=12, fontweight='bold', ha='center', va='center', zorder=3)
    ax.text(slot_x - 1.8, y0 + 24.0, "ISOLATION BARRIER (5mm CREEPAGE)", color="#FFD166", fontsize=10, fontweight='bold', rotation=90, ha='center', va='center', zorder=3)

    # Mounting Holes (M2.5 for Raspberry Pi Zero)
    hole_coords = [(x0 + 4.0, y0 + 4.0), (x0 + 62.0, y0 + 4.0), (x0 + 4.0, y0 + 27.0), (x0 + 62.0, y0 + 27.0)]
    for hx, hy in hole_coords:
        ax.add_patch(plt.Circle((hx, hy), 2.2, facecolor="#C0C0C0", edgecolor="#888888", linewidth=1.0, zorder=2))
        ax.add_patch(plt.Circle((hx, hy), 1.35, facecolor="#111315", edgecolor="#333333", linewidth=1.5, zorder=3))
        ax.text(hx, hy - 3.2, "M2.5", color="#A8DADC", fontsize=7, ha='center', zorder=4)

    # 1. J1: Raspberry Pi Zero 40-Pin GPIO Header
    j1_x, j1_y = x0 + 8.5, y0 + 10.5
    ax.add_patch(patches.Rectangle((j1_x - 2.5, j1_y - 2.5), 50.8, 5.0, facecolor="#212529", edgecolor="#FFB703", linewidth=1.5, zorder=4))
    for col in range(20):
        for row in range(2):
            px = j1_x + col * 2.54
            py = j1_y + row * 2.54
            ax.add_patch(plt.Circle((px, py), 0.75, facecolor="#FFD166", edgecolor="#B7950B", linewidth=0.5, zorder=5))
            ax.add_patch(plt.Circle((px, py), 0.45, facecolor="#111315", zorder=6))
    ax.text(j1_x + 24.0, j1_y - 4.2, "J1: Raspberry Pi Zero 2W 40-Pin Header", color="#FFD166", fontsize=9, fontweight='bold', ha='center', zorder=7)

    # 2. SCT-013 CT Clamp Interface (J_CT, 33-ohm burden, DC Bias)
    jct_x, jct_y = x0 + 6.0, y0 + 26.0
    ax.add_patch(patches.Rectangle((jct_x - 4.5, jct_y - 4.0), 9.0, 8.0, facecolor="#212529", edgecolor="#78909C", linewidth=1.2, zorder=4))
    ax.add_patch(plt.Circle((jct_x, jct_y), 2.0, facecolor="#37474F", edgecolor="#90A4AE", linewidth=1.0, zorder=5))
    ax.add_patch(plt.Circle((jct_x, jct_y), 1.0, facecolor="#111315", zorder=6))
    ax.text(jct_x + 6.0, jct_y, "J_CT: 3.5mm\nCT Clamp", color="#90CAF9", fontsize=8, fontweight='bold', va='center', zorder=7)

    # Burden & Bias Resistors
    ax.add_patch(patches.Rectangle((x0 + 16.0 - 1.0, y0 + 24.0 - 0.6), 2.0, 1.2, facecolor="#333333", edgecolor="#888888", linewidth=0.8, zorder=4))
    ax.text(x0 + 16.0, y0 + 24.0 - 1.5, "R_BURDEN\n33Ω", color="#CCCCCC", fontsize=6, ha='center', zorder=5)

    for rb_ref, rby in [("R_BIAS1", y0 + 22.0), ("R_BIAS2", y0 + 26.0)]:
        ax.add_patch(patches.Rectangle((x0 + 22.0 - 1.0, rby - 0.6), 2.0, 1.2, facecolor="#333333", edgecolor="#888888", linewidth=0.8, zorder=4))
        ax.text(x0 + 22.0, rby - 1.4, f"{rb_ref}\n10k", color="#CCCCCC", fontsize=6, ha='center', zorder=5)

    # 3. SX1278 Ra-02 LoRa Module & SMA Connector
    lora_x, lora_y = x0 + 20.0, y0 + 42.0
    ax.add_patch(patches.Rectangle((lora_x - 8.0, lora_y - 8.0), 16.0, 16.0, facecolor="#263238", edgecolor="#78909C", linewidth=1.5, zorder=4))
    ax.add_patch(patches.Rectangle((lora_x - 6.5, lora_y - 6.0), 13.0, 11.0, facecolor="#90A4AE", edgecolor="#B0BEC5", linewidth=1.0, zorder=5))
    ax.text(lora_x, lora_y - 1.0, "Ai-Thinker\nRa-02", color="#212121", fontsize=8, fontweight='bold', ha='center', va='center', zorder=6)
    ax.text(lora_x, lora_y + 3.5, "433MHz LoRa", color="#37474F", fontsize=7, ha='center', va='center', zorder=6)
    ax.text(lora_x, lora_y - 9.5, "U_LORA: SX1278", color="#F1FAEE", fontsize=9, fontweight='bold', ha='center', zorder=7)

    # LoRa Filtering Capacitors (10uF + 0.1uF)
    for cl_ref, cl_val, clx in [("C_LORA1", "10uF", x0 + 15.0), ("C_LORA2", "0.1uF", x0 + 21.0)]:
        ax.add_patch(patches.Rectangle((clx - 1.0, y0 + 33.0 - 0.6), 2.0, 1.2, facecolor="#C49A45", edgecolor="#B7950B", linewidth=0.8, zorder=4))
        ax.text(clx, y0 + 33.0 - 1.6, f"{cl_ref}\n{cl_val}", color="#D4AF37", fontsize=6, ha='center', zorder=5)

    # Castellated pads on LoRa module
    for i in range(8):
        ax.add_patch(patches.Rectangle((lora_x - 8.2, lora_y - 7.0 + i * 2.0), 1.4, 1.0, facecolor="#FFD166", edgecolor="#B7950B", linewidth=0.5, zorder=6))
        ax.add_patch(patches.Rectangle((lora_x + 6.8, lora_y - 7.0 + i * 2.0), 1.4, 1.0, facecolor="#FFD166", edgecolor="#B7950B", linewidth=0.5, zorder=6))

    # SMA Connector (J_SMA) on board edge
    sma_x, sma_y = x0 + 4.0, y0 + 42.0
    ax.add_patch(patches.Rectangle((sma_x - 3.5, sma_y - 3.5), 7.0, 7.0, facecolor="#B45309", edgecolor="#F59E0B", linewidth=1.5, zorder=4))
    ax.add_patch(plt.Circle((sma_x, sma_y), 2.5, facecolor="#F59E0B", edgecolor="#D97706", linewidth=1.0, zorder=5))
    ax.add_patch(plt.Circle((sma_x, sma_y), 0.8, facecolor="#FFD166", zorder=6))
    ax.text(sma_x + 1.5, sma_y + 5.5, "J_SMA\n50Ω Ant", color="#F59E0B", fontsize=8, fontweight='bold', ha='center', zorder=7)

    # 4. ADS1115 16-Bit I2C ADC (U2), Decoupling (C_ADS) & Expansion Terminal (TB_EXP)
    adc_x, adc_y = x0 + 48.0, y0 + 36.0
    ax.add_patch(patches.Rectangle((adc_x - 2.5, adc_y - 2.0), 5.0, 4.0, facecolor="#111111", edgecolor="#616161", linewidth=1.2, zorder=4))
    ax.add_patch(plt.Circle((adc_x - 1.8, adc_y - 1.2), 0.35, facecolor="#FFFFFF", zorder=5))
    ax.text(adc_x, adc_y, "ADS1115", color="#E0E0E0", fontsize=7, fontweight='bold', ha='center', va='center', zorder=6)
    ax.text(adc_x, adc_y - 3.5, "U2: 16-Bit ADC", color="#A8DADC", fontsize=8, fontweight='bold', ha='center', zorder=7)

    # C_ADS decoupling
    ax.add_patch(patches.Rectangle((x0 + 54.0 - 0.8, adc_y - 0.6), 1.6, 1.2, facecolor="#C49A45", edgecolor="#B7950B", linewidth=0.8, zorder=4))
    ax.text(x0 + 54.0, adc_y + 2.0, "C_ADS\n100nF", color="#D4AF37", fontsize=6, ha='center', zorder=5)

    # TB_EXP Screw Terminal (A2, A3)
    tbexp_x, tbexp_y = x0 + 54.0, y0 + 19.0
    ax.add_patch(patches.Rectangle((tbexp_x - 4.5, tbexp_y - 3.5), 9.0, 7.0, facecolor="#2E7D32", edgecolor="#4CAF50", linewidth=1.2, zorder=4))
    for dx in [-2.54, 2.54]:
        ax.add_patch(plt.Circle((tbexp_x + dx, tbexp_y), 1.4, facecolor="#E0E0E0", edgecolor="#757575", linewidth=0.8, zorder=5))
    ax.text(tbexp_x, tbexp_y - 4.5, "TB_EXP: A2/A3", color="#81C784", fontsize=7, fontweight='bold', ha='center', zorder=6)

    # I2C Pull-up resistors
    for r_ref, rx in [("R_PU1", x0 + 30.0), ("R_PU2", x0 + 36.0)]:
        ax.add_patch(patches.Rectangle((rx - 1.0, y0 + 19.0 - 0.6), 2.0, 1.2, facecolor="#333333", edgecolor="#888888", linewidth=0.8, zorder=4))
        ax.text(rx, y0 + 19.0 - 1.8, f"{r_ref}\n4.7k", color="#CCCCCC", fontsize=6, ha='center', zorder=5)

    # 5. Power Supply: J_USBC (USB Type-C 5V DC Main Power), U1 (AMS1117-3.3)
    usbc_x, usbc_y = x0 + 5.5, y0 + 68.0
    ax.add_patch(patches.Rectangle((usbc_x - 4.5, usbc_y - 4.5), 9.0, 9.0, facecolor="#455A64", edgecolor="#90A4AE", linewidth=1.5, zorder=4))
    ax.add_patch(patches.FancyBboxPatch((usbc_x - 3.5, usbc_y - 1.8), 7.0, 3.6, boxstyle="round,pad=0,rounding_size=1.5", facecolor="#263238", edgecolor="#B0BEC5", linewidth=1.0, zorder=5))
    ax.text(usbc_x + 6.0, usbc_y, "J_USBC:\n5V USB-C IN\n(MAIN POWER)", color="#90CAF9", fontsize=8, fontweight='bold', va='center', zorder=7)

    # CC Resistors R_CC1, R_CC2
    for rcc_ref, rcc_y in [("R_CC1", y0 + 64.0), ("R_CC2", y0 + 72.0)]:
        ax.add_patch(patches.Rectangle((x0 + 12.0 - 0.8, rcc_y - 0.5), 1.6, 1.0, facecolor="#333333", edgecolor="#888888", linewidth=0.6, zorder=4))
        ax.text(x0 + 12.0, rcc_y - 1.2, f"{rcc_ref}: 5.1k", color="#B0BEC5", fontsize=5.5, ha='center', zorder=5)

    # AMS1117-3.3 LDO (U1)
    u1_x, u1_y = x0 + 24.0, y0 + 68.0
    ax.add_patch(patches.Rectangle((u1_x - 3.5, u1_y - 2.5), 7.0, 5.0, facecolor="#1E1E1E", edgecolor="#757575", linewidth=1.2, zorder=4))
    ax.add_patch(patches.Rectangle((u1_x - 2.5, u1_y + 2.5), 5.0, 1.5, facecolor="#C0C0C0", edgecolor="#9E9E9E", linewidth=0.8, zorder=4))
    ax.text(u1_x, u1_y, "AMS1117\n3.3V", color="#ECEFF1", fontsize=7, fontweight='bold', ha='center', va='center', zorder=5)
    ax.text(u1_x, u1_y - 4.5, "U1: 3.3V LDO", color="#81C784", fontsize=8, fontweight='bold', ha='center', zorder=6)

    # Filter Capacitors C1 (10uF) and C2 (22uF)
    for c_ref, c_val, cx in [("C1", "10uF", x0 + 18.0), ("C2", "22uF", x0 + 31.0)]:
        ax.add_patch(patches.Rectangle((cx - 1.0, y0 + 68.0 - 0.6), 2.0, 1.2, facecolor="#C49A45", edgecolor="#B7950B", linewidth=0.8, zorder=4))
        ax.text(cx, y0 + 68.0 + 2.5, f"{c_ref}\n{c_val}", color="#D4AF37", fontsize=7, ha='center', zorder=5)

    # 6. User Controls: Push Buttons (SW1, SW2) & Status LEDs with Series Resistors
    # R_LED2 & R_LED3 current limiting
    ax.add_patch(patches.Rectangle((x0 + 12.0 - 0.8, y0 + 52.0 - 0.5), 1.6, 1.0, facecolor="#333333", edgecolor="#888888", linewidth=0.6, zorder=4))
    ax.text(x0 + 12.0, y0 + 52.0 - 1.2, "R_LED2\n470Ω", color="#B0BEC5", fontsize=5.5, ha='center', zorder=5)

    ax.add_patch(patches.Rectangle((x0 + 20.0 - 0.8, y0 + 52.0 - 0.5), 1.6, 1.0, facecolor="#333333", edgecolor="#888888", linewidth=0.6, zorder=4))
    ax.text(x0 + 20.0, y0 + 52.0 - 1.2, "R_LED3\n330Ω", color="#B0BEC5", fontsize=5.5, ha='center', zorder=5)

    leds = [
        ("LED_5V", "5V PWR", x0 + 12.0, "#22C55E"),
        ("LED_3V3", "3V3 RF", x0 + 20.0, "#3B82F6"),
        ("LED_PUMP", "PUMP ON", x0 + 36.0, "#EAB308"),
    ]
    for l_ref, l_lbl, lx, col in leds:
        ax.add_patch(patches.Rectangle((lx - 1.2, y0 + 56.0 - 0.8), 2.4, 1.6, facecolor=col, edgecolor="#FFFFFF", linewidth=1.0, zorder=4))
        ax.text(lx, y0 + 56.0 - 2.5, f"{l_ref}\n{l_lbl}", color=col, fontsize=7, fontweight='bold', ha='center', zorder=5)

    # R_LED1 330-ohm series resistor
    ax.add_patch(patches.Rectangle((x0 + 28.0 - 1.0, y0 + 56.0 - 0.6), 2.0, 1.2, facecolor="#333333", edgecolor="#888888", linewidth=0.8, zorder=4))
    ax.text(x0 + 28.0, y0 + 56.0 - 1.8, "R_LED1\n330Ω", color="#CCCCCC", fontsize=6, ha='center', zorder=5)

    # Push Buttons SW1 (Force ON) and SW2 (Force OFF)
    buttons = [
        ("SW1", "FORCE ON", x0 + 42.0, "#2E7D32"),
        ("SW2", "FORCE OFF", x0 + 56.0, "#C62828"),
    ]
    for b_ref, b_lbl, bx, b_col in buttons:
        ax.add_patch(patches.Rectangle((bx - 3.2, y0 + 72.0 - 3.2), 6.4, 6.4, facecolor="#37474F", edgecolor="#78909C", linewidth=1.5, zorder=4))
        ax.add_patch(plt.Circle((bx, y0 + 72.0), 2.0, facecolor=b_col, edgecolor="#FFFFFF", linewidth=1.0, zorder=5))
        ax.text(bx, y0 + 72.0 + 5.5, f"{b_ref}\n{b_lbl}", color="#FFFFFF", fontsize=8, fontweight='bold', ha='center', zorder=6)

    # 7. Relay Drivers: Optocouplers (U5, U6), NPNs (Q1, Q2) & Protection Networks
    for q_ref, qx in [("Q1", x0 + 46.0), ("Q2", x0 + 56.0)]:
        ax.add_patch(patches.Rectangle((qx - 1.5, y0 + 47.0 - 1.0), 3.0, 2.0, facecolor="#111111", edgecolor="#616161", linewidth=0.8, zorder=4))
        ax.text(qx, y0 + 47.0 - 2.2, f"{q_ref}: NPN", color="#B0BEC5", fontsize=7, ha='center', zorder=5)

    # Base drive & pull-down resistors
    ax.add_patch(patches.Rectangle((x0 + 52.0 - 0.8, y0 + 46.0 - 0.5), 1.6, 1.0, facecolor="#333333", edgecolor="#888888", linewidth=0.6, zorder=4))
    ax.text(x0 + 52.0, y0 + 46.0 - 1.2, "R_DRV1\n1k", color="#B0BEC5", fontsize=5.5, ha='center', zorder=5)

    ax.add_patch(patches.Rectangle((x0 + 46.0 - 0.8, y0 + 52.0 - 0.5), 1.6, 1.0, facecolor="#333333", edgecolor="#888888", linewidth=0.6, zorder=4))
    ax.text(x0 + 46.0, y0 + 52.0 - 1.2, "R_PD1\n10k", color="#B0BEC5", fontsize=5.5, ha='center', zorder=5)

    # Optocoupler input resistors R_OPT1, R_OPT2
    ax.add_patch(patches.Rectangle((x0 + 61.0 - 0.8, y0 + 44.0 - 0.5), 1.6, 1.0, facecolor="#333333", edgecolor="#888888", linewidth=0.6, zorder=4))
    ax.text(x0 + 61.0, y0 + 44.0 - 1.2, "R_OPT1\n470Ω", color="#FFD166", fontsize=5.5, ha='center', zorder=5)

    ax.add_patch(patches.Rectangle((x0 + 61.0 - 0.8, y0 + 56.0 - 0.5), 1.6, 1.0, facecolor="#333333", edgecolor="#888888", linewidth=0.6, zorder=4))
    ax.text(x0 + 61.0, y0 + 56.0 - 1.2, "R_OPT2\n470Ω", color="#FFD166", fontsize=5.5, ha='center', zorder=5)

    # Optocouplers (U5, U6) bridging isolation
    for u_ref, u_lbl, uy in [("U5", "Opto 1", y0 + 48.0), ("U6", "Opto 2", y0 + 60.0)]:
        ax.add_patch(patches.Rectangle((slot_x - 3.8, uy - 3.0), 7.6, 6.0, facecolor="#1E1E1E", edgecolor="#FFB703", linewidth=1.5, zorder=4))
        ax.add_patch(plt.Circle((slot_x - 2.8, uy - 1.8), 0.5, facecolor="#FFFFFF", zorder=5))
        ax.text(slot_x, uy, f"{u_ref}\nPC817", color="#FFD166", fontsize=7, fontweight='bold', ha='center', va='center', zorder=6)

    # =========================================================================
    # ZONE 2: 230V AC MAINS & POWER SWITCHING
    # =========================================================================

    # 8. TB2: 230V AC Mains In (Top Right)
    tb2_x, tb2_y = x0 + 110.0, y0 + 12.0
    ax.add_patch(patches.Rectangle((tb2_x - 5.5, tb2_y - 4.5), 11.0, 9.0, facecolor="#B71C1C", edgecolor="#EF5350", linewidth=1.8, zorder=4))
    for dx in [-2.54, 2.54]:
        ax.add_patch(plt.Circle((tb2_x + dx, tb2_y), 1.8, facecolor="#E0E0E0", edgecolor="#757575", linewidth=1.0, zorder=5))
        ax.add_patch(patches.Rectangle((tb2_x + dx - 1.2, tb2_y - 0.25), 2.4, 0.5, facecolor="#424242", zorder=6))
    ax.text(tb2_x - 2.54, tb2_y + 6.2, "L", color="#EF5350", fontsize=9, fontweight='bold', ha='center', zorder=7)
    ax.text(tb2_x + 2.54, tb2_y + 6.2, "N", color="#90CAF9", fontsize=9, fontweight='bold', ha='center', zorder=7)
    ax.text(tb2_x, tb2_y - 6.5, "TB2: AC VOLT SENSE\n(ZMPT101B SENSE ONLY)", color="#EF5350", fontsize=7.5, fontweight='bold', ha='center', zorder=7)

    # 9. T1: ZMPT101B Voltage Transformer & High Voltage Resistors
    t1_x, t1_y = x0 + 86.0, y0 + 18.0
    ax.add_patch(patches.Rectangle((t1_x - 9.0, t1_y - 9.0), 18.0, 18.0, facecolor="#0D1B2A", edgecolor="#415A77", linewidth=2.0, zorder=4))
    ax.add_patch(plt.Circle((t1_x, t1_y), 6.5, facecolor="#1B263B", edgecolor="#778DA9", linewidth=1.5, zorder=5))
    ax.add_patch(plt.Circle((t1_x, t1_y), 3.0, facecolor="#0D1B2A", edgecolor="#415A77", linewidth=1.0, zorder=6))
    ax.text(t1_x, t1_y - 1.0, "T1:\nZMPT101B", color="#E0E1DD", fontsize=8, fontweight='bold', ha='center', va='center', zorder=7)
    ax.text(t1_x, t1_y - 11.0, "Voltage Sensor", color="#E0E1DD", fontsize=8, ha='center', zorder=7)

    # High Voltage Resistors (R_HV1, R_HV2)
    for rhv_ref, rhv_x in [("R_HV1", x0 + 80.0), ("R_HV2", x0 + 102.0)]:
        ax.add_patch(patches.Rectangle((rhv_x - 7.5, y0 + 30.0 - 1.8), 15.0, 3.6, facecolor="#D4A373", edgecolor="#BC6C25", linewidth=1.0, zorder=4))
        ax.text(rhv_x, y0 + 30.0, f"{rhv_ref}: 41.2k 1W", color="#283618", fontsize=7, fontweight='bold', ha='center', va='center', zorder=5)

    # 10. U4: LM358 Conditioner & U3: ACS712T-30A Current Sensor
    u4_x, u4_y = x0 + 78.0, y0 + 40.0
    ax.add_patch(patches.Rectangle((u4_x - 2.5, u4_y - 2.5), 5.0, 5.0, facecolor="#111111", edgecolor="#616161", linewidth=1.0, zorder=4))
    ax.text(u4_x, u4_y, "LM358", color="#E0E0E0", fontsize=7, fontweight='bold', ha='center', va='center', zorder=5)
    ax.text(u4_x, u4_y - 4.0, "U4: AC Filter", color="#CCCCCC", fontsize=8, ha='center', zorder=6)

    # ACS712T-30A Current Sensor (U3) + C_ACS decoupling
    u3_x, u3_y = x0 + 104.0, y0 + 40.0
    ax.add_patch(patches.Rectangle((u3_x - 3.0, u3_y - 2.5), 6.0, 5.0, facecolor="#111111", edgecolor="#E63946", linewidth=1.5, zorder=4))
    ax.text(u3_x, u3_y, "ACS712\n30A", color="#FFD166", fontsize=7, fontweight='bold', ha='center', va='center', zorder=5)
    ax.text(u3_x, u3_y - 4.5, "U3: Current Sensor", color="#E63946", fontsize=8, fontweight='bold', ha='center', zorder=6)

    ax.add_patch(patches.Rectangle((x0 + 96.0 - 0.8, y0 + 40.0 - 0.5), 1.6, 1.0, facecolor="#C49A45", edgecolor="#B7950B", linewidth=0.6, zorder=4))
    ax.text(x0 + 96.0, y0 + 40.0 - 1.2, "C_ACS\n0.1uF", color="#D4AF37", fontsize=5.5, ha='center', zorder=5)

    # 11. Relays K1 & K2, MOV1, Snubber (R_SNUB1 + C_SNUB1)
    # Relay K1 (Primary Pump)
    k1_x, k1_y = x0 + 80.0, y0 + 56.0
    ax.add_patch(patches.Rectangle((k1_x, k1_y - 7.75), 19.0, 15.5, facecolor="#1E88E5", edgecolor="#1565C0", linewidth=2.0, zorder=4))
    ax.text(k1_x + 9.5, k1_y - 1.5, "SONGLE RELAY\n10A 250VAC", color="#FFFFFF", fontsize=8, fontweight='bold', ha='center', va='center', zorder=5)
    ax.text(k1_x + 9.5, k1_y + 4.5, "K1: WILO PUMP", color="#BBDEFB", fontsize=8, fontweight='bold', ha='center', va='center', zorder=5)

    # MOV1 Varistor (14D471K)
    mov_x, mov_y = x0 + 102.0, y0 + 52.0
    ax.add_patch(plt.Circle((mov_x, mov_y), 4.5, facecolor="#0077B6", edgecolor="#03045E", linewidth=1.2, zorder=5))
    ax.text(mov_x, mov_y, "MOV1\n14D471K", color="#FFFFFF", fontsize=6, fontweight='bold', ha='center', va='center', zorder=6)

    # RC Snubber (R_SNUB1 + C_SNUB1)
    ax.add_patch(patches.Rectangle((x0 + 96.0 - 5.0, y0 + 46.0 - 1.5), 10.0, 3.0, facecolor="#D4A373", edgecolor="#BC6C25", linewidth=0.8, zorder=4))
    ax.text(x0 + 96.0, y0 + 46.0, "R_SNUB: 100Ω 1W", color="#283618", fontsize=5.5, fontweight='bold', ha='center', va='center', zorder=5)

    ax.add_patch(patches.Rectangle((x0 + 106.0 - 4.5, y0 + 46.0 - 2.0), 9.0, 4.0, facecolor="#D90429", edgecolor="#EF233C", linewidth=1.0, zorder=4))
    ax.text(x0 + 106.0, y0 + 46.0, "C_SNUB\n0.1uF X2", color="#FFFFFF", fontsize=5.5, fontweight='bold', ha='center', va='center', zorder=5)

    # Relay K2 (Aux / Valve)
    k2_x, k2_y = x0 + 80.0, y0 + 73.0
    ax.add_patch(patches.Rectangle((k2_x, k2_y - 7.75), 19.0, 15.5, facecolor="#1E88E5", edgecolor="#1565C0", linewidth=2.0, zorder=4))
    ax.text(k2_x + 9.5, k2_y - 1.5, "SONGLE RELAY\n10A 250VAC", color="#FFFFFF", fontsize=8, fontweight='bold', ha='center', va='center', zorder=5)
    ax.text(k2_x + 9.5, k2_y + 4.5, "K2: AUX / VALVE", color="#BBDEFB", fontsize=8, fontweight='bold', ha='center', va='center', zorder=5)

    # Flyback Diodes D2, D3
    for d_ref, dy in [("D2", k1_y), ("D3", k2_y)]:
        ax.add_patch(patches.Rectangle((k1_x - 7.0, dy - 1.2), 4.5, 2.4, facecolor="#212121", edgecolor="#9E9E9E", linewidth=0.8, zorder=4))
        ax.text(k1_x - 4.75, dy + 2.5, f"{d_ref}\n1N4007", color="#9E9E9E", fontsize=6, ha='center', zorder=5)

    # 12. TB3: 3-Pin Actuator Output Screw Terminal (Far Right)
    tb3_x, tb3_y = x0 + 112.0, y0 + 64.0
    ax.add_patch(patches.Rectangle((tb3_x - 4.5, tb3_y - 8.0), 9.0, 16.0, facecolor="#2E7D32", edgecolor="#4CAF50", linewidth=1.8, zorder=4))
    for dy, lbl in [(-5.08, "PUMP"), (0, "VALVE"), (5.08, "NEUT")]:
        ax.add_patch(plt.Circle((tb3_x, tb3_y + dy), 1.8, facecolor="#E0E0E0", edgecolor="#757575", linewidth=1.0, zorder=5))
        ax.add_patch(patches.Rectangle((tb3_x - 0.25, tb3_y + dy - 1.2), 0.5, 2.4, facecolor="#424242", zorder=6))
        ax.text(tb3_x + 6.5, tb3_y + dy, lbl, color="#A5D6A7", fontsize=8, fontweight='bold', va='center', zorder=7)
    ax.text(tb3_x, tb3_y - 10.5, "TB3: LOAD OUT", color="#A5D6A7", fontsize=9, fontweight='bold', ha='center', zorder=7)

    # Title & Metadata block
    ax.text(x0 + 60.0, y0 + 82.5, "WILO WATER PUMP AUTOMATION — RECEIVER HAT (120mm x 85mm)", color="#A8DADC", fontsize=10, fontweight='bold', ha='center', zorder=3)

    ax.set_xlim(x0 - 5.0, x0 + w + 5.0)
    ax.set_ylim(y0 + h + 5.0, y0 - 5.0)  # Invert Y so 0 is top
    ax.set_aspect('equal')
    ax.axis('off')

    plt.tight_layout()
    output_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_png, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Generated clean high-res PCB layout PNG: {output_png}")


if __name__ == "__main__":
    out_file = Path("output/wilo_receiver/wilo_receiver_board_top.png")
    render_board_png(out_file)
