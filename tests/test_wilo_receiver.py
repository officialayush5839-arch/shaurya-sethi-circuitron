"""Unit tests for the Wilo Receiver Station PCB circuit implementation."""
import pytest


def test_wilo_receiver_circuit_components():
    """Verify all required circuit components exist in the generated SKiDL circuit."""
    from circuitron.circuits.wilo_receiver import create_wilo_receiver_circuit

    circuit = create_wilo_receiver_circuit()
    part_refs = {p.ref for p in circuit.parts}

    # Primary integrated components
    expected_parts = {
        "J1",       # 40-pin Raspberry Pi GPIO header
        "J_USBC",   # USB Type-C 5V power supply connector
        "R_CC1", "R_CC2", # 5.1k USB-C CC pull-down resistors
        "U_LORA",   # SX1278 433MHz Ra-02 LoRa module
        "C_LORA1", "C_LORA2", # 10uF + 0.1uF RF decoupling capacitors
        "U1",       # AMS1117-3.3 dedicated LDO regulator
        "C1", "C2", # 10uF in / 22uF out LDO filter capacitors
        "U2",       # ADS1115 16-bit I2C ADC
        "C_ADS",    # 100nF ADC decoupling capacitor
        "R_PU1", "R_PU2", # 4.7k I2C pull-up resistors
        "TB_EXP",   # Channels A2 & A3 expansion terminal block
        "J_CT",     # SCT-013-000 3.5mm CT clamp audio jack
        "R_BURDEN", # 33-ohm burden resistor
        "R_BIAS1", "R_BIAS2", "C_BIAS", # CT clamp DC bias network (10k + 10k + 10uF)
        "U3",       # ACS712T-30A current sensor
        "C_F",      # 4.7nF ACS712 filter capacitor
        "C_ACS",    # 0.1uF ACS712 VCC decoupling capacitor
        "T1",       # ZMPT101B voltage transformer
        "R_HV1", "R_HV2", # 41.2k 1W voltage divider resistors
        "U4",       # LM358 op-amp conditioning circuit
        "U5", "U6", # PC817 optocouplers
        "R_OPT1", "R_OPT2", # Optocoupler LED current-limiting resistors (470 ohm)
        "R_DRV1", "R_DRV2", # NPN base drive resistors (1k ohm)
        "R_PD1", "R_PD2",   # NPN base pull-down resistors (10k ohm)
        "K1", "K2", # 5V 10A Songle Relays (Pump + Aux Valve)
        "D2", "D3", # 1N4007 flyback diodes across relay coils
        "MOV1",     # 14D471K Varistor for pump inductive transient protection
        "R_SNUB1", "C_SNUB1", # RC Snubber (100-ohm + 0.1uF 630V X2) for pump relay contacts
        "Q1", "Q2", # NPN driver transistors
        "SW1", "SW2", # Force ON and Force OFF tactile push buttons
        "LED_PUMP", "R_LED1", # Status LED + 330-ohm resistor
        "LED_5V", "R_LED2",   # 5V Power LED + 470-ohm resistor
        "LED_3V3", "R_LED3",  # 3.3V LoRa LED + 330-ohm resistor
        "TB2", "TB3", # AC Mains Voltage Sense & Load Actuators
    }

    missing = expected_parts - part_refs
    assert not missing, f"Missing parts from circuit: {missing}"


def test_pin_connectivity():
    """Verify exact pin bindings between RPi header, sensors, LoRa, and relays."""
    from circuitron.circuits.wilo_receiver import create_wilo_receiver_circuit

    circuit = create_wilo_receiver_circuit()
    j1 = next(p for p in circuit.parts if p.ref == "J1")

    # RPi Header signal pins
    assert j1["3"].net.name == "I2C_SDA"
    assert j1["5"].net.name == "I2C_SCL"
    assert j1["11"].net.name == "RELAY1_CTRL"
    assert j1["13"].net.name == "RELAY2_CTRL"
    assert j1["15"].net.name == "BTN_FORCE_ON"
    assert j1["18"].net.name == "LORA_DIO0"
    assert j1["19"].net.name == "SPI0_MOSI"
    assert j1["21"].net.name == "SPI0_MISO"
    assert j1["22"].net.name == "LORA_RST"
    assert j1["23"].net.name == "SPI0_SCLK"
    assert j1["24"].net.name == "SPI0_CE0"
    assert j1["29"].net.name == "BTN_FORCE_OFF"
    assert j1["31"].net.name == "LED_PUMP_RUN"

    # Radio power isolation (dedicated 3.3V LDO, not RPi rail)
    u_lora = next(p for p in circuit.parts if p.ref == "U_LORA")
    assert u_lora["9"].net.name == "+3V3_LORA"

    # Current sensor net connections
    u3 = next(p for p in circuit.parts if p.ref == "U3")
    assert u3["1"].net.name == "AC_L_IN"
    assert u3["3"].net.name == "AC_L_PUMP"
    assert u3["7"].net.name == "ADC_A0"

    # Voltage sensor output to ADC
    u4 = next(p for p in circuit.parts if p.ref == "U4")
    assert u4["1"].net.name == "ADC_A1"

    # Relay 1 (Pump) connects between ACS712 output and Pump Output terminal
    k1 = next(p for p in circuit.parts if p.ref == "K1")
    assert k1["3"].net.name == "AC_L_PUMP"
    assert k1["4"].net.name == "AC_PUMP_OUT"

    # Relay 2 (Aux/Valve) connects to Valve Output terminal
    k2 = next(p for p in circuit.parts if p.ref == "K2")
    assert k2["3"].net.name == "AC_L_IN"
    assert k2["4"].net.name == "AC_VALVE_OUT"

    # USB-C 5V and CC pull-downs
    j_usbc = next(p for p in circuit.parts if p.ref == "J_USBC")
    assert j_usbc["A4"].net.name == "+5V"
    assert j_usbc["A1"].net.name == "GND"

    # Transient protection on pump contacts
    mov1 = next(p for p in circuit.parts if p.ref == "MOV1")
    assert {mov1["1"].net.name, mov1["2"].net.name} == {"AC_L_PUMP", "AC_PUMP_OUT"}

    # Expansion terminal for ADC channels A2 and A3
    tb_exp = next(p for p in circuit.parts if p.ref == "TB_EXP")
    assert tb_exp["1"].net.name == "ADC_A2"
    assert tb_exp["2"].net.name == "ADC_A3"

    # Optocoupler inputs have series resistors
    r_opt1 = next(p for p in circuit.parts if p.ref == "R_OPT1")
    assert r_opt1["1"].net.name == "RELAY1_CTRL"
    r_opt2 = next(p for p in circuit.parts if p.ref == "R_OPT2")
    assert r_opt2["1"].net.name == "RELAY2_CTRL"

    # LEDs have series current-limiting resistors
    r_led2 = next(p for p in circuit.parts if p.ref == "R_LED2")
    assert r_led2["1"].net.name == "+5V"
    r_led3 = next(p for p in circuit.parts if p.ref == "R_LED3")
    assert r_led3["1"].net.name == "+3V3_LORA"


def test_wilo_receiver_erc():
    """Verify that SKiDL Electrical Rules Check reports 0 errors on the receiver circuit."""
    from circuitron.circuits.wilo_receiver import validate_wilo_receiver_erc

    errors, warnings = validate_wilo_receiver_erc()
    assert errors == 0, f"Circuit failed Electrical Rules Check with {errors} errors"
