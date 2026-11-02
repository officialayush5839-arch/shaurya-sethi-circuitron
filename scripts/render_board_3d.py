"""Generate a realistic 3D perspective raytraced-style render of the Wilo Receiver PCB."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from pathlib import Path


def create_box(x, y, z, dx, dy, dz, color, alpha=1.0, edgecolor=None):
    """Generate 6 faces for a 3D box."""
    faces = [
        # bottom
        [[x, y, z], [x + dx, y, z], [x + dx, y + dy, z], [x, y + dy, z]],
        # top
        [[x, y, z + dz], [x + dx, y, z + dz], [x + dx, y + dy, z + dz], [x, y + dy, z + dz]],
        # front
        [[x, y, z], [x + dx, y, z], [x + dx, y, z + dz], [x, y, z + dz]],
        # back
        [[x, y + dy, z], [x + dx, y + dy, z], [x + dx, y + dy, z + dz], [x, y + dy, z + dz]],
        # left
        [[x, y, z], [x, y + dy, z], [x, y + dy, z + dz], [x, y, z + dz]],
        # right
        [[x + dx, y, z], [x + dx, y + dy, z], [x + dx, y + dy, z + dz], [x + dx, y, z + dz]],
    ]
    return Poly3DCollection(faces, facecolors=color, linewidths=0.5, edgecolors=edgecolor or color, alpha=alpha)


def render_3d_pcb(output_png: Path):
    fig = plt.figure(figsize=(18, 12), dpi=200)
    fig.patch.set_facecolor('#0B0F12')
    ax = fig.add_subplot(projection='3d')
    ax.set_facecolor('#0B0F12')

    # Dimensions in mm
    w, h, pcb_th = 120.0, 85.0, 1.6

    # 1. Main PCB Slab (Dark Green soldermask)
    pcb = create_box(0, 0, 0, w, h, pcb_th, '#1A4D2E', alpha=0.98, edgecolor='#2D6A4F')
    ax.add_collection3d(pcb)

    # 2. Creepage Slot Cutouts (Black through-slots)
    slot_x = 67.0
    for sy_start, sy_len in [(8.0, 32.0), (66.0, 12.0)]:
        slot = create_box(slot_x - 0.8, sy_start, -0.1, 1.6, sy_len, pcb_th + 0.2, '#0B0F12', alpha=1.0, edgecolor='#E63946')
        ax.add_collection3d(slot)

    # 3. Mounting Holes (M2.5)
    for hx, hy in [(4.0, 4.0), (62.0, 4.0), (4.0, 27.0), (62.0, 27.0)]:
        hole = create_box(hx - 1.35, hy - 1.35, -0.1, 2.7, 2.7, pcb_th + 0.2, '#0B0F12', alpha=1.0, edgecolor='#C0C0C0')
        ax.add_collection3d(hole)

    # =========================================================================
    # ZONE 1 COMPONENTS (DC LOGIC)
    # =========================================================================

    # J1: Raspberry Pi Zero 2W 40-Pin Header (Black 8.5mm tall socket)
    j1 = create_box(8.5 - 2.5, 10.5 - 2.5, pcb_th, 50.8, 5.0, 8.5, '#1C1C1C', edgecolor='#333333')
    ax.add_collection3d(j1)
    for c in range(0, 20, 2):
        gold_pad = create_box(8.5 + c * 2.54, 10.5, pcb_th + 8.5, 1.2, 1.2, 0.1, '#FFD166', edgecolor='#B7950B')
        ax.add_collection3d(gold_pad)
    ax.text(8.5 + 24.0, 10.5, pcb_th + 9.5, "J1: RPi Zero 2W", color='#FFD166', fontsize=9, fontweight='bold', ha='center')

    # J_CT: 3.5mm CT Clamp Audio Jack
    j_ct = create_box(6.0 - 4.5, 26.0 - 4.0, pcb_th, 9.0, 8.0, 5.0, '#212529', edgecolor='#78909C')
    ax.add_collection3d(j_ct)
    ax.text(6.0, 26.0, pcb_th + 6.0, "J_CT: 3.5mm CT", color='#90CAF9', fontsize=7, fontweight='bold', ha='center')

    # U_LORA: SX1278 Ra-02 LoRa Module (16x16x3.2mm)
    lora_pcb = create_box(20.0 - 8.0, 42.0 - 8.0, pcb_th, 16.0, 16.0, 0.8, '#263238', edgecolor='#37474F')
    ax.add_collection3d(lora_pcb)
    lora_shield = create_box(20.0 - 6.5, 42.0 - 6.0, pcb_th + 0.8, 13.0, 11.0, 2.2, '#B0BEC5', edgecolor='#CFD8DC')
    ax.add_collection3d(lora_shield)
    ax.text(20.0, 42.0, pcb_th + 3.5, "SX1278 Ra-02\n433MHz", color='#263238', fontsize=8, fontweight='bold', ha='center')

    # J_SMA: SMA 50-Ohm Connector (Gold Plated)
    sma = create_box(4.0 - 3.5, 42.0 - 3.5, pcb_th, 7.0, 7.0, 6.0, '#B45309', edgecolor='#F59E0B')
    ax.add_collection3d(sma)
    ax.text(4.0, 42.0, pcb_th + 7.0, "SMA 50Ω", color='#F59E0B', fontsize=7, fontweight='bold', ha='center')

    # U2: ADS1115 16-Bit ADC (MSOP-10, 1.1mm tall)
    u2 = create_box(48.0 - 2.0, 36.0 - 1.5, pcb_th, 4.0, 3.0, 1.2, '#1A1A1A', edgecolor='#424242')
    ax.add_collection3d(u2)
    ax.text(48.0, 36.0, pcb_th + 2.0, "U2: ADS1115", color='#A8DADC', fontsize=8, fontweight='bold', ha='center')

    # TB_EXP: ADC Expansion Terminal Block (A2, A3)
    tb_exp = create_box(54.0 - 4.5, 19.0 - 3.5, pcb_th, 9.0, 7.0, 8.5, '#2E7D32', edgecolor='#4CAF50')
    ax.add_collection3d(tb_exp)
    ax.text(54.0, 19.0, pcb_th + 9.5, "TB_EXP: A2/A3", color='#81C784', fontsize=7, fontweight='bold', ha='center')

    # J_USBC: USB Type-C Receptacle 5V In (Metallic 3.5mm tall)
    j_usbc = create_box(5.5 - 4.5, 68.0 - 4.5, pcb_th, 9.0, 9.0, 3.5, '#546E7A', edgecolor='#B0BEC5')
    ax.add_collection3d(j_usbc)
    ax.text(5.5, 68.0, pcb_th + 4.5, "USB-C 5V MAIN PWR", color='#90CAF9', fontsize=7.5, fontweight='bold', ha='center')

    # U1: AMS1117-3.3V LDO (SOT-223)
    u1 = create_box(24.0 - 3.2, 68.0 - 1.8, pcb_th, 6.5, 3.5, 1.8, '#1E1E1E', edgecolor='#616161')
    ax.add_collection3d(u1)
    ax.text(24.0, 68.0, pcb_th + 2.6, "AMS1117", color='#81C784', fontsize=7, fontweight='bold', ha='center')

    # Push Buttons SW1 (Force ON) and SW2 (Force OFF)
    for bx, col, lbl in [(42.0, '#2E7D32', 'FORCE ON'), (56.0, '#C62828', 'FORCE OFF')]:
        btn_body = create_box(bx - 3.0, 72.0 - 3.0, pcb_th, 6.0, 6.0, 3.5, '#455A64', edgecolor='#78909C')
        ax.add_collection3d(btn_body)
        btn_plunger = create_box(bx - 1.5, 72.0 - 1.5, pcb_th + 3.5, 3.0, 3.0, 2.5, col, edgecolor='#FFFFFF')
        ax.add_collection3d(btn_plunger)
        ax.text(bx, 72.0, pcb_th + 7.0, lbl, color=col, fontsize=8, fontweight='bold', ha='center')

    # Status LEDs (0805)
    for lx, col, lbl in [(12.0, '#22C55E', '5V'), (20.0, '#3B82F6', '3V3'), (36.0, '#EAB308', 'PUMP')]:
        led = create_box(lx - 1.0, 56.0 - 0.6, pcb_th, 2.0, 1.2, 0.8, col, edgecolor='#FFFFFF')
        ax.add_collection3d(led)

    # Optocouplers U5, U6 (PC817 DIP-4 straddling boundary)
    for uy, lbl in [(48.0, 'U5: Opto1'), (60.0, 'U6: Opto2')]:
        opto = create_box(slot_x - 3.8, uy - 2.5, pcb_th, 7.6, 5.0, 3.5, '#212121', edgecolor='#FFB703')
        ax.add_collection3d(opto)
        ax.text(slot_x, uy, pcb_th + 4.2, "PC817", color='#FFD166', fontsize=7, fontweight='bold', ha='center')

    # =========================================================================
    # ZONE 2 COMPONENTS (230V AC MAINS & POWER)
    # =========================================================================

    # TB2: 230V AC Mains In (Red 10mm tall screw terminal)
    tb2 = create_box(110.0 - 5.5, 12.0 - 4.5, pcb_th, 11.0, 9.0, 10.0, '#B71C1C', edgecolor='#EF5350')
    ax.add_collection3d(tb2)
    ax.text(110.0, 12.0, pcb_th + 11.5, "TB2: AC SENSE (ZMPT101B)", color='#EF5350', fontsize=7.5, fontweight='bold', ha='center')

    # T1: ZMPT101B Potential Transformer (18x18x12mm Blue-Black block)
    t1 = create_box(86.0 - 9.0, 18.0 - 9.0, pcb_th, 18.0, 18.0, 12.0, '#0D1B2A', edgecolor='#415A77')
    ax.add_collection3d(t1)
    coil = create_box(86.0 - 6.0, 18.0 - 6.0, pcb_th + 12.0, 12.0, 12.0, 1.5, '#415A77', edgecolor='#778DA9')
    ax.add_collection3d(coil)
    ax.text(86.0, 18.0, pcb_th + 15.0, "T1: ZMPT101B\nVoltage Sensor", color='#E0E1DD', fontsize=8, fontweight='bold', ha='center')

    # High Voltage Resistors (R_HV1, R_HV2, 1W Cylindrical)
    for rx in [80.0, 102.0]:
        rhv = create_box(rx - 7.5, 30.0 - 1.8, pcb_th, 15.0, 3.6, 3.6, '#D4A373', edgecolor='#BC6C25')
        ax.add_collection3d(rhv)

    # U3: ACS712T-30A Hall-Effect Current Sensor (SOIC-8)
    u3 = create_box(104.0 - 3.0, 40.0 - 2.5, pcb_th, 6.0, 5.0, 1.8, '#1A1A1A', edgecolor='#E63946')
    ax.add_collection3d(u3)
    ax.text(104.0, 40.0, pcb_th + 2.8, "U3: ACS712-30A\nCurrent Sensor", color='#FFD166', fontsize=8, fontweight='bold', ha='center')

    # U4: LM358 Condition Op-Amp (SOIC-8)
    u4 = create_box(78.0 - 2.5, 40.0 - 2.5, pcb_th, 5.0, 5.0, 1.8, '#1A1A1A', edgecolor='#616161')
    ax.add_collection3d(u4)
    ax.text(78.0, 40.0, pcb_th + 2.8, "LM358", color='#CCCCCC', fontsize=7, ha='center')

    # K1 & K2: Songle SRD Power Relays (19x15.5x15.5mm High-Gloss Blue Boxes)
    k1 = create_box(80.0, 56.0 - 7.75, pcb_th, 19.0, 15.5, 15.5, '#1E88E5', edgecolor='#1565C0')
    ax.add_collection3d(k1)
    ax.text(80.0 + 9.5, 56.0, pcb_th + 16.5, "K1: SONGLE RELAY\n(WILO PUMP 10A)", color='#FFFFFF', fontsize=8, fontweight='bold', ha='center')

    # MOV1 Varistor (14D471K Blue Disc) & RC Snubber
    mov1 = create_box(102.0 - 4.5, 52.0 - 2.0, pcb_th, 9.0, 4.0, 11.0, '#0077B6', edgecolor='#03045E')
    ax.add_collection3d(mov1)
    ax.text(102.0, 52.0, pcb_th + 12.0, "MOV1: 14D471K", color='#90CAF9', fontsize=6, fontweight='bold', ha='center')

    c_snub = create_box(106.0 - 4.5, 46.0 - 2.0, pcb_th, 9.0, 4.0, 8.0, '#D90429', edgecolor='#EF233C')
    ax.add_collection3d(c_snub)
    ax.text(106.0, 46.0, pcb_th + 9.0, "0.1uF X2", color='#FFFFFF', fontsize=5.5, ha='center')

    k2 = create_box(80.0, 73.0 - 7.75, pcb_th, 19.0, 15.5, 15.5, '#1E88E5', edgecolor='#1565C0')
    ax.add_collection3d(k2)
    ax.text(80.0 + 9.5, 73.0, pcb_th + 16.5, "K2: SONGLE RELAY\n(VALVE 10A)", color='#FFFFFF', fontsize=8, fontweight='bold', ha='center')

    # TB3: 3-Pin Actuator Output Screw Terminal (Green 10mm tall)
    tb3 = create_box(112.0 - 4.5, 64.0 - 8.0, pcb_th, 9.0, 16.0, 10.0, '#2E7D32', edgecolor='#4CAF50')
    ax.add_collection3d(tb3)
    ax.text(112.0, 64.0, pcb_th + 11.5, "TB3:\nPUMP / VALVE\nOUTPUT", color='#A5D6A7', fontsize=8, fontweight='bold', ha='center')

    # Labels and Metadata
    ax.text(60.0, 83.0, pcb_th + 0.2, "WILO WATER PUMP AUTOMATION — RECEIVER HAT (120mm x 85mm)", color='#A8DADC', fontsize=11, fontweight='bold', ha='center')

    # Set 3D View Angle & Limits
    ax.set_xlim(-5, w + 10)
    ax.set_ylim(-5, h + 10)
    ax.set_zlim(0, 30)

    # Isometric viewing perspective: 35 degrees elevation, -60 degrees azimuth
    ax.view_init(elev=38, azim=-55)

    ax.axis('off')
    plt.tight_layout()
    output_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_png, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Generated 3D PCB render: {output_png}")


if __name__ == "__main__":
    out_file = Path("output/wilo_receiver/wilo_receiver_3d_final.png")
    render_3d_pcb(out_file)
