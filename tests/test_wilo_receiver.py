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
