"""Wilo Water Pump Automation Receiver Station Circuit Definition.

Implements the complete SKiDL circuit model for the Raspberry Pi Zero 2W HAT,
integrating:
- SX1278 433MHz LoRa transceiver (Ra-02 footprint) with 10uF + 0.1uF decoupling
- ADS1115 16-bit I2C ADC with 100nF decoupling and expansion terminal for A2/A3
- ACS712T-30A AC current sensor with 4.7nF filter & 0.1uF VCC decoupling
- SCT-013-000 3.5mm CT clamp interface with 33 ohm burden and DC bias network
- ZMPT101B AC voltage transformer & op-amp conditioning circuit with 82k 1W HV resistors
- Dual optocoupled 10A relays (Pump & Aux Valve) with PC817, series resistors & NPN drivers
- Mains transient protection: MOV (14D471K) and RC Snubber (100 ohm 1W + 0.1uF 630V X2)
- USB Type-C 5V power supply input with dual 5.1k CC pull-down resistors
- Tactile push buttons (Force ON / Force OFF) & status LEDs with series current-limiting resistors
- Dedicated 3.3V LDO regulator and dual-zone isolation
"""
import os
import sys

# Configure KiCad library search paths before skidl import to suppress fallback warnings
_KICAD_SYMBOLS = "E:/kicad/share/kicad/symbols"
if os.path.exists(_KICAD_SYMBOLS):
    for var in [
        "KICAD10_SYMBOL_DIR",
        "KICAD_SYMBOL_DIR",
        "KICAD6_SYMBOL_DIR",
        "KICAD7_SYMBOL_DIR",
        "KICAD8_SYMBOL_DIR",
        "KICAD9_SYMBOL_DIR",
    ]:
        os.environ.setdefault(var, _KICAD_SYMBOLS)

from skidl import (
    Circuit,
    Net,
    Part,
    Pin,
    POWER,
    set_default_tool,
    SKIDL,
    KICAD,
    lib_search_paths,
)

if os.path.exists(_KICAD_SYMBOLS) and _KICAD_SYMBOLS not in lib_search_paths[KICAD]:
    lib_search_paths[KICAD].append(_KICAD_SYMBOLS)


def _make_part(
    circuit: Circuit,
    name: str,
    ref_prefix: str,
    pins: list[tuple[int | str, str, str]],
    footprint: str,
    value: str = "",
) -> Part:
    """Helper to create a deterministic SKiDL Part with explicit pins and footprint.
    
    Args:
        circuit: Circuit instance to add part to.
        name: Part component name.
        ref_prefix: Reference designator prefix (e.g. 'R', 'C', 'U').
        pins: List of (num, pin_name, pin_type) tuples.
        footprint: KiCad footprint identifier.
        value: Component value or designation.
    """
    pin_objs = [Pin(num=str(num), name=pin_name, func=pin_type) for num, pin_name, pin_type in pins]
    p = Part(
        name=name,
        tool=SKIDL,
        ref_prefix=ref_prefix,
        footprint=footprint,
        value=value or name,
        circuit=circuit,
        pins=pin_objs,
    )
    return p


def create_wilo_receiver_circuit() -> Circuit:
    """Create and return the complete Wilo Receiver Station SKiDL circuit."""
    c = Circuit()

    # =========================================================================
    # 1. POWER NETS & POWER RAILS
    # =========================================================================
    vcc_5v = Net("+5V", circuit=c)
    vcc_5v.drive = POWER

    vcc_3v3_rpi = Net("+3V3_RPI", circuit=c)
    vcc_3v3_rpi.drive = POWER

    vcc_3v3_lora = Net("+3V3_LORA", circuit=c)
    vcc_3v3_lora.drive = POWER

    gnd = Net("GND", circuit=c)
    gnd.drive = POWER
    gnd.do_erc = False

    ac_l_in = Net("AC_L_IN", circuit=c)
    ac_n_in = Net("AC_N_IN", circuit=c)
    ac_l_pump = Net("AC_L_PUMP", circuit=c)
    ac_pump_out = Net("AC_PUMP_OUT", circuit=c)
    ac_valve_out = Net("AC_VALVE_OUT", circuit=c)

    # Signal Nets
    i2c_sda = Net("I2C_SDA", circuit=c)
    i2c_scl = Net("I2C_SCL", circuit=c)
    spi_mosi = Net("SPI0_MOSI", circuit=c)
    spi_miso = Net("SPI0_MISO", circuit=c)
    spi_sclk = Net("SPI0_SCLK", circuit=c)
    spi_ce0 = Net("SPI0_CE0", circuit=c)
    lora_rst = Net("LORA_RST", circuit=c)
    lora_dio0 = Net("LORA_DIO0", circuit=c)
    relay1_ctrl = Net("RELAY1_CTRL", circuit=c)
    relay2_ctrl = Net("RELAY2_CTRL", circuit=c)
    btn_force_on = Net("BTN_FORCE_ON", circuit=c)
    btn_force_off = Net("BTN_FORCE_OFF", circuit=c)
    led_pump_run = Net("LED_PUMP_RUN", circuit=c)
    led_drive = Net("LED_DRIVE", circuit=c)
    led_5v_mid = Net("LED_5V_MID", circuit=c)
    led_3v3_mid = Net("LED_3V3_MID", circuit=c)
    opt1_in = Net("OPT1_IN", circuit=c)
    opt2_in = Net("OPT2_IN", circuit=c)
    q1_base = Net("Q1_BASE", circuit=c)
    q2_base = Net("Q2_BASE", circuit=c)
    adc_a0 = Net("ADC_A0", circuit=c)
    adc_a1 = Net("ADC_A1", circuit=c)
    adc_a2 = Net("ADC_A2", circuit=c)
    adc_a3 = Net("ADC_A3", circuit=c)
    ct_bias = Net("CT_BIAS", circuit=c)
    snub1_mid = Net("SNUB1_MID", circuit=c)

    # =========================================================================
    # 2. RASPBERRY PI ZERO 2W 40-PIN GPIO HEADER (J1)
    # =========================================================================
    j1_pins = [(i, f"Pin_{i}", Pin.types.PASSIVE) for i in range(1, 41)]
    j1 = _make_part(c, 
        name="Conn_02x20_Odd_Even",
        ref_prefix="J",
        pins=j1_pins,
        footprint="Connector_PinSocket_2.54mm:PinSocket_2x20_P2.54mm_Vertical",
        value="RPi_Zero_2W_Header",
    )
    j1.ref = "J1"

    # Connect RPi Header Pins per specification
    j1["1"] += vcc_3v3_rpi
    j1["2"] += vcc_5v
    j1["3"] += i2c_sda
    j1["4"] += vcc_5v
    j1["5"] += i2c_scl
    j1["6"] += gnd
    j1["9"] += gnd
    j1["11"] += relay1_ctrl
    j1["13"] += relay2_ctrl
    j1["14"] += gnd
    j1["15"] += btn_force_on
    j1["17"] += vcc_3v3_rpi
    j1["18"] += lora_dio0
    j1["19"] += spi_mosi
    j1["20"] += gnd
    j1["21"] += spi_miso
    j1["22"] += lora_rst
    j1["23"] += spi_sclk
    j1["24"] += spi_ce0
    j1["25"] += gnd
    j1["29"] += btn_force_off
    j1["30"] += gnd
    j1["31"] += led_pump_run
    j1["34"] += gnd
    j1["39"] += gnd

    # Mark unused RPi header pins with do_erc=False
    for unused_pin in ["7", "8", "10", "12", "16", "26", "27", "28", "32", "33", "35", "36", "37", "38", "40"]:
        j1[unused_pin].do_erc = False

    # =========================================================================
    # 3. POWER INPUT: USB TYPE-C RECEPTACLE (J_USBC) & 3.3V LDO (U1)
    # =========================================================================
    # USB Type-C Receptacle (Standard 16-pin power sinking)
    usbc_pins = [
        ("A1", "GND", Pin.types.PWRIN),
        ("A4", "VBUS", Pin.types.PWRIN),
        ("A5", "CC1", Pin.types.PASSIVE),
        ("A6", "DP1", Pin.types.PASSIVE),
        ("A7", "DN1", Pin.types.PASSIVE),
        ("A8", "SBU1", Pin.types.PASSIVE),
        ("A9", "VBUS", Pin.types.PWRIN),
        ("A12", "GND", Pin.types.PWRIN),
        ("B1", "GND", Pin.types.PWRIN),
        ("B4", "VBUS", Pin.types.PWRIN),
        ("B5", "CC2", Pin.types.PASSIVE),
        ("B6", "DP2", Pin.types.PASSIVE),
        ("B7", "DN2", Pin.types.PASSIVE),
        ("B8", "SBU2", Pin.types.PASSIVE),
        ("B9", "VBUS", Pin.types.PWRIN),
        ("B12", "GND", Pin.types.PWRIN),
        ("SH", "SHIELD", Pin.types.PWRIN),
    ]
    j_usbc = _make_part(c,
        name="USB_C_Receptacle_USB2.0_16P",
        ref_prefix="J",
        pins=usbc_pins,
        footprint="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
        value="USB_C_5V_IN",
    )
    j_usbc.ref = "J_USBC"
    j_usbc["A4"] += vcc_5v
    j_usbc["A9"] += vcc_5v
    j_usbc["B4"] += vcc_5v
    j_usbc["B9"] += vcc_5v
    j_usbc["A1"] += gnd
    j_usbc["A12"] += gnd
    j_usbc["B1"] += gnd
    j_usbc["B12"] += gnd
    j_usbc["SH"] += gnd

    # USB-C CC Pull-Down Resistors (5.1k each for 5V sinking up to 3A)
    r_cc1 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_SMD:R_0805_2012Metric", "5.1k")
    r_cc1.ref = "R_CC1"
    r_cc1["1"] += j_usbc["A5"]
    r_cc1["2"] += gnd

    r_cc2 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_SMD:R_0805_2012Metric", "5.1k")
    r_cc2.ref = "R_CC2"
    r_cc2["1"] += j_usbc["B5"]
    r_cc2["2"] += gnd

    for nc_pin in ["A6", "A7", "A8", "B6", "B7", "B8"]:
        j_usbc[nc_pin].do_erc = False

    # AMS1117-3.3 LDO (provides clean, isolated 3.3V power for LoRa radio)
    u1_pins = [("1", "GND", Pin.types.PWRIN), ("2", "VOUT", Pin.types.PWROUT), ("3", "VIN", Pin.types.PWRIN)]
    u1 = _make_part(c, 
        name="AMS1117-3.3",
        ref_prefix="U",
        pins=u1_pins,
        footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
        value="AMS1117-3.3",
    )
    u1.ref = "U1"
    u1["1"] += gnd
    u1["2"] += vcc_3v3_lora
    u1["3"] += vcc_5v

    # LDO Decoupling Capacitors
    c1 = _make_part(c, "C", "C", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Capacitor_SMD:C_0805_2012Metric", "10uF")
    c1.ref = "C1"
    c1["1"] += vcc_5v
    c1["2"] += gnd

    c2 = _make_part(c, "C", "C", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Capacitor_SMD:C_0805_2012Metric", "22uF")
    c2.ref = "C2"
    c2["1"] += vcc_3v3_lora
    c2["2"] += gnd

    # =========================================================================
    # 4. SX1278 433MHz LoRa TRANSCEIVER (U_LORA), FILTERING CAPS & SMA ANTENNA
    # =========================================================================
    lora_pins = [
        ("1", "GND", Pin.types.PWRIN),
        ("2", "DIO1", Pin.types.OUTPUT),
        ("3", "DIO2", Pin.types.OUTPUT),
        ("4", "DIO3", Pin.types.OUTPUT),
        ("5", "DIO4", Pin.types.OUTPUT),
        ("6", "RESET", Pin.types.INPUT),
        ("7", "DIO0", Pin.types.OUTPUT),
        ("8", "GND", Pin.types.PWRIN),
        ("9", "VCC", Pin.types.PWRIN),
        ("10", "SCK", Pin.types.INPUT),
        ("11", "MISO", Pin.types.OUTPUT),
        ("12", "MOSI", Pin.types.INPUT),
        ("13", "NSS", Pin.types.INPUT),
        ("14", "DIO5", Pin.types.OUTPUT),
        ("15", "ANT", Pin.types.PASSIVE),
        ("16", "GND", Pin.types.PWRIN),
    ]
    u_lora = _make_part(c, name="Ra-02_SX1278", ref_prefix="U", pins=lora_pins, footprint="RF_Module:Ai-Thinker-Ra-01-LoRa", value="SX1278_433MHz")
    u_lora.ref = "U_LORA"
    u_lora["1"] += gnd
    u_lora["2"].do_erc = False
    u_lora["3"].do_erc = False
    u_lora["4"].do_erc = False
    u_lora["5"].do_erc = False
    u_lora["6"] += lora_rst
    u_lora["7"] += lora_dio0
    u_lora["8"] += gnd
    u_lora["9"] += vcc_3v3_lora
    u_lora["10"] += spi_sclk
    u_lora["11"] += spi_miso
    u_lora["12"] += spi_mosi
    u_lora["13"] += spi_ce0
    u_lora["14"].do_erc = False
    u_lora["16"] += gnd

    # LoRa Module Dedicated Filtering Capacitors (10uF electrolytic + 0.1uF ceramic right at VCC/GND pins)
    c_lora1 = _make_part(c, "CP", "C", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Capacitor_SMD:C_0805_2012Metric", "10uF")
    c_lora1.ref = "C_LORA1"
    c_lora1["1"] += vcc_3v3_lora
    c_lora1["2"] += gnd

    c_lora2 = _make_part(c, "C", "C", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Capacitor_SMD:C_0805_2012Metric", "0.1uF")
    c_lora2.ref = "C_LORA2"
    c_lora2["1"] += vcc_3v3_lora
    c_lora2["2"] += gnd

    rf_ant = Net("RF_ANT", circuit=c)
    u_lora["15"] += rf_ant

    j_sma_pins = [("1", "In", Pin.types.PASSIVE), ("2", "Ext", Pin.types.PWRIN)]
    j_sma = _make_part(c, name="SMA_Connector", ref_prefix="J", pins=j_sma_pins, footprint="Connector_Coaxial:SMA_Amphenol_132134-10_Vertical", value="SMA_50_Ohm")
    j_sma.ref = "J_SMA"
    j_sma["1"] += rf_ant
    j_sma["2"] += gnd

    # =========================================================================
    # 5. ADS1115 16-BIT I2C ADC (U2), DECOUPLING & EXPANSION TERMINAL (TB_EXP)
    # =========================================================================
    ads_pins = [
        ("1", "ADDR", Pin.types.INPUT),
        ("2", "ALERT", Pin.types.OUTPUT),
        ("3", "GND", Pin.types.PWRIN),
        ("4", "AIN0", Pin.types.INPUT),
        ("5", "AIN1", Pin.types.INPUT),
        ("6", "AIN2", Pin.types.INPUT),
        ("7", "AIN3", Pin.types.INPUT),
        ("8", "VDD", Pin.types.PWRIN),
        ("9", "SDA", Pin.types.BIDIR),
        ("10", "SCL", Pin.types.INPUT),
    ]
    u2 = _make_part(c, name="ADS1115IDGSR", ref_prefix="U", pins=ads_pins, footprint="Package_SO:MSOP-10_3x3mm_P0.5mm", value="ADS1115")
    u2.ref = "U2"
    u2["1"] += gnd         # Hardware address 0x48
    u2["2"].do_erc = False
    u2["3"] += gnd
    u2["4"] += adc_a0      # Channel 0: Current sensor output (0-5V)
    u2["5"] += adc_a1      # Channel 1: Voltage sensor output (0-5V)
    u2["6"] += adc_a2      # Channel 2: Expansion terminal A2
    u2["7"] += adc_a3      # Channel 3: Expansion terminal A3
    u2["8"] += vcc_5v      # Full 0-5V dynamic analog range
    u2["9"] += i2c_sda
    u2["10"] += i2c_scl

    # ADS1115 Decoupling Capacitor (100nF near VDD pin)
    c_ads = _make_part(c, "C", "C", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Capacitor_SMD:C_0805_2012Metric", "100nF")
    c_ads.ref = "C_ADS"
    c_ads["1"] += vcc_5v
    c_ads["2"] += gnd

    # I2C Pull-Up Resistors (4.7k to 3.3V)
    r_pu1 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_SMD:R_0805_2012Metric", "4.7k")
    r_pu1.ref = "R_PU1"
    r_pu1["1"] += i2c_sda
    r_pu1["2"] += vcc_3v3_rpi

    r_pu2 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_SMD:R_0805_2012Metric", "4.7k")
    r_pu2.ref = "R_PU2"
    r_pu2["1"] += i2c_scl
    r_pu2["2"] += vcc_3v3_rpi

    # Expansion Screw Terminal Block for A2 and A3 channels
    tb_exp_pins = [("1", "A2", Pin.types.PASSIVE), ("2", "A3", Pin.types.PASSIVE)]
    tb_exp = _make_part(c, 
        name="Screw_Terminal_01x02",
        ref_prefix="TB",
        pins=tb_exp_pins,
        footprint="TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
        value="ADC_EXP_A2_A3",
    )
    tb_exp.ref = "TB_EXP"
    tb_exp["1"] += adc_a2
    tb_exp["2"] += adc_a3

    # =========================================================================
    # 6. MOTOR CURRENT SENSING: ACS712T-30A (U3) & SCT-013-000 CT CLAMP (J_CT)
    # =========================================================================
    # ACS712 Hall-Effect Sensor
    acs_pins = [
        ("1", "IP+", Pin.types.PASSIVE),
        ("2", "IP+", Pin.types.PASSIVE),
        ("3", "IP-", Pin.types.PASSIVE),
        ("4", "IP-", Pin.types.PASSIVE),
        ("5", "GND", Pin.types.PWRIN),
        ("6", "FILTER", Pin.types.PASSIVE),
        ("7", "VIOUT", Pin.types.OUTPUT),
        ("8", "VCC", Pin.types.PWRIN),
    ]
    u3 = _make_part(c, name="ACS712ELCTR-30A-T", ref_prefix="U", pins=acs_pins, footprint="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", value="ACS712T-30A")
    u3.ref = "U3"
    u3["1"] += ac_l_in
    u3["2"] += ac_l_in
    u3["3"] += ac_l_pump
    u3["4"] += ac_l_pump
    u3["5"] += gnd
    u3["7"] += adc_a0
    u3["8"] += vcc_5v

    # ACS712 Filter Capacitor
    c_f = _make_part(c, "C", "C", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Capacitor_SMD:C_0805_2012Metric", "4.7nF")
    c_f.ref = "C_F"
    c_f["1"] += u3["6"]
    c_f["2"] += gnd

    # ACS712 VCC Decoupling Capacitor
    c_acs = _make_part(c, "C", "C", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Capacitor_SMD:C_0805_2012Metric", "0.1uF")
    c_acs.ref = "C_ACS"
    c_acs["1"] += vcc_5v
    c_acs["2"] += gnd

    # SCT-013-000 CT Clamp Input Interface (3.5mm Jack + 33 ohm Burden + DC Bias Network)
    j_ct_pins = [("T", "TIP", Pin.types.PASSIVE), ("R", "RING", Pin.types.PASSIVE), ("S", "SLEEVE", Pin.types.PASSIVE)]
    j_ct = _make_part(c, name="AudioJack3", ref_prefix="J", pins=j_ct_pins, footprint="Connector_Audio:Jack_3.5mm_CUI_SJ1-3513N_Horizontal", value="SCT013_CT_Jack")
    j_ct.ref = "J_CT"
    j_ct["S"] += ct_bias
    j_ct["T"] += adc_a0
    j_ct["R"].do_erc = False

    # 33-ohm burden resistor across CT output
    r_burden = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_SMD:R_0805_2012Metric", "33_Ohm")
    r_burden.ref = "R_BURDEN"
    r_burden["1"] += ct_bias
    r_burden["2"] += adc_a0

    # DC Bias Network (shifts AC current waveform to 2.5V DC midpoint for ADC sampling)
    r_bias1 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_SMD:R_0805_2012Metric", "10k")
    r_bias1.ref = "R_BIAS1"
    r_bias1["1"] += vcc_5v
    r_bias1["2"] += ct_bias

    r_bias2 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_SMD:R_0805_2012Metric", "10k")
    r_bias2.ref = "R_BIAS2"
    r_bias2["1"] += ct_bias
    r_bias2["2"] += gnd

    c_bias = _make_part(c, "C", "C", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Capacitor_SMD:C_0805_2012Metric", "10uF")
    c_bias.ref = "C_BIAS"
    c_bias["1"] += ct_bias
    c_bias["2"] += gnd

    # =========================================================================
    # 7. ZMPT101B AC VOLTAGE SENSOR (T1) & CONDITIONING OP-AMP (U4)
    # =========================================================================
    zmpt_pins = [
        ("1", "PRI1", Pin.types.PASSIVE),
        ("2", "PRI2", Pin.types.PASSIVE),
        ("3", "SEC1", Pin.types.PASSIVE),
        ("4", "SEC2", Pin.types.PASSIVE),
    ]
    t1 = _make_part(c, name="ZMPT101B", ref_prefix="T", pins=zmpt_pins, footprint="Transformer_THT:Transformer_Zeming_ZMPT101K", value="ZMPT101B_Transformer")
    t1.ref = "T1"

    # High Voltage Limit Resistors (82k total across AC Line)
    r_hv1 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_THT:R_Axial_DIN0411_L9.9mm_D3.6mm_P15.24mm_Horizontal", "41.2k_1W")
    r_hv1.ref = "R_HV1"
    r_hv1["1"] += ac_l_in

    r_hv2 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_THT:R_Axial_DIN0411_L9.9mm_D3.6mm_P15.24mm_Horizontal", "41.2k_1W")
    r_hv2.ref = "R_HV2"
    r_hv2["1"] += r_hv1["2"]
    r_hv2["2"] += t1["1"]

    t1["2"] += ac_n_in

    # Conditioning Op-Amp (LM358)
    opamp_pins = [
        ("1", "OUTA", Pin.types.OUTPUT),
        ("2", "INA-", Pin.types.INPUT),
        ("3", "INA+", Pin.types.INPUT),
        ("4", "GND", Pin.types.PWRIN),
        ("5", "INB+", Pin.types.INPUT),
        ("6", "INB-", Pin.types.INPUT),
        ("7", "OUTB", Pin.types.OUTPUT),
        ("8", "VCC", Pin.types.PWRIN),
    ]
    u4 = _make_part(c, name="LM358", ref_prefix="U", pins=opamp_pins, footprint="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", value="LM358_Conditioner")
    u4.ref = "U4"
    u4["4"] += gnd
    u4["8"] += vcc_5v
    u4["5"] += gnd
    u4["6"] += u4["7"]  # Follower tie for unused channel B
    u4["7"].do_erc = False

    # Connect Transformer Secondary to Op-Amp A
    t1["3"] += u4["2"]
    t1["4"] += gnd
    u4["3"] += gnd
    u4["1"] += adc_a1

    # =========================================================================
    # 8. DUAL RELAYS (K1, K2), OPTOCOUPLERS, DRIVERS & MAINS TRANSIENT PROTECTION
    # =========================================================================
    relay_pins = [
        ("1", "A1", Pin.types.PASSIVE),
        ("2", "A2", Pin.types.PASSIVE),
        ("3", "COM", Pin.types.PASSIVE),
        ("4", "NO", Pin.types.PASSIVE),
        ("5", "NC", Pin.types.PASSIVE),
    ]
    optoc_pins = [
        ("1", "Anode", Pin.types.PASSIVE),
        ("2", "Cathode", Pin.types.PASSIVE),
        ("3", "Emitter", Pin.types.PASSIVE),
        ("4", "Collector", Pin.types.PASSIVE),
    ]
    npn_pins = [("1", "B", Pin.types.INPUT), ("2", "E", Pin.types.PASSIVE), ("3", "C", Pin.types.PASSIVE)]

    # --- Relay 1 (Primary Pump) ---
    # Optocoupler input series current limiting resistor (470 ohm for 3.3V GPIO -> PC817 LED)
    r_opt1 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_SMD:R_0805_2012Metric", "470")
    r_opt1.ref = "R_OPT1"
    r_opt1["1"] += relay1_ctrl
    r_opt1["2"] += opt1_in

    u5 = _make_part(c, name="PC817", ref_prefix="U", pins=optoc_pins, footprint="Package_DIP:DIP-4_W7.62mm", value="PC817_Pump")
    u5.ref = "U5"
    u5["1"] += opt1_in
    u5["2"] += gnd
    u5["4"] += vcc_5v

    # NPN Base Drive Resistor (1k) and Pull-Down Resistor (10k)
    r_drv1 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_SMD:R_0805_2012Metric", "1k")
    r_drv1.ref = "R_DRV1"
    r_drv1["1"] += u5["3"]
    r_drv1["2"] += q1_base

    r_pd1 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_SMD:R_0805_2012Metric", "10k")
    r_pd1.ref = "R_PD1"
    r_pd1["1"] += q1_base
    r_pd1["2"] += gnd

    q1 = _make_part(c, name="MMBT3904", ref_prefix="Q", pins=npn_pins, footprint="Package_TO_SOT_SMD:SOT-23", value="2N2222_NPN")
    q1.ref = "Q1"
    q1["1"] += q1_base
    q1["2"] += gnd

    k1 = _make_part(c, name="SRD-05VDC-SL-C", ref_prefix="K", pins=relay_pins, footprint="Relay_THT:Relay_SPDT_SANYOU_SRD_Series_Form_C", value="Songle_5V_10A")
    k1.ref = "K1"
    k1["1"] += vcc_5v
    k1["2"] += q1["3"]
    k1["3"] += ac_l_pump
    k1["4"] += ac_pump_out
    k1["5"].do_erc = False

    # Relay 1 Mains Transient Protection: MOV (14D471K / 275VAC) across contact terminals
    varistor_pins = [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)]
    mov1 = _make_part(c, name="Varistor", ref_prefix="MOV", pins=varistor_pins, footprint="Varistor:RV_Disc_D12mm_W4.2mm_P7.5mm", value="14D471K_275VAC")
    mov1.ref = "MOV1"
    mov1["1"] += ac_l_pump
    mov1["2"] += ac_pump_out

    # Relay 1 RC Snubber: 100 ohm 1W + 0.1uF 630V X2 film cap in series across contact terminals
    r_snub1 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_THT:R_Axial_DIN0411_L9.9mm_D3.6mm_P15.24mm_Horizontal", "100_1W")
    r_snub1.ref = "R_SNUB1"
    r_snub1["1"] += ac_l_pump
    r_snub1["2"] += snub1_mid

    c_snub1 = _make_part(c, "C", "C", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Capacitor_THT:C_Rect_L10.0mm_W4.0mm_P7.50mm_MKS4", "0.1uF_630V_X2")
    c_snub1.ref = "C_SNUB1"
    c_snub1["1"] += snub1_mid
    c_snub1["2"] += ac_pump_out

    # --- Relay 2 (Aux / Valve) ---
    r_opt2 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_SMD:R_0805_2012Metric", "470")
    r_opt2.ref = "R_OPT2"
    r_opt2["1"] += relay2_ctrl
    r_opt2["2"] += opt2_in

    u6 = _make_part(c, name="PC817", ref_prefix="U", pins=optoc_pins, footprint="Package_DIP:DIP-4_W7.62mm", value="PC817_Aux")
    u6.ref = "U6"
    u6["1"] += opt2_in
    u6["2"] += gnd
    u6["4"] += vcc_5v

    # NPN Base Drive Resistor (1k) and Pull-Down Resistor (10k)
    r_drv2 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_SMD:R_0805_2012Metric", "1k")
    r_drv2.ref = "R_DRV2"
    r_drv2["1"] += u6["3"]
    r_drv2["2"] += q2_base

    r_pd2 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_SMD:R_0805_2012Metric", "10k")
    r_pd2.ref = "R_PD2"
    r_pd2["1"] += q2_base
    r_pd2["2"] += gnd

    q2 = _make_part(c, name="MMBT3904", ref_prefix="Q", pins=npn_pins, footprint="Package_TO_SOT_SMD:SOT-23", value="2N2222_NPN")
    q2.ref = "Q2"
    q2["1"] += q2_base
    q2["2"] += gnd

    k2 = _make_part(c, name="SRD-05VDC-SL-C", ref_prefix="K", pins=relay_pins, footprint="Relay_THT:Relay_SPDT_SANYOU_SRD_Series_Form_C", value="Songle_5V_10A")
    k2.ref = "K2"
    k2["1"] += vcc_5v
    k2["2"] += q2["3"]
    k2["3"] += ac_l_in
    k2["4"] += ac_valve_out
    k2["5"].do_erc = False

    # Flyback Protection Diodes across relay coils
    d_pins = [("1", "K", Pin.types.PASSIVE), ("2", "A", Pin.types.PASSIVE)]
    d2 = _make_part(c, name="1N4007", ref_prefix="D", pins=d_pins, footprint="Diode_SMD:D_SMA", value="1N4007")
    d2.ref = "D2"
    d2["1"] += vcc_5v
    d2["2"] += q1["3"]

    d3 = _make_part(c, name="1N4007", ref_prefix="D", pins=d_pins, footprint="Diode_SMD:D_SMA", value="1N4007")
    d3.ref = "D3"
    d3["1"] += vcc_5v
    d3["2"] += q2["3"]

    # =========================================================================
    # 9. MANUAL OVERRIDE BUTTONS (SW1, SW2) & STATUS LEDS
    # =========================================================================
    sw_pins = [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)]
    sw1 = _make_part(c, name="SW_Push", ref_prefix="SW", pins=sw_pins, footprint="Button_Switch_THT:SW_PUSH_6mm", value="Force_ON")
    sw1.ref = "SW1"
    sw1["1"] += btn_force_on
    sw1["2"] += gnd

    sw2 = _make_part(c, name="SW_Push", ref_prefix="SW", pins=sw_pins, footprint="Button_Switch_THT:SW_PUSH_6mm", value="Force_OFF")
    sw2.ref = "SW2"
    sw2["1"] += btn_force_off
    sw2["2"] += gnd

    # Pump Status LED with 330-ohm series resistor
    r_led1 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_SMD:R_0805_2012Metric", "330")
    r_led1.ref = "R_LED1"
    r_led1["1"] += led_pump_run
    r_led1["2"] += led_drive

    led_pins = [("1", "A", Pin.types.PASSIVE), ("2", "K", Pin.types.PASSIVE)]
    led_pump = _make_part(c, name="LED", ref_prefix="D", pins=led_pins, footprint="LED_SMD:LED_0805_2012Metric", value="Green_Pump_Active")
    led_pump.ref = "LED_PUMP"
    led_pump["1"] += led_drive
    led_pump["2"] += gnd

    # 5V Power LED with 470-ohm series resistor
    r_led2 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_SMD:R_0805_2012Metric", "470")
    r_led2.ref = "R_LED2"
    r_led2["1"] += vcc_5v
    r_led2["2"] += led_5v_mid

    led_5v = _make_part(c, name="LED", ref_prefix="D", pins=led_pins, footprint="LED_SMD:LED_0805_2012Metric", value="Green_5V_Power")
    led_5v.ref = "LED_5V"
    led_5v["1"] += led_5v_mid
    led_5v["2"] += gnd

    # 3.3V LoRa Power LED with 330-ohm series resistor
    r_led3 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_SMD:R_0805_2012Metric", "330")
    r_led3.ref = "R_LED3"
    r_led3["1"] += vcc_3v3_lora
    r_led3["2"] += led_3v3_mid

    led_3v3 = _make_part(c, name="LED", ref_prefix="D", pins=led_pins, footprint="LED_SMD:LED_0805_2012Metric", value="Blue_3V3_LoRa")
    led_3v3.ref = "LED_3V3"
    led_3v3["1"] += led_3v3_mid
    led_3v3["2"] += gnd

    # =========================================================================
    # 10. HIGH VOLTAGE AC TERMINAL BLOCKS (TB2, TB3)
    # =========================================================================
    tb2_pins = [("1", "AC_LIVE", Pin.types.PASSIVE), ("2", "AC_NEUTRAL", Pin.types.PASSIVE)]
    tb2 = _make_part(c, 
        name="Screw_Terminal_01x02",
        ref_prefix="TB",
        pins=tb2_pins,
        footprint="TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
        value="AC_VOLT_SENSE_IN",
    )
    tb2.ref = "TB2"
    tb2["1"] += ac_l_in
    tb2["2"] += ac_n_in

    tb3_pins = [
        ("1", "PUMP_LIVE", Pin.types.PASSIVE),
        ("2", "VALVE_LIVE", Pin.types.PASSIVE),
        ("3", "NEUTRAL_RETURN", Pin.types.PASSIVE),
    ]
    tb3 = _make_part(c, 
        name="Screw_Terminal_01x03",
        ref_prefix="TB",
        pins=tb3_pins,
        footprint="TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal",
        value="LOAD_ACTUATORS_OUT",
    )
    tb3.ref = "TB3"
    tb3["1"] += ac_pump_out
    tb3["2"] += ac_valve_out
    tb3["3"] += ac_n_in

    return c


def validate_wilo_receiver_erc() -> tuple[int, int]:
    """Run SKiDL Electrical Rules Check (ERC) on the receiver circuit.

    Returns:
        tuple[int, int]: Count of (errors, warnings) reported by ERC.
    """
    from skidl import erc_logger

    circuit = create_wilo_receiver_circuit()
    circuit.ERC()
    errors = erc_logger.error.count
    warnings = erc_logger.warning.count
    return errors, warnings
