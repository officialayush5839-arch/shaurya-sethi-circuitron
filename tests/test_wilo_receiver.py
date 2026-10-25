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
        "U_LORA",   # SX1278 433MHz Ra-02 LoRa module
        "U1",       # AMS1117-3.3 dedicated LDO regulator
        "U2",       # ADS1115 16-bit I2C ADC
        "U3",       # ACS712T-30A current sensor
        "T1",       # ZMPT101B voltage transformer
        "U4",       # LM358 op-amp conditioning circuit
        "U5", "U6", # PC817 optocouplers
        "K1", "K2", # 5V 10A Songle Relays (Pump + Aux Valve)
        "Q1", "Q2", # NPN driver transistors
        "SW1", "SW2", # Force ON and Force OFF tactile push buttons
        "LED_PUMP", "LED_5V", "LED_3V3", # Status and power LEDs
        "TB1", "TB2", "TB3", # Screw terminal blocks for Power & AC Mains
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


def test_wilo_receiver_erc():
    """Verify that SKiDL Electrical Rules Check reports 0 errors on the receiver circuit."""
    from circuitron.circuits.wilo_receiver import validate_wilo_receiver_erc

    errors, warnings = validate_wilo_receiver_erc()
    assert errors == 0, f"Circuit failed Electrical Rules Check with {errors} errors"
