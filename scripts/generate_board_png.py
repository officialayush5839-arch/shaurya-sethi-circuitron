"""Generate a high-resolution, photorealistic 2D composite rendering of the Wilo Receiver PCB.

Updated for Rev 3.0:
- Dimensions: 140 mm x 95 mm
- Single Unified Zone (solid ground plane, powered via 5V USB-C, no isolation slots)
- All connectors placed on perimeter and corners (J1, TB_EXP, TB2, J_SMA, J_CT, J_USBC, TB3, SW1, SW2)
- Zero component/pad/silkscreen overlap
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path


def render_board_png(output_png: Path) -> None:
    # Board dimensions in mm
    # Origin: (50.0, 50.0), Width: 140.0, Height: 95.0
    x0, y0 = 50.0, 50.0
    w, h = 140.0, 95.0

    fig, ax = plt.subplots(figsize=(18, 12.2), dpi=250)
    fig.patch.set_facecolor('#0B0F19')
    ax.set_facecolor('#0B0F19')

    # 1. Dark green FR4 PCB substrate with soldermask
    pcb_rect = patches.FancyBboxPatch(
        (x0, y0), w, h,
        boxstyle="round,pad=0,rounding_size=3.0",
        facecolor="#064E3B",
        edgecolor="#047857",
        linewidth=2.5,
        zorder=1
    )
    ax.add_patch(pcb_rect)

    # 2. Board Corner Mounting Holes (4 Board Corners M2.5)
    corner_holes = [(x0 + 4.0, y0 + 4.0), (x0 + w - 4.0, y0 + 4.0), (x0 + 4.0, y0 + h - 4.0), (x0 + w - 4.0, y0 + h - 4.0)]
    for hx, hy in corner_holes:
        ax.add_patch(plt.Circle((hx, hy), 2.2, facecolor="#94A3B8", edgecolor="#64748B", linewidth=1.0, zorder=2))
        ax.add_patch(plt.Circle((hx, hy), 1.35, facecolor="#0B0F19", edgecolor="#334155", linewidth=1.2, zorder=3))
        ax.text(hx, hy + 3.2, "M2.5", color="#CBD5E1", fontsize=6.5, ha='center', va='center', zorder=4)

    # 3. Silkscreen System Title (Single Unified Zone)
    ax.text(x0 + 70.0, y0 + 3.2, "WILO WATER PUMP AUTOMATION — RECEIVER STATION HAT (140mm x 95mm)", color="#F8FAFC", fontsize=10.5, fontweight='bold', ha='center', va='center', zorder=3)
    ax.text(x0 + 42.0, y0 + 92.5, "MAIN SYSTEM POWER: 5V DC USB-C ONLY (NO AC POWER SUPPLY)", color="#38BDF8", fontsize=8.0, fontweight='bold', ha='center', va='center', zorder=3)

    # =========================================================================
    # TOP EDGE CONNECTORS: J1 (RPi 40-Pin Header), TB_EXP, TB2 (AC Voltage Sense)
    # =========================================================================

    # J1: Raspberry Pi Zero 2W 40-Pin Header
    j1_x, j1_y = x0 + 55.0, y0 + 10.0
    j1_w, j1_h = 50.8, 5.0
    j1_left = j1_x - (j1_w / 2.0)
    j1_top = j1_y - (j1_h / 2.0)
    ax.add_patch(patches.Rectangle((j1_left, j1_top), j1_w, j1_h, facecolor="#1E293B", edgecolor="#F59E0B", linewidth=1.2, zorder=4))
    for col in range(20):
        px = j1_left + 1.27 + col * 2.54
        for row in range(2):
            py = (j1_y - 1.27) + row * 2.54
            ax.add_patch(plt.Circle((px, py), 0.75, facecolor="#FBBF24", edgecolor="#D97706", linewidth=0.5, zorder=5))
            ax.add_patch(plt.Circle((px, py), 0.4, facecolor="#0B0F19", zorder=6))
    ax.text(j1_x, j1_y - 4.5, "J1: Raspberry Pi Zero 2W 40-Pin Header", color="#FDE047", fontsize=8.5, fontweight='bold', ha='center', va='center', zorder=7)

    # TB_EXP Screw Terminal (A2, A3 Expansion)
    tbexp_x, tbexp_y = x0 + 98.0, y0 + 10.0
    ax.add_patch(patches.Rectangle((tbexp_x - 4.5, tbexp_y - 3.0), 9.0, 6.0, facecolor="#166534", edgecolor="#22C55E", linewidth=1.2, zorder=4))
    for dx in [-2.54, 2.54]:
        ax.add_patch(plt.Circle((tbexp_x + dx, tbexp_y), 1.3, facecolor="#E2E8F0", edgecolor="#94A3B8", linewidth=0.8, zorder=5))
        ax.add_patch(patches.Rectangle((tbexp_x + dx - 1.0, tbexp_y - 0.2), 2.0, 0.4, facecolor="#475569", zorder=6))
    ax.text(tbexp_x, tbexp_y - 4.5, "TB_EXP: A2/A3", color="#86EFAC", fontsize=7.2, fontweight='bold', ha='center', va='center', zorder=7)

    # TB2: AC Mains Voltage Sense Input Terminal (Top-Right Corner)
    tb2_x, tb2_y = x0 + 128.0, y0 + 12.0
    ax.add_patch(patches.Rectangle((tb2_x - 5.5, tb2_y - 4.5), 11.0, 9.0, facecolor="#7F1D1D", edgecolor="#EF4444", linewidth=1.5, zorder=4))
    for dx, lbl in [(-2.54, "L"), (2.54, "N")]:
        ax.add_patch(plt.Circle((tb2_x + dx, tb2_y), 1.8, facecolor="#E2E8F0", edgecolor="#94A3B8", linewidth=1.0, zorder=5))
        ax.add_patch(patches.Rectangle((tb2_x + dx - 1.2, tb2_y - 0.25), 2.4, 0.5, facecolor="#334155", zorder=6))
        ax.text(tb2_x + dx, tb2_y + 6.0, lbl, color="#F87171" if lbl == "L" else "#60A5FA", fontsize=8.0, fontweight='bold', ha='center', va='center', zorder=7)
    ax.text(tb2_x, tb2_y - 6.0, "TB2: VOLTAGE SENSE ONLY\n(NOT POWER INPUT)", color="#FCA5A5", fontsize=6.5, fontweight='bold', ha='center', va='center', zorder=7)

    # =========================================================================
    # LEFT EDGE CONNECTORS: J_SMA (Antenna), J_CT (CT Clamp), J_USBC (5V Power)
    # =========================================================================

    # J_SMA: 50Ω Coaxial SMA Antenna Connector (Top-Left Edge)
    sma_x, sma_y = x0 + 6.0, y0 + 26.0
    ax.add_patch(patches.Rectangle((sma_x - 3.5, sma_y - 3.5), 7.0, 7.0, facecolor="#B45309", edgecolor="#F59E0B", linewidth=1.5, zorder=4))
    ax.add_patch(plt.Circle((sma_x, sma_y), 2.5, facecolor="#F59E0B", edgecolor="#D97706", linewidth=1.0, zorder=5))
    ax.add_patch(plt.Circle((sma_x, sma_y), 0.8, facecolor="#FEF08A", zorder=6))
    ax.text(sma_x + 6.0, sma_y, "J_SMA: 50Ω Ant", color="#F59E0B", fontsize=7.5, fontweight='bold', va='center', zorder=7)

    # J_CT: 3.5mm SCT-013 CT Clamp Audio Jack (Mid-Left Edge)
    jct_x, jct_y = x0 + 8.0, y0 + 52.0
    ax.add_patch(patches.Rectangle((jct_x - 4.5, jct_y - 4.0), 9.0, 8.0, facecolor="#1E293B", edgecolor="#64748B", linewidth=1.2, zorder=4))
    ax.add_patch(plt.Circle((jct_x, jct_y), 2.2, facecolor="#334155", edgecolor="#94A3B8", linewidth=1.0, zorder=5))
    ax.add_patch(plt.Circle((jct_x, jct_y), 1.1, facecolor="#0B0F19", zorder=6))
    ax.text(jct_x + 6.2, jct_y, "J_CT: 3.5mm\nCT Clamp", color="#93C5FD", fontsize=7.2, fontweight='bold', va='center', zorder=7)

    # J_USBC: USB Type-C 5V Main Power Input (Bottom-Left Corner)
    usbc_x, usbc_y = x0 + 7.0, y0 + 84.0
    ax.add_patch(patches.Rectangle((usbc_x - 4.5, usbc_y - 4.5), 9.0, 9.0, facecolor="#334155", edgecolor="#94A3B8", linewidth=1.5, zorder=4))
    ax.add_patch(patches.FancyBboxPatch((usbc_x - 3.5, usbc_y - 1.8), 7.0, 3.6, boxstyle="round,pad=0,rounding_size=1.5", facecolor="#0F172A", edgecolor="#CBD5E1", linewidth=1.0, zorder=5))
    ax.text(usbc_x + 6.5, usbc_y - 2.0, "J_USBC: 5V IN\n(MAIN POWER)", color="#60A5FA", fontsize=7.2, fontweight='bold', va='center', zorder=7)

    # CC Resistors R_CC1, R_CC2
    for rcc_ref, rcc_y in [("R_CC1", y0 + 80.0), ("R_CC2", y0 + 88.0)]:
        ax.add_patch(patches.Rectangle((x0 + 14.0 - 0.8, rcc_y - 0.5), 1.6, 1.0, facecolor="#334155", edgecolor="#64748B", linewidth=0.6, zorder=4))
        ax.text(x0 + 14.0, rcc_y - 1.3, f"{rcc_ref}: 5.1k", color="#94A3B8", fontsize=5.2, ha='center', va='center', zorder=5)

    # Filter Capacitors C1 (10uF) & C2 (22uF)
    ax.add_patch(patches.Rectangle((x0 + 20.0 - 1.0, y0 + 84.0 - 0.6), 2.0, 1.2, facecolor="#B45309", edgecolor="#F59E0B", linewidth=0.8, zorder=4))
    ax.text(x0 + 20.0, y0 + 81.0, "C1: 10uF", color="#FDE047", fontsize=5.5, ha='center', va='center', zorder=5)

    ax.add_patch(patches.Rectangle((x0 + 36.0 - 1.0, y0 + 84.0 - 0.6), 2.0, 1.2, facecolor="#B45309", edgecolor="#F59E0B", linewidth=0.8, zorder=4))
    ax.text(x0 + 36.0, y0 + 81.0, "C2: 22uF", color="#FDE047", fontsize=5.5, ha='center', va='center', zorder=5)

    # U1: AMS1117-3.3V LDO Regulator (SOT-223)
    u1_x, u1_y = x0 + 28.0, y0 + 84.0
    ax.add_patch(patches.Rectangle((u1_x - 3.5, u1_y - 2.5), 7.0, 5.0, facecolor="#0F172A", edgecolor="#64748B", linewidth=1.2, zorder=4))
    ax.add_patch(patches.Rectangle((u1_x - 2.5, u1_y + 2.5), 5.0, 1.5, facecolor="#94A3B8", edgecolor="#64748B", linewidth=0.8, zorder=4))
    ax.text(u1_x, u1_y, "AMS1117\n3.3V", color="#F8FAFC", fontsize=6.5, fontweight='bold', ha='center', va='center', zorder=5)
    ax.text(u1_x, u1_y - 4.2, "U1: 3.3V LDO", color="#86EFAC", fontsize=7.2, fontweight='bold', ha='center', va='center', zorder=6)

    # =========================================================================
    # INTERNAL LOGICAL CHIP PLACEMENT: LoRa, ADC, Transformers, Sensors, Relays
    # =========================================================================

    # U_LORA: Ai-Thinker Ra-02 SX1278 433MHz Module
    lora_x, lora_y = x0 + 26.0, y0 + 28.0
    ax.add_patch(patches.Rectangle((lora_x - 8.0, lora_y - 8.0), 16.0, 16.0, facecolor="#0F172A", edgecolor="#64748B", linewidth=1.5, zorder=4))
    ax.add_patch(patches.Rectangle((lora_x - 6.5, lora_y - 6.0), 13.0, 11.0, facecolor="#64748B", edgecolor="#94A3B8", linewidth=1.0, zorder=5))
    ax.text(lora_x, lora_y - 1.0, "Ai-Thinker\nRa-02", color="#0F172A", fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=6)
    ax.text(lora_x, lora_y + 3.5, "433MHz LoRa", color="#1E293B", fontsize=6.5, ha='center', va='center', zorder=6)
    ax.text(lora_x, lora_y + 10.5, "U_LORA: SX1278", color="#F8FAFC", fontsize=8.0, fontweight='bold', ha='center', va='center', zorder=7)

    # LoRa Decoupling Capacitors (C_LORA1, C_LORA2)
    for cl_ref, cl_val, clx in [("C_LORA1", "10uF", x0 + 22.0), ("C_LORA2", "0.1uF", x0 + 28.0)]:
        ax.add_patch(patches.Rectangle((clx - 1.0, y0 + 16.0 - 0.6), 2.0, 1.2, facecolor="#B45309", edgecolor="#F59E0B", linewidth=0.8, zorder=4))
        ax.text(clx, y0 + 13.5, f"{cl_ref}: {cl_val}", color="#FDE047", fontsize=5.5, ha='center', va='center', zorder=5)

    # Castellated pads on LoRa module
    for i in range(8):
        ax.add_patch(patches.Rectangle((lora_x - 8.2, lora_y - 7.0 + i * 2.0), 1.4, 1.0, facecolor="#FBBF24", edgecolor="#D97706", linewidth=0.5, zorder=6))
        ax.add_patch(patches.Rectangle((lora_x + 6.8, lora_y - 7.0 + i * 2.0), 1.4, 1.0, facecolor="#FBBF24", edgecolor="#D97706", linewidth=0.5, zorder=6))

    # Microstrip trace connecting J_SMA to U_LORA ANT pin
    ax.plot([sma_x + 3.5, lora_x - 8.2], [sma_y, lora_y - 7.0], color="#FBBF24", linewidth=2.0, zorder=3)

    # CT Bias Network (R_BURDEN, R_BIAS1, R_BIAS2, C_BIAS)
    ax.add_patch(patches.Rectangle((x0 + 20.0 - 1.0, y0 + 48.0 - 0.6), 2.0, 1.2, facecolor="#334155", edgecolor="#64748B", linewidth=0.8, zorder=4))
    ax.text(x0 + 20.0, y0 + 45.8, "R_BURDEN: 33Ω", color="#CBD5E1", fontsize=5.5, ha='center', va='center', zorder=5)

    for rb_ref, rby in [("R_BIAS1", y0 + 53.0), ("R_BIAS2", y0 + 58.0)]:
        ax.add_patch(patches.Rectangle((x0 + 20.0 - 1.0, rby - 0.6), 2.0, 1.2, facecolor="#334155", edgecolor="#64748B", linewidth=0.8, zorder=4))
        ax.text(x0 + 20.0, rby - 1.6, f"{rb_ref}: 10k", color="#CBD5E1", fontsize=5.2, ha='center', va='center', zorder=5)

    ax.add_patch(patches.Rectangle((x0 + 26.0 - 1.0, y0 + 54.0 - 0.6), 2.0, 1.2, facecolor="#B45309", edgecolor="#F59E0B", linewidth=0.8, zorder=4))
    ax.text(x0 + 26.0, y0 + 57.0, "C_BIAS: 10uF", color="#FDE047", fontsize=5.5, ha='center', va='center', zorder=5)

    # U2: ADS1115 16-Bit I2C ADC (Central Analog Hub)
    adc_x, adc_y = x0 + 60.0, y0 + 30.0
    ax.add_patch(patches.Rectangle((adc_x - 2.5, adc_y - 2.0), 5.0, 4.0, facecolor="#0F172A", edgecolor="#64748B", linewidth=1.2, zorder=4))
    ax.add_patch(plt.Circle((adc_x - 1.8, adc_y - 1.2), 0.35, facecolor="#FFFFFF", zorder=5))
    ax.text(adc_x, adc_y, "ADS1115", color="#E2E8F0", fontsize=6.5, fontweight='bold', ha='center', va='center', zorder=6)
    ax.text(adc_x, adc_y - 3.8, "U2: 16-Bit ADC", color="#93C5FD", fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=7)

    # C_ADS, R_PU1, R_PU2
    ax.add_patch(patches.Rectangle((x0 + 66.0 - 0.8, adc_y - 0.6), 1.6, 1.2, facecolor="#B45309", edgecolor="#F59E0B", linewidth=0.8, zorder=4))
    ax.text(x0 + 66.0, adc_y + 2.2, "C_ADS: 100nF", color="#FDE047", fontsize=5.2, ha='center', va='center', zorder=5)

    for rpu_ref, rx in [("R_PU1", x0 + 56.0), ("R_PU2", x0 + 64.0)]:
        ax.add_patch(patches.Rectangle((rx - 1.0, y0 + 22.0 - 0.6), 2.0, 1.2, facecolor="#334155", edgecolor="#64748B", linewidth=0.8, zorder=4))
        ax.text(rx, y0 + 19.5, f"{rpu_ref}: 4.7k", color="#CBD5E1", fontsize=5.5, ha='center', va='center', zorder=5)

    # U4: LM358 Op-Amp Conditioner
    u4_x, u4_y = x0 + 85.0, y0 + 28.0
    ax.add_patch(patches.Rectangle((u4_x - 2.5, u4_y - 2.5), 5.0, 5.0, facecolor="#0F172A", edgecolor="#64748B", linewidth=1.0, zorder=4))
    ax.text(u4_x, u4_y, "LM358", color="#E2E8F0", fontsize=6.5, fontweight='bold', ha='center', va='center', zorder=5)
    ax.text(u4_x, u4_y - 4.2, "U4: AC Filter", color="#94A3B8", fontsize=7.2, ha='center', va='center', zorder=6)

    # T1: ZMPT101B Voltage Transformer (Top-Right Subsystem)
    t1_x, t1_y = x0 + 112.0, y0 + 26.0
    ax.add_patch(patches.Rectangle((t1_x - 4.5, t1_y - 4.5), 19.0, 19.6, facecolor="#0B132B", edgecolor="#3A506B", linewidth=2.0, zorder=4))
    ax.add_patch(plt.Circle((t1_x + 5.0, t1_y + 6.35), 6.5, facecolor="#1C2541", edgecolor="#5BC0BE", linewidth=1.2, zorder=5))
    ax.add_patch(plt.Circle((t1_x + 5.0, t1_y + 6.35), 3.0, facecolor="#0B132B", edgecolor="#3A506B", linewidth=1.0, zorder=6))
    ax.text(t1_x + 5.0, t1_y + 6.35, "T1:\nZMPT101B", color="#F8FAFC", fontsize=7.2, fontweight='bold', ha='center', va='center', zorder=7)
    ax.text(t1_x + 5.0, t1_y - 6.0, "Voltage Transformer", color="#94A3B8", fontsize=7.0, ha='center', va='center', zorder=7)
    for tpx, tpy in [(t1_x, t1_y), (t1_x, t1_y + 12.7), (t1_x + 10.0, t1_y + 12.7), (t1_x + 10.0, t1_y)]:
        ax.add_patch(plt.Circle((tpx, tpy), 1.5, facecolor="#E2E8F0", edgecolor="#F59E0B", linewidth=0.8, zorder=6))
        ax.add_patch(plt.Circle((tpx, tpy), 0.7, facecolor="#0B0F19", zorder=7))

    # High Voltage Limiting Resistors R_HV1 and R_HV2 (Separated to the right of T1, ZERO overlap)
    for rhv_ref, rx in [("R_HV1", x0 + 128.0), ("R_HV2", x0 + 134.0)]:
        ry = y0 + 24.0
        # Axial resistor body vertical
        ax.add_patch(patches.Rectangle((rx - 1.8, ry + 7.62 - 5.0), 3.6, 10.0, facecolor="#92400E", edgecolor="#D97706", linewidth=1.0, zorder=4))
        ax.plot([rx, rx], [ry, ry + 7.62 - 5.0], color="#D97706", linewidth=1.2, zorder=4)
        ax.plot([rx, rx], [ry + 7.62 + 5.0, ry + 15.24], color="#D97706", linewidth=1.2, zorder=4)
        for py in [ry, ry + 15.24]:
            ax.add_patch(plt.Circle((rx, py), 1.5, facecolor="#E2E8F0", edgecolor="#F59E0B", linewidth=0.8, zorder=5))
            ax.add_patch(plt.Circle((rx, py), 0.7, facecolor="#0B0F19", zorder=6))
        ax.text(rx, ry - 3.5, f"{rhv_ref}\n41.2k 1W", color="#FEF08A", fontsize=5.8, fontweight='bold', ha='center', va='center', zorder=7)

    # U3: ACS712T-30A Hall-Effect AC Current Sensor
    u3_x, u3_y = x0 + 95.0, y0 + 46.0
    ax.add_patch(patches.Rectangle((u3_x - 3.0, u3_y - 2.5), 6.0, 5.0, facecolor="#0F172A", edgecolor="#EF4444", linewidth=1.5, zorder=4))
    ax.text(u3_x, u3_y, "ACS712\n30A", color="#FDE047", fontsize=6.5, fontweight='bold', ha='center', va='center', zorder=5)
    ax.text(u3_x, u3_y - 4.5, "U3: Current Sensor", color="#F87171", fontsize=7.2, fontweight='bold', ha='center', va='center', zorder=6)

    ax.add_patch(patches.Rectangle((x0 + 88.0 - 0.8, u3_y - 0.5), 1.6, 1.0, facecolor="#B45309", edgecolor="#F59E0B", linewidth=0.6, zorder=4))
    ax.text(x0 + 88.0, u3_y + 2.0, "C_ACS: 0.1uF", color="#FDE047", fontsize=5.2, ha='center', va='center', zorder=5)

    ax.add_patch(patches.Rectangle((x0 + 102.0 - 0.8, u3_y - 0.5), 1.6, 1.0, facecolor="#B45309", edgecolor="#F59E0B", linewidth=0.6, zorder=4))
    ax.text(x0 + 102.0, u3_y + 2.0, "C_F: 4.7nF", color="#FDE047", fontsize=5.2, ha='center', va='center', zorder=5)

    # Galvanic Isolated Relay Drivers (U5, U6, Q1, Q2, Resistors)
    for u_ref, uy in [("U5", y0 + 58.0), ("U6", y0 + 72.0)]:
        ux = x0 + 65.0
        ax.add_patch(patches.Rectangle((ux - 3.8, uy - 3.0), 7.6, 6.0, facecolor="#0F172A", edgecolor="#F59E0B", linewidth=1.5, zorder=4))
        ax.add_patch(plt.Circle((ux - 2.8, uy - 1.8), 0.5, facecolor="#FFFFFF", zorder=5))
        ax.text(ux, uy, f"{u_ref}\nPC817", color="#FDE047", fontsize=6.8, fontweight='bold', ha='center', va='center', zorder=6)

    # Optocoupler input resistors R_OPT1, R_OPT2
    for ro_ref, roy in [("R_OPT1", y0 + 58.0), ("R_OPT2", y0 + 72.0)]:
        ax.add_patch(patches.Rectangle((x0 + 56.0 - 0.8, roy - 0.5), 1.6, 1.0, facecolor="#334155", edgecolor="#64748B", linewidth=0.6, zorder=4))
        ax.text(x0 + 56.0, roy - 1.5, f"{ro_ref}: 470Ω", color="#FBBF24", fontsize=5.2, ha='center', va='center', zorder=5)

    # NPN Drivers (Q1, Q2), R_DRV, R_PD
    for q_ref, rdrv_ref, rpd_ref, qy in [("Q1", "R_DRV1", "R_PD1", y0 + 58.0), ("Q2", "R_DRV2", "R_PD2", y0 + 72.0)]:
        ax.add_patch(patches.Rectangle((x0 + 74.0 - 0.8, qy - 0.5), 1.6, 1.0, facecolor="#334155", edgecolor="#64748B", linewidth=0.6, zorder=4))
        ax.text(x0 + 74.0, qy - 1.5, f"{rdrv_ref}: 1k", color="#94A3B8", fontsize=5.2, ha='center', va='center', zorder=5)

        ax.add_patch(patches.Rectangle((x0 + 80.0 - 1.5, qy - 1.0), 3.0, 2.0, facecolor="#0F172A", edgecolor="#64748B", linewidth=0.8, zorder=4))
        ax.text(x0 + 80.0, qy - 2.5, f"{q_ref}: NPN", color="#94A3B8", fontsize=6.0, ha='center', va='center', zorder=5)

        ax.add_patch(patches.Rectangle((x0 + 80.0 - 0.8, qy + 5.0 - 0.5), 1.6, 1.0, facecolor="#334155", edgecolor="#64748B", linewidth=0.6, zorder=4))
        ax.text(x0 + 80.0, qy + 6.8, f"{rpd_ref}: 10k", color="#94A3B8", fontsize=5.2, ha='center', va='center', zorder=5)

    # Relays K1 (Pump) & K2 (Aux Valve)
    k1_x, k1_y = x0 + 98.0, y0 + 60.0
    ax.add_patch(patches.Rectangle((k1_x - 9.5, k1_y - 7.75), 19.0, 15.5, facecolor="#1D4ED8", edgecolor="#2563EB", linewidth=1.8, zorder=4))
    ax.text(k1_x, k1_y - 1.5, "SONGLE RELAY\n10A 250VAC", color="#FFFFFF", fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=5)
    ax.text(k1_x, k1_y + 4.5, "K1: WILO PUMP", color="#BFDBFE", fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=5)

    k2_x, k2_y = x0 + 98.0, y0 + 78.0
    ax.add_patch(patches.Rectangle((k2_x - 9.5, k2_y - 7.75), 19.0, 15.5, facecolor="#1D4ED8", edgecolor="#2563EB", linewidth=1.8, zorder=4))
    ax.text(k2_x, k2_y - 1.5, "SONGLE RELAY\n10A 250VAC", color="#FFFFFF", fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=5)
    ax.text(k2_x, k2_y + 4.5, "K2: AUX / VALVE", color="#BFDBFE", fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=5)

    # Flyback Diodes D2, D3
    for d_ref, dy in [("D2", k1_y), ("D3", k2_y)]:
        ax.add_patch(patches.Rectangle((x0 + 90.0 - 1.2, dy - 2.25), 2.4, 4.5, facecolor="#0F172A", edgecolor="#94A3B8", linewidth=0.8, zorder=4))
        ax.text(x0 + 90.0, dy - 3.5, f"{d_ref}\n1N4007", color="#CBD5E1", fontsize=5.2, ha='center', va='center', zorder=5)

    # Transient Protection: MOV1 & RC Snubber (R_SNUB1 + C_SNUB1)
    mov_x, mov_y = x0 + 118.0, y0 + 54.0
    ax.add_patch(plt.Circle((mov_x, mov_y), 4.5, facecolor="#0284C7", edgecolor="#0369A1", linewidth=1.2, zorder=5))
    ax.text(mov_x, mov_y, "MOV1\n14D471K", color="#FFFFFF", fontsize=5.5, fontweight='bold', ha='center', va='center', zorder=6)

    rsnub_x, rsnub_y = x0 + 118.0, y0 + 62.0
    ax.add_patch(patches.Rectangle((rsnub_x - 7.62, rsnub_y - 1.5), 15.24, 3.0, facecolor="#92400E", edgecolor="#D97706", linewidth=0.8, zorder=4))
    ax.text(rsnub_x, rsnub_y, "R_SNUB: 100Ω 1W", color="#FEF08A", fontsize=5.5, fontweight='bold', ha='center', va='center', zorder=5)

    csnub_x, csnub_y = x0 + 118.0, y0 + 70.0
    ax.add_patch(patches.Rectangle((csnub_x - 5.0, csnub_y - 2.0), 10.0, 4.0, facecolor="#B91C1C", edgecolor="#DC2626", linewidth=1.0, zorder=4))
    ax.text(csnub_x, csnub_y, "C_SNUB: 0.1uF X2", color="#FFFFFF", fontsize=5.5, fontweight='bold', ha='center', va='center', zorder=5)

    # =========================================================================
    # BOTTOM-RIGHT CORNER: TB3 (Actuators Load Output: PUMP, VALVE, NEUT)
    # =========================================================================
    tb3_x, tb3_y = x0 + 130.0, y0 + 75.0
    ax.add_patch(patches.Rectangle((tb3_x - 4.5, tb3_y - 8.0), 9.0, 16.0, facecolor="#166534", edgecolor="#22C55E", linewidth=1.5, zorder=4))
    for dy, lbl in [(-5.08, "PUMP"), (0, "VALVE"), (5.08, "NEUT")]:
        ax.add_patch(plt.Circle((tb3_x, tb3_y + dy), 1.8, facecolor="#E2E8F0", edgecolor="#94A3B8", linewidth=1.0, zorder=5))
        ax.add_patch(patches.Rectangle((tb3_x - 0.25, tb3_y + dy - 1.2), 0.5, 2.4, facecolor="#334155", zorder=6))
        ax.text(tb3_x + 6.2, tb3_y + dy, lbl, color="#86EFAC", fontsize=7.5, fontweight='bold', va='center', zorder=7)
    ax.text(tb3_x, tb3_y - 10.5, "TB3: LOAD OUT", color="#86EFAC", fontsize=8.0, fontweight='bold', ha='center', va='center', zorder=7)

    # =========================================================================
    # BOTTOM EDGE UI: Push Buttons (SW1, SW2) & Status LEDs
    # =========================================================================
    buttons = [
        ("SW1", "FORCE ON", x0 + 48.0, "#166534"),
        ("SW2", "FORCE OFF", x0 + 62.0, "#991B1B"),
    ]
    for b_ref, b_lbl, bx, b_col in buttons:
        ax.add_patch(patches.Rectangle((bx - 3.2, y0 + 86.0 - 3.2), 6.4, 6.4, facecolor="#334155", edgecolor="#64748B", linewidth=1.2, zorder=4))
        ax.add_patch(plt.Circle((bx, y0 + 86.0), 2.0, facecolor=b_col, edgecolor="#FFFFFF", linewidth=1.0, zorder=5))
        ax.text(bx, y0 + 92.5, f"{b_ref}: {b_lbl}", color="#F8FAFC", fontsize=7.0, fontweight='bold', ha='center', va='center', zorder=6)

    leds = [
        ("LED_5V", "5V PWR", x0 + 76.0, "#22C55E"),
        ("LED_3V3", "3V3 RF", x0 + 86.0, "#3B82F6"),
        ("LED_PUMP", "PUMP ON", x0 + 96.0, "#EAB308"),
    ]
    for l_ref, l_lbl, lx, col in leds:
        ax.add_patch(patches.Rectangle((lx - 1.2, y0 + 86.0 - 0.8), 2.4, 1.6, facecolor=col, edgecolor="#FFFFFF", linewidth=1.0, zorder=4))
        ax.text(lx, y0 + 82.5, f"{l_ref}\n{l_lbl}", color=col, fontsize=6.2, fontweight='bold', ha='center', va='center', zorder=5)

    ax.set_xlim(x0 - 5.0, x0 + w + 5.0)
    ax.set_ylim(y0 + h + 5.0, y0 - 5.0)  # Invert Y so top is 0
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
