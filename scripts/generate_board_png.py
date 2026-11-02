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

    fig, ax = plt.subplots(figsize=(16, 11.3), dpi=250)
    fig.patch.set_facecolor('#0B0F19')
    ax.set_facecolor('#0B0F19')

    # Draw dark green FR4 PCB substrate with soldermask
    pcb_rect = patches.FancyBboxPatch(
        (x0, y0), w, h,
        boxstyle="round,pad=0,rounding_size=3.0",
        facecolor="#064E3B",
        edgecolor="#047857",
        linewidth=2.5,
        zorder=1
    )
    ax.add_patch(pcb_rect)

    # High-Voltage Isolation Milling Slots (Edge.Cuts)
    slot_x = x0 + 67.0
    for sy_start, sy_end in [(y0 + 8.0, y0 + 40.0), (y0 + 66.0, y0 + 78.0)]:
        slot = patches.Rectangle(
            (slot_x - 0.8, sy_start), 1.6, sy_end - sy_start,
            facecolor="#0B0F19", edgecolor="#EF4444", linewidth=1.5,
            linestyle="--", zorder=2
        )
        ax.add_patch(slot)

    # Silkscreen Zone Dividers and Text (Strictly spaced with zero overlaps)
    ax.text(x0 + 32.0, y0 + 3.0, "ZONE 1: LOW-VOLTAGE DC LOGIC (5V USB-C MAIN POWER)", color="#F8FAFC", fontsize=10.5, fontweight='bold', ha='center', va='center', zorder=3)
    ax.text(x0 + 94.0, y0 + 3.0, "ZONE 2: 230V AC SENSE & SWITCHING", color="#F87171", fontsize=10.5, fontweight='bold', ha='center', va='center', zorder=3)
    ax.text(slot_x - 1.8, y0 + 24.0, "ISOLATION BARRIER (5mm CREEPAGE)", color="#FBBF24", fontsize=9, fontweight='bold', rotation=90, ha='center', va='center', zorder=3)

    # Mounting Holes (M2.5 for Raspberry Pi Zero in Zone 1)
    hole_coords = [(x0 + 4.0, y0 + 4.0), (x0 + 62.0, y0 + 4.0), (x0 + 4.0, y0 + 27.0), (x0 + 62.0, y0 + 27.0)]
    for hx, hy in hole_coords:
        ax.add_patch(plt.Circle((hx, hy), 2.2, facecolor="#94A3B8", edgecolor="#64748B", linewidth=1.0, zorder=2))
        ax.add_patch(plt.Circle((hx, hy), 1.35, facecolor="#0B0F19", edgecolor="#334155", linewidth=1.2, zorder=3))
        ax.text(hx, hy + 3.2, "M2.5", color="#CBD5E1", fontsize=6.5, ha='center', va='center', zorder=4)

    # =========================================================================
    # ZONE 1: LOW-VOLTAGE DC LOGIC (5V USB-C MAIN POWER)
    # =========================================================================

    # 1. J1: Raspberry Pi Zero 2W 40-Pin Header
    # Centered at x0 + 32.5, y0 + 12.0
    j1_w, j1_h = 50.8, 5.0
    j1_left = (x0 + 32.5) - (j1_w / 2.0)
    j1_top = (y0 + 12.0) - (j1_h / 2.0)
    ax.add_patch(patches.Rectangle((j1_left, j1_top), j1_w, j1_h, facecolor="#1E293B", edgecolor="#F59E0B", linewidth=1.2, zorder=4))
    
    # Header Pins 2x20
    for col in range(20):
        px = j1_left + 1.27 + col * 2.54
        for row in range(2):
            py = (y0 + 12.0 - 1.27) + row * 2.54
            ax.add_patch(plt.Circle((px, py), 0.75, facecolor="#FBBF24", edgecolor="#D97706", linewidth=0.5, zorder=5))
            ax.add_patch(plt.Circle((px, py), 0.4, facecolor="#0B0F19", zorder=6))
    ax.text(x0 + 32.5, y0 + 7.5, "J1: Raspberry Pi Zero 2W 40-Pin Header", color="#FDE047", fontsize=8.5, fontweight='bold', ha='center', va='center', zorder=7)

    # I2C Pull-Up Resistors (R_PU1, R_PU2)
    for r_ref, rx in [("R_PU1", x0 + 29.0), ("R_PU2", x0 + 35.0)]:
        ax.add_patch(patches.Rectangle((rx - 1.0, y0 + 20.0 - 0.6), 2.0, 1.2, facecolor="#334155", edgecolor="#64748B", linewidth=0.8, zorder=4))
        ax.text(rx, y0 + 22.8, f"{r_ref}\n4.7k", color="#CBD5E1", fontsize=6, ha='center', va='center', zorder=5)

    # TB_EXP Screw Terminal (A2, A3 Expansion) - Cleared completely below J1
    tbexp_x, tbexp_y = x0 + 54.0, y0 + 21.0
    ax.add_patch(patches.Rectangle((tbexp_x - 4.5, tbexp_y - 3.0), 9.0, 6.0, facecolor="#166534", edgecolor="#22C55E", linewidth=1.2, zorder=4))
    for dx in [-2.54, 2.54]:
        ax.add_patch(plt.Circle((tbexp_x + dx, tbexp_y), 1.3, facecolor="#E2E8F0", edgecolor="#94A3B8", linewidth=0.8, zorder=5))
        ax.add_patch(patches.Rectangle((tbexp_x + dx - 1.0, tbexp_y - 0.2), 2.0, 0.4, facecolor="#475569", zorder=6))
    ax.text(tbexp_x, tbexp_y + 5.5, "TB_EXP: A2/A3", color="#86EFAC", fontsize=7, fontweight='bold', ha='center', va='center', zorder=7)

    # 2. SCT-013 CT Clamp Interface (J_CT, R_BURDEN, R_BIAS1, R_BIAS2, C_BIAS)
    jct_x, jct_y = x0 + 6.0, y0 + 26.0
    ax.add_patch(patches.Rectangle((jct_x - 4.5, jct_y - 4.0), 9.0, 8.0, facecolor="#1E293B", edgecolor="#64748B", linewidth=1.2, zorder=4))
    ax.add_patch(plt.Circle((jct_x, jct_y), 2.2, facecolor="#334155", edgecolor="#94A3B8", linewidth=1.0, zorder=5))
    ax.add_patch(plt.Circle((jct_x, jct_y), 1.1, facecolor="#0B0F19", zorder=6))
    ax.text(jct_x + 5.8, jct_y, "J_CT: 3.5mm\nCT Clamp", color="#93C5FD", fontsize=7.5, fontweight='bold', va='center', zorder=7)

    # Burden & Bias Resistors and Filter Cap
    ax.add_patch(patches.Rectangle((x0 + 16.0 - 1.0, y0 + 24.0 - 0.6), 2.0, 1.2, facecolor="#334155", edgecolor="#64748B", linewidth=0.8, zorder=4))
    ax.text(x0 + 16.0, y0 + 21.8, "R_BURDEN\n33Ω", color="#CBD5E1", fontsize=5.8, ha='center', va='center', zorder=5)

    for rb_ref, rby in [("R_BIAS1", y0 + 22.0), ("R_BIAS2", y0 + 26.5)]:
        ax.add_patch(patches.Rectangle((x0 + 22.0 - 1.0, rby - 0.6), 2.0, 1.2, facecolor="#334155", edgecolor="#64748B", linewidth=0.8, zorder=4))
        ax.text(x0 + 22.0, rby - 1.6, f"{rb_ref}: 10k", color="#CBD5E1", fontsize=5.5, ha='center', va='center', zorder=5)

    ax.add_patch(patches.Rectangle((x0 + 28.0 - 1.0, y0 + 25.0 - 0.6), 2.0, 1.2, facecolor="#B45309", edgecolor="#F59E0B", linewidth=0.8, zorder=4))
    ax.text(x0 + 28.0, y0 + 27.5, "C_BIAS\n10uF", color="#FDE047", fontsize=5.5, ha='center', va='center', zorder=5)

    # 3. SX1278 Ra-02 LoRa Module & SMA Connector
    lora_x, lora_y = x0 + 20.0, y0 + 42.0
    ax.add_patch(patches.Rectangle((lora_x - 8.0, lora_y - 8.0), 16.0, 16.0, facecolor="#0F172A", edgecolor="#64748B", linewidth=1.5, zorder=4))
    ax.add_patch(patches.Rectangle((lora_x - 6.5, lora_y - 6.0), 13.0, 11.0, facecolor="#64748B", edgecolor="#94A3B8", linewidth=1.0, zorder=5))
    ax.text(lora_x, lora_y - 1.0, "Ai-Thinker\nRa-02", color="#0F172A", fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=6)
    ax.text(lora_x, lora_y + 3.5, "433MHz LoRa", color="#1E293B", fontsize=6.5, ha='center', va='center', zorder=6)
    ax.text(lora_x, lora_y - 9.8, "U_LORA: SX1278", color="#F8FAFC", fontsize=8.5, fontweight='bold', ha='center', va='center', zorder=7)

    # LoRa Filtering Capacitors (10uF + 0.1uF)
    for cl_ref, cl_val, clx in [("C_LORA1", "10uF", x0 + 15.0), ("C_LORA2", "0.1uF", x0 + 21.0)]:
        ax.add_patch(patches.Rectangle((clx - 1.0, y0 + 33.0 - 0.6), 2.0, 1.2, facecolor="#B45309", edgecolor="#F59E0B", linewidth=0.8, zorder=4))
        ax.text(clx, y0 + 31.0, f"{cl_ref}\n{cl_val}", color="#FDE047", fontsize=5.5, ha='center', va='center', zorder=5)

    # Castellated pads on LoRa module
    for i in range(8):
        ax.add_patch(patches.Rectangle((lora_x - 8.2, lora_y - 7.0 + i * 2.0), 1.4, 1.0, facecolor="#FBBF24", edgecolor="#D97706", linewidth=0.5, zorder=6))
        ax.add_patch(patches.Rectangle((lora_x + 6.8, lora_y - 7.0 + i * 2.0), 1.4, 1.0, facecolor="#FBBF24", edgecolor="#D97706", linewidth=0.5, zorder=6))

    # SMA Connector (J_SMA) on board edge
    sma_x, sma_y = x0 + 4.0, y0 + 42.0
    ax.add_patch(patches.Rectangle((sma_x - 3.5, sma_y - 3.5), 7.0, 7.0, facecolor="#B45309", edgecolor="#F59E0B", linewidth=1.5, zorder=4))
    ax.add_patch(plt.Circle((sma_x, sma_y), 2.5, facecolor="#F59E0B", edgecolor="#D97706", linewidth=1.0, zorder=5))
    ax.add_patch(plt.Circle((sma_x, sma_y), 0.8, facecolor="#FEF08A", zorder=6))
    ax.text(sma_x + 1.2, sma_y + 5.5, "J_SMA\n50Ω Ant", color="#F59E0B", fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=7)

    # 4. ADS1115 16-Bit I2C ADC (U2) & Decoupling (C_ADS)
    adc_x, adc_y = x0 + 48.0, y0 + 36.0
    ax.add_patch(patches.Rectangle((adc_x - 2.5, adc_y - 2.0), 5.0, 4.0, facecolor="#0F172A", edgecolor="#64748B", linewidth=1.2, zorder=4))
    ax.add_patch(plt.Circle((adc_x - 1.8, adc_y - 1.2), 0.35, facecolor="#FFFFFF", zorder=5))
    ax.text(adc_x, adc_y, "ADS1115", color="#E2E8F0", fontsize=6.5, fontweight='bold', ha='center', va='center', zorder=6)
    ax.text(adc_x, adc_y - 3.5, "U2: 16-Bit ADC", color="#93C5FD", fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=7)

    ax.add_patch(patches.Rectangle((x0 + 54.0 - 0.8, adc_y - 0.6), 1.6, 1.2, facecolor="#B45309", edgecolor="#F59E0B", linewidth=0.8, zorder=4))
    ax.text(x0 + 54.0, adc_y + 2.2, "C_ADS\n100nF", color="#FDE047", fontsize=5.5, ha='center', va='center', zorder=5)

    # 5. Power Supply: J_USBC (5V DC USB-C Main Power), U1 (AMS1117-3.3V)
    usbc_x, usbc_y = x0 + 5.5, y0 + 68.0
    ax.add_patch(patches.Rectangle((usbc_x - 4.5, usbc_y - 4.5), 9.0, 9.0, facecolor="#334155", edgecolor="#94A3B8", linewidth=1.5, zorder=4))
    ax.add_patch(patches.FancyBboxPatch((usbc_x - 3.5, usbc_y - 1.8), 7.0, 3.6, boxstyle="round,pad=0,rounding_size=1.5", facecolor="#0F172A", edgecolor="#CBD5E1", linewidth=1.0, zorder=5))
    ax.text(usbc_x + 0.5, usbc_y - 6.2, "J_USBC: 5V DC IN\n(MAIN POWER)", color="#60A5FA", fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=7)

    # CC Resistors R_CC1, R_CC2
    for rcc_ref, rcc_y in [("R_CC1", y0 + 65.0), ("R_CC2", y0 + 71.0)]:
        ax.add_patch(patches.Rectangle((x0 + 13.0 - 0.8, rcc_y - 0.5), 1.6, 1.0, facecolor="#334155", edgecolor="#64748B", linewidth=0.6, zorder=4))
        ax.text(x0 + 13.0, rcc_y - 1.3, f"{rcc_ref}: 5.1k", color="#94A3B8", fontsize=5.2, ha='center', va='center', zorder=5)

    # Filter Capacitor C1 (10uF)
    ax.add_patch(patches.Rectangle((x0 + 18.0 - 1.0, y0 + 68.0 - 0.6), 2.0, 1.2, facecolor="#B45309", edgecolor="#F59E0B", linewidth=0.8, zorder=4))
    ax.text(x0 + 18.0, y0 + 71.0, "C1: 10uF", color="#FDE047", fontsize=5.8, ha='center', va='center', zorder=5)

    # AMS1117-3.3 LDO (U1)
    u1_x, u1_y = x0 + 25.0, y0 + 68.0
    ax.add_patch(patches.Rectangle((u1_x - 3.5, u1_y - 2.5), 7.0, 5.0, facecolor="#0F172A", edgecolor="#64748B", linewidth=1.2, zorder=4))
    ax.add_patch(patches.Rectangle((u1_x - 2.5, u1_y + 2.5), 5.0, 1.5, facecolor="#94A3B8", edgecolor="#64748B", linewidth=0.8, zorder=4))
    ax.text(u1_x, u1_y, "AMS1117\n3.3V", color="#F8FAFC", fontsize=6.5, fontweight='bold', ha='center', va='center', zorder=5)
    ax.text(u1_x, u1_y - 4.5, "U1: 3.3V LDO", color="#86EFAC", fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=6)

    # Filter Capacitor C2 (22uF)
    ax.add_patch(patches.Rectangle((x0 + 32.0 - 1.0, y0 + 68.0 - 0.6), 2.0, 1.2, facecolor="#B45309", edgecolor="#F59E0B", linewidth=0.8, zorder=4))
    ax.text(x0 + 32.0, y0 + 71.0, "C2: 22uF", color="#FDE047", fontsize=5.8, ha='center', va='center', zorder=5)

    # 6. Status LEDs & User Controls
    # R_LED2 & R_LED3 current limiting
    ax.add_patch(patches.Rectangle((x0 + 12.0 - 0.8, y0 + 51.0 - 0.5), 1.6, 1.0, facecolor="#334155", edgecolor="#64748B", linewidth=0.6, zorder=4))
    ax.text(x0 + 12.0, y0 + 48.8, "R_LED2\n470Ω", color="#94A3B8", fontsize=5.2, ha='center', va='center', zorder=5)

    ax.add_patch(patches.Rectangle((x0 + 20.0 - 0.8, y0 + 51.0 - 0.5), 1.6, 1.0, facecolor="#334155", edgecolor="#64748B", linewidth=0.6, zorder=4))
    ax.text(x0 + 20.0, y0 + 48.8, "R_LED3\n330Ω", color="#94A3B8", fontsize=5.2, ha='center', va='center', zorder=5)

    leds = [
        ("LED_5V", "5V PWR", x0 + 12.0, "#22C55E"),
        ("LED_3V3", "3V3 RF", x0 + 20.0, "#3B82F6"),
        ("LED_PUMP", "PUMP ON", x0 + 36.0, "#EAB308"),
    ]
    for l_ref, l_lbl, lx, col in leds:
        ax.add_patch(patches.Rectangle((lx - 1.2, y0 + 56.0 - 0.8), 2.4, 1.6, facecolor=col, edgecolor="#FFFFFF", linewidth=1.0, zorder=4))
        ax.text(lx, y0 + 59.0, f"{l_ref}\n{l_lbl}", color=col, fontsize=6.5, fontweight='bold', ha='center', va='center', zorder=5)

    # R_LED1 330-ohm series resistor for Pump LED
    ax.add_patch(patches.Rectangle((x0 + 28.0 - 1.0, y0 + 56.0 - 0.6), 2.0, 1.2, facecolor="#334155", edgecolor="#64748B", linewidth=0.8, zorder=4))
    ax.text(x0 + 28.0, y0 + 59.0, "R_LED1\n330Ω", color="#CBD5E1", fontsize=5.5, ha='center', va='center', zorder=5)

    # Push Buttons SW1 (Force ON) and SW2 (Force OFF)
    buttons = [
        ("SW1", "FORCE ON", x0 + 42.0, "#166534"),
        ("SW2", "FORCE OFF", x0 + 56.0, "#991B1B"),
    ]
    for b_ref, b_lbl, bx, b_col in buttons:
        ax.add_patch(patches.Rectangle((bx - 3.2, y0 + 68.0 - 3.2), 6.4, 6.4, facecolor="#334155", edgecolor="#64748B", linewidth=1.2, zorder=4))
        ax.add_patch(plt.Circle((bx, y0 + 68.0), 2.0, facecolor=b_col, edgecolor="#FFFFFF", linewidth=1.0, zorder=5))
        ax.text(bx, y0 + 74.5, f"{b_ref}\n{b_lbl}", color="#F8FAFC", fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=6)

    # 7. Relay Drivers: NPNs (Q1, Q2), Resistors & Boundary Optocouplers (U5, U6)
    for q_ref, qx in [("Q1", x0 + 46.0), ("Q2", x0 + 56.0)]:
        ax.add_patch(patches.Rectangle((qx - 1.5, y0 + 47.0 - 1.0), 3.0, 2.0, facecolor="#0F172A", edgecolor="#64748B", linewidth=0.8, zorder=4))
        ax.text(qx, y0 + 44.5, f"{q_ref}: NPN", color="#94A3B8", fontsize=6.5, ha='center', va='center', zorder=5)

    ax.add_patch(patches.Rectangle((x0 + 51.5 - 0.8, y0 + 46.0 - 0.5), 1.6, 1.0, facecolor="#334155", edgecolor="#64748B", linewidth=0.6, zorder=4))
    ax.text(x0 + 51.5, y0 + 48.0, "R_DRV1\n1k", color="#94A3B8", fontsize=5.2, ha='center', va='center', zorder=5)

    ax.add_patch(patches.Rectangle((x0 + 46.0 - 0.8, y0 + 52.0 - 0.5), 1.6, 1.0, facecolor="#334155", edgecolor="#64748B", linewidth=0.6, zorder=4))
    ax.text(x0 + 46.0, y0 + 54.0, "R_PD1\n10k", color="#94A3B8", fontsize=5.2, ha='center', va='center', zorder=5)

    # Optocoupler input resistors R_OPT1, R_OPT2
    ax.add_patch(patches.Rectangle((x0 + 61.0 - 0.8, y0 + 44.0 - 0.5), 1.6, 1.0, facecolor="#334155", edgecolor="#64748B", linewidth=0.6, zorder=4))
    ax.text(x0 + 61.0, y0 + 42.0, "R_OPT1\n470Ω", color="#FBBF24", fontsize=5.2, ha='center', va='center', zorder=5)

    ax.add_patch(patches.Rectangle((x0 + 61.0 - 0.8, y0 + 56.0 - 0.5), 1.6, 1.0, facecolor="#334155", edgecolor="#64748B", linewidth=0.6, zorder=4))
    ax.text(x0 + 61.0, y0 + 54.0, "R_OPT2\n470Ω", color="#FBBF24", fontsize=5.2, ha='center', va='center', zorder=5)

    # Optocouplers (U5, U6) straddling isolation barrier at slot_x = x0 + 67.0
    for u_ref, uy in [("U5", y0 + 48.0), ("U6", y0 + 60.0)]:
        ax.add_patch(patches.Rectangle((slot_x - 3.8, uy - 3.0), 7.6, 6.0, facecolor="#0F172A", edgecolor="#F59E0B", linewidth=1.5, zorder=4))
        ax.add_patch(plt.Circle((slot_x - 2.8, uy - 1.8), 0.5, facecolor="#FFFFFF", zorder=5))
        ax.text(slot_x, uy, f"{u_ref}\nPC817", color="#FDE047", fontsize=6.8, fontweight='bold', ha='center', va='center', zorder=6)

    # =========================================================================
    # ZONE 2: 230V AC MAINS & POWER SWITCHING
    # =========================================================================

    # 8. TB2: 230V AC Mains In (Placed at x0 + 110.0, y0 + 14.0)
    # Silkscreen text is strictly placed BELOW at y0 + 21.5 to guarantee ZERO overlap with Zone 2 Header
    tb2_x, tb2_y = x0 + 110.0, y0 + 14.0
    ax.add_patch(patches.Rectangle((tb2_x - 5.5, tb2_y - 4.5), 11.0, 9.0, facecolor="#7F1D1D", edgecolor="#EF4444", linewidth=1.5, zorder=4))
    for dx in [-2.54, 2.54]:
        ax.add_patch(plt.Circle((tb2_x + dx, tb2_y), 1.8, facecolor="#E2E8F0", edgecolor="#94A3B8", linewidth=1.0, zorder=5))
        ax.add_patch(patches.Rectangle((tb2_x + dx - 1.2, tb2_y - 0.25), 2.4, 0.5, facecolor="#334155", zorder=6))
    ax.text(tb2_x - 2.54, tb2_y - 6.0, "L", color="#F87171", fontsize=8.5, fontweight='bold', ha='center', va='center', zorder=7)
    ax.text(tb2_x + 2.54, tb2_y - 6.0, "N", color="#60A5FA", fontsize=8.5, fontweight='bold', ha='center', va='center', zorder=7)
    ax.text(tb2_x, tb2_y + 7.5, "TB2: 230V AC SENSE ONLY\n(ZMPT101B SENSE ONLY)", color="#FCA5A5", fontsize=7.2, fontweight='bold', ha='center', va='center', zorder=7)

    # 9. T1: ZMPT101B Voltage Transformer & High Voltage Resistors
    t1_x, t1_y = x0 + 86.0, y0 + 18.0
    ax.add_patch(patches.Rectangle((t1_x - 9.0, t1_y - 9.0), 18.0, 18.0, facecolor="#0B132B", edgecolor="#3A506B", linewidth=2.0, zorder=4))
    ax.add_patch(plt.Circle((t1_x, t1_y), 6.5, facecolor="#1C2541", edgecolor="#5BC0BE", linewidth=1.2, zorder=5))
    ax.add_patch(plt.Circle((t1_x, t1_y), 3.0, facecolor="#0B132B", edgecolor="#3A506B", linewidth=1.0, zorder=6))
    ax.text(t1_x, t1_y - 1.0, "T1:\nZMPT101B", color="#F8FAFC", fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=7)
    ax.text(t1_x, t1_y - 11.2, "Voltage Sensor", color="#94A3B8", fontsize=7.5, ha='center', va='center', zorder=7)

    # High Voltage Resistors (R_HV1, R_HV2)
    for rhv_ref, rhv_x in [("R_HV1", x0 + 80.0), ("R_HV2", x0 + 102.0)]:
        ax.add_patch(patches.Rectangle((rhv_x - 7.5, y0 + 30.0 - 1.8), 15.0, 3.6, facecolor="#92400E", edgecolor="#D97706", linewidth=1.0, zorder=4))
        ax.text(rhv_x, y0 + 30.0, f"{rhv_ref}: 41.2k 1W", color="#FEF08A", fontsize=6.8, fontweight='bold', ha='center', va='center', zorder=5)

    # 10. U4: LM358 Conditioner & U3: ACS712T-30A Current Sensor
    u4_x, u4_y = x0 + 78.0, y0 + 40.0
    ax.add_patch(patches.Rectangle((u4_x - 2.5, u4_y - 2.5), 5.0, 5.0, facecolor="#0F172A", edgecolor="#64748B", linewidth=1.0, zorder=4))
    ax.text(u4_x, u4_y, "LM358", color="#E2E8F0", fontsize=6.5, fontweight='bold', ha='center', va='center', zorder=5)
    ax.text(u4_x, u4_y - 4.2, "U4: AC Filter", color="#94A3B8", fontsize=7.5, ha='center', va='center', zorder=6)

    # ACS712T-30A Current Sensor (U3) + C_ACS decoupling
    u3_x, u3_y = x0 + 104.0, y0 + 40.0
    ax.add_patch(patches.Rectangle((u3_x - 3.0, u3_y - 2.5), 6.0, 5.0, facecolor="#0F172A", edgecolor="#EF4444", linewidth=1.5, zorder=4))
    ax.text(u3_x, u3_y, "ACS712\n30A", color="#FDE047", fontsize=6.5, fontweight='bold', ha='center', va='center', zorder=5)
    ax.text(u3_x, u3_y - 4.5, "U3: Current Sensor", color="#F87171", fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=6)

    ax.add_patch(patches.Rectangle((x0 + 96.0 - 0.8, y0 + 40.0 - 0.5), 1.6, 1.0, facecolor="#B45309", edgecolor="#F59E0B", linewidth=0.6, zorder=4))
    ax.text(x0 + 96.0, y0 + 42.0, "C_ACS\n0.1uF", color="#FDE047", fontsize=5.2, ha='center', va='center', zorder=5)

    # 11. Relays K1 & K2, MOV1, Snubber (R_SNUB1 + C_SNUB1)
    # Relay K1 (Primary Pump)
    k1_x, k1_y = x0 + 80.0, y0 + 56.0
    ax.add_patch(patches.Rectangle((k1_x, k1_y - 7.75), 19.0, 15.5, facecolor="#1D4ED8", edgecolor="#2563EB", linewidth=1.8, zorder=4))
    ax.text(k1_x + 9.5, k1_y - 1.5, "SONGLE RELAY\n10A 250VAC", color="#FFFFFF", fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=5)
    ax.text(k1_x + 9.5, k1_y + 4.5, "K1: WILO PUMP", color="#BFDBFE", fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=5)

    # MOV1 Varistor (14D471K)
    mov_x, mov_y = x0 + 102.0, y0 + 52.0
    ax.add_patch(plt.Circle((mov_x, mov_y), 4.5, facecolor="#0284C7", edgecolor="#0369A1", linewidth=1.2, zorder=5))
    ax.text(mov_x, mov_y, "MOV1\n14D471K", color="#FFFFFF", fontsize=5.8, fontweight='bold', ha='center', va='center', zorder=6)

    # RC Snubber (R_SNUB1 + C_SNUB1)
    ax.add_patch(patches.Rectangle((x0 + 95.0 - 4.5, y0 + 46.0 - 1.5), 9.0, 3.0, facecolor="#92400E", edgecolor="#D97706", linewidth=0.8, zorder=4))
    ax.text(x0 + 95.0, y0 + 46.0, "R_SNUB\n100Ω 1W", color="#FEF08A", fontsize=5.2, fontweight='bold', ha='center', va='center', zorder=5)

    ax.add_patch(patches.Rectangle((x0 + 105.0 - 4.0, y0 + 46.0 - 2.0), 8.0, 4.0, facecolor="#B91C1C", edgecolor="#DC2626", linewidth=1.0, zorder=4))
    ax.text(x0 + 105.0, y0 + 46.0, "C_SNUB\n0.1uF X2", color="#FFFFFF", fontsize=5.2, fontweight='bold', ha='center', va='center', zorder=5)

    # Relay K2 (Aux / Valve)
    k2_x, k2_y = x0 + 80.0, y0 + 73.0
    ax.add_patch(patches.Rectangle((k2_x, k2_y - 7.75), 19.0, 15.5, facecolor="#1D4ED8", edgecolor="#2563EB", linewidth=1.8, zorder=4))
    ax.text(k2_x + 9.5, k2_y - 1.5, "SONGLE RELAY\n10A 250VAC", color="#FFFFFF", fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=5)
    ax.text(k2_x + 9.5, k2_y + 4.5, "K2: AUX / VALVE", color="#BFDBFE", fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=5)

    # Flyback Diodes D2, D3
    for d_ref, dy in [("D2", k1_y), ("D3", k2_y)]:
        ax.add_patch(patches.Rectangle((k1_x - 7.0, dy - 1.2), 4.5, 2.4, facecolor="#0F172A", edgecolor="#94A3B8", linewidth=0.8, zorder=4))
        ax.text(k1_x - 4.75, dy + 2.5, f"{d_ref}\n1N4007", color="#CBD5E1", fontsize=5.5, ha='center', va='center', zorder=5)

    # 12. TB3: 3-Pin Actuator Output Screw Terminal (Far Right)
    tb3_x, tb3_y = x0 + 112.0, y0 + 64.0
    ax.add_patch(patches.Rectangle((tb3_x - 4.5, tb3_y - 8.0), 9.0, 16.0, facecolor="#166534", edgecolor="#22C55E", linewidth=1.5, zorder=4))
    for dy, lbl in [(-5.08, "PUMP"), (0, "VALVE"), (5.08, "NEUT")]:
        ax.add_patch(plt.Circle((tb3_x, tb3_y + dy), 1.8, facecolor="#E2E8F0", edgecolor="#94A3B8", linewidth=1.0, zorder=5))
        ax.add_patch(patches.Rectangle((tb3_x - 0.25, tb3_y + dy - 1.2), 0.5, 2.4, facecolor="#334155", zorder=6))
        ax.text(tb3_x + 6.2, tb3_y + dy, lbl, color="#86EFAC", fontsize=7.5, fontweight='bold', va='center', zorder=7)
    ax.text(tb3_x, tb3_y - 10.5, "TB3: LOAD OUT", color="#86EFAC", fontsize=8.5, fontweight='bold', ha='center', va='center', zorder=7)

    # Title & Metadata block
    ax.text(x0 + 60.0, y0 + 82.5, "WILO WATER PUMP AUTOMATION — RECEIVER HAT (120mm x 85mm)", color="#94A3B8", fontsize=9.5, fontweight='bold', ha='center', va='center', zorder=3)

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
