"""Wilo Water Pump Automation Receiver Station Circuit Definition.

Implements the complete SKiDL circuit model for the Raspberry Pi Zero 2W HAT,
integrating:
- SX1278 433MHz LoRa transceiver (Ra-02 footprint)
- ADS1115 16-bit I2C ADC
- ACS712T-30A AC current sensor
- ZMPT101B AC voltage transformer & op-amp conditioning circuit
- Dual optocoupled 10A relays (Pump & Aux Valve)
- Tactile push buttons (Force ON / Force OFF) & status LEDs
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
    adc_a0 = Net("ADC_A0", circuit=c)
    adc_a1 = Net("ADC_A1", circuit=c)

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
    for unused_pin in ["7", "8", "10", "12", "16", "17", "26", "27", "28", "32", "33", "35", "36", "37", "38", "40"]:
        j1[unused_pin].do_erc = False

    # =========================================================================
    # 3. POWER INPUT & DEDICATED 3.3V LDO REGULATOR (U1)
    # =========================================================================
    tb1_pins = [("1", "VCC_5V", Pin.types.PWRIN), ("2", "GND", Pin.types.PWRIN)]
    tb1 = _make_part(c, 
        name="Screw_Terminal_01x02",
        ref_prefix="TB",
        pins=tb1_pins,
        footprint="TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
        value="5V_DC_IN",
    )
    tb1.ref = "TB1"
    tb1["1"] += vcc_5v
    tb1["2"] += gnd

    # AMS1117-3.3 LDO
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
    # 4. SX1278 433MHz LoRa TRANSCEIVER (U_LORA) & SMA ANTENNA (J_SMA)
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
    u_lora = _make_part(c, name="Ra-02_SX1278", ref_prefix="U", pins=lora_pins, footprint="RF_Module:Ra-02", value="SX1278_433MHz")
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

    rf_ant = Net("RF_ANT", circuit=c)
    u_lora["15"] += rf_ant

    j_sma_pins = [("1", "In", Pin.types.PASSIVE), ("2", "Ext", Pin.types.PWRIN)]
    j_sma = _make_part(c, name="SMA_Connector", ref_prefix="J", pins=j_sma_pins, footprint="Connector_Coaxial:SMA_Amphenol_132134-10_Vertical", value="SMA_50_Ohm")
    j_sma.ref = "J_SMA"
    j_sma["1"] += rf_ant
    j_sma["2"] += gnd

    # =========================================================================
    # 5. ADS1115 16-BIT I2C ADC (U2) & I2C PULL-UPS
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
    u2["4"] += adc_a0      # Channel 0: Current sensor output
    u2["5"] += adc_a1      # Channel 1: Voltage sensor output
    u2["6"].do_erc = False
    u2["7"].do_erc = False
    u2["8"] += vcc_5v      # Full 0-5V dynamic analog range
    u2["9"] += i2c_sda
    u2["10"] += i2c_scl

    # I2C Pull-Up Resistors (4.7k to 3.3V)
    r_pu1 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_SMD:R_0805_2012Metric", "4.7k")
    r_pu1.ref = "R_PU1"
    r_pu1["1"] += i2c_sda
    r_pu1["2"] += vcc_3v3_rpi

    r_pu2 = _make_part(c, "R", "R", [("1", "1", Pin.types.PASSIVE), ("2", "2", Pin.types.PASSIVE)], "Resistor_SMD:R_0805_2012Metric", "4.7k")
    r_pu2.ref = "R_PU2"
    r_pu2["1"] += i2c_scl
    r_pu2["2"] += vcc_3v3_rpi

    # =========================================================================
    # 6. ACS712T-30A CURRENT SENSOR (U3)
    # =========================================================================
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

    # =========================================================================
    # 7. ZMPT101B AC VOLTAGE SENSOR (T1) & CONDITIONING OP-AMP (U4)
    # =========================================================================
    zmpt_pins = [
        ("1", "PRI1", Pin.types.PASSIVE),
        ("2", "PRI2", Pin.types.PASSIVE),
        ("3", "SEC1", Pin.types.PASSIVE),
        ("4", "SEC2", Pin.types.PASSIVE),
    ]
    t1 = _make_part(c, name="ZMPT101B", ref_prefix="T", pins=zmpt_pins, footprint="Transformer_THT:Transformer_ZMPT101B", value="ZMPT101B_Transformer")
    t1.ref = "T1"

    # High Voltage Limit Resistors (82k total)
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
    # 8. DUAL RELAYS (K1, K2), OPTOCOUPLERS (U5, U6) & DRIVERS (Q1, Q2)
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

    # Relay 1 (Primary Pump)
    u5 = _make_part(c, name="PC817", ref_prefix="U", pins=optoc_pins, footprint="Package_DIP:DIP-4_W7.62mm", value="PC817_Pump")
    u5.ref = "U5"
    u5["1"] += relay1_ctrl
    u5["2"] += gnd
    u5["4"] += vcc_5v

    q1 = _make_part(c, name="MMBT3904", ref_prefix="Q", pins=npn_pins, footprint="Package_TO_SOT_SMD:SOT-23", value="2N2222_NPN")
    q1.ref = "Q1"
    q1["1"] += u5["3"]
    q1["2"] += gnd

    k1 = _make_part(c, name="SRD-05VDC-SL-C", ref_prefix="K", pins=relay_pins, footprint="Relay_THT:Relay_SPDT_Songle_SRD_Series", value="Songle_5V_10A")
    k1.ref = "K1"
    k1["1"] += vcc_5v
    k1["2"] += q1["3"]
    k1["3"] += ac_l_pump
    k1["4"] += ac_pump_out
    k1["5"].do_erc = False

    # Relay 2 (Aux / Valve)
    u6 = _make_part(c, name="PC817", ref_prefix="U", pins=optoc_pins, footprint="Package_DIP:DIP-4_W7.62mm", value="PC817_Aux")
    u6.ref = "U6"
    u6["1"] += relay2_ctrl
    u6["2"] += gnd
    u6["4"] += vcc_5v

    q2 = _make_part(c, name="MMBT3904", ref_prefix="Q", pins=npn_pins, footprint="Package_TO_SOT_SMD:SOT-23", value="2N2222_NPN")
    q2.ref = "Q2"
    q2["1"] += u6["3"]
    q2["2"] += gnd

    k2 = _make_part(c, name="SRD-05VDC-SL-C", ref_prefix="K", pins=relay_pins, footprint="Relay_THT:Relay_SPDT_Songle_SRD_Series", value="Songle_5V_10A")
    k2.ref = "K2"
    k2["1"] += vcc_5v
    k2["2"] += q2["3"]
    k2["3"] += ac_l_in
    k2["4"] += ac_valve_out
    k2["5"].do_erc = False

    # Flyback Protection Diodes
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

    # Status LEDs
    led_pins = [("1", "A", Pin.types.PASSIVE), ("2", "K", Pin.types.PASSIVE)]
    led_pump = _make_part(c, name="LED", ref_prefix="D", pins=led_pins, footprint="LED_SMD:LED_0805_2012Metric", value="Green_Pump_Active")
    led_pump.ref = "LED_PUMP"
    led_pump["1"] += led_pump_run
    led_pump["2"] += gnd

    led_5v = _make_part(c, name="LED", ref_prefix="D", pins=led_pins, footprint="LED_SMD:LED_0805_2012Metric", value="Green_5V_Power")
    led_5v.ref = "LED_5V"
    led_5v["1"] += vcc_5v
    led_5v["2"] += gnd

    led_3v3 = _make_part(c, name="LED", ref_prefix="D", pins=led_pins, footprint="LED_SMD:LED_0805_2012Metric", value="Blue_3V3_LoRa")
    led_3v3.ref = "LED_3V3"
    led_3v3["1"] += vcc_3v3_lora
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
        value="AC_MAINS_IN",
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
