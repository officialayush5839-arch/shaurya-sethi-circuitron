"""Unit tests for the Wilo Receiver Station companion firmware & calibration logic."""
import math
import pytest
from scripts.companion_firmware.calibrate_voltage import compute_true_rms, measure_zero_point
from scripts.companion_firmware.measure_current import (
    compute_current_rms,
    MotorProtectionMonitor,
)
from scripts.companion_firmware.tank_config import (
    VOLTAGE_CALIBRATION_FACTOR,
    DRY_RUN_CURRENT_THRESHOLD_A,
    OVERLOAD_CURRENT_THRESHOLD_A,
)


def test_voltage_rms_calculation():
    """Verify that True-RMS calculation converts sinusoidal samples to expected RMS voltage."""
    # Generate 1 complete sine wave cycle with 230V RMS equivalent
    num_samples = 100
    peak_v = 1.0  # Normalized peak
    dc_offset = 2.5
    cal_factor = 230.0 / (peak_v / math.sqrt(2))  # Scale factor so RMS == 230V

    samples = [dc_offset + peak_v * math.sin(2 * math.pi * i / num_samples) for i in range(num_samples)]
    rms = compute_true_rms(samples, dc_offset, cal_factor)
    assert pytest.approx(rms, rel=1e-2) == 230.0


def test_measure_zero_point():
    """Verify DC offset averaging with simulated constant DC voltage."""
    fn = lambda: 2.502
    avg = measure_zero_point(fn, num_samples=10, sample_delay_sec=0.0001)
    assert pytest.approx(avg, abs=1e-4) == 2.502


def test_current_rms_calculation():
    """Verify current sensor sensitivity scaling and zero-point subtraction."""
    num_samples = 100
    sensitivity = 0.066  # 66 mV/A
    dc_offset = 2.500
    peak_amps = 10.0 * math.sqrt(2)  # 10A RMS
    peak_v = peak_amps * sensitivity

    samples = [dc_offset + peak_v * math.sin(2 * math.pi * i / num_samples) for i in range(num_samples)]
    rms_amps = compute_current_rms(samples, dc_offset, sensitivity)
    assert pytest.approx(rms_amps, rel=1e-2) == 10.0


def test_motor_protection_monitor_dry_run():
    """Verify dry-run trip occurs when current < 1.5A persists for > 2.0 seconds."""
    monitor = MotorProtectionMonitor()
    t0 = 100.0

    # Low current at t0
    assert monitor.evaluate_current(1.0, now=t0) == "NORMAL"
    # Low current after 1.5 seconds (< 2.0s duration) -> still NORMAL
    assert monitor.evaluate_current(1.0, now=t0 + 1.5) == "NORMAL"
    # Low current after 2.1 seconds (> 2.0s duration) -> DRY_RUN_TRIP
    assert monitor.evaluate_current(1.0, now=t0 + 2.1) == "DRY_RUN_TRIP"
    # Current recovers to normal (11.4A) -> resets to NORMAL
    assert monitor.evaluate_current(11.4, now=t0 + 2.5) == "NORMAL"


def test_motor_protection_monitor_overload():
    """Verify overload trip occurs when current > 13.7A persists for > 3.0 seconds."""
    monitor = MotorProtectionMonitor()
    t0 = 100.0

    # Normal current
    assert monitor.evaluate_current(11.4, now=t0) == "NORMAL"
    # Overload spike at t0 + 1.0s
    assert monitor.evaluate_current(15.0, now=t0 + 1.0) == "NORMAL"
    # Overload persists for 2.5s (duration < 3.0s) -> still NORMAL
    assert monitor.evaluate_current(15.0, now=t0 + 3.5) == "NORMAL"
    # Overload persists for 3.1s (duration >= 3.0s) -> OVERLOAD_TRIP
    assert monitor.evaluate_current(15.0, now=t0 + 4.1) == "OVERLOAD_TRIP"
