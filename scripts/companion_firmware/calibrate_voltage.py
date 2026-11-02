"""ZMPT101B AC Voltage Sensor Calibration Script.

Records baseline DC zero-offset (at 0 V AC) and True-RMS live mains scaling
against a reference True-RMS digital multimeter.
"""
import time
import math
from typing import Callable
from scripts.companion_firmware.tank_config import (
    ADC_CHANNEL_VOLTAGE,
    VOLTAGE_CALIBRATION_FACTOR,
    VOLTAGE_BASELINE_MIDPOINT_V,
)


def compute_true_rms(
    samples: list[float],
    dc_offset: float,
    calibration_factor: float,
) -> float:
    """Calculate True-RMS AC voltage from ADC voltage samples.

    Args:
        samples: List of sampled voltages in volts (0-5V).
        dc_offset: Measured DC midpoint offset (typically ~2.5V).
        calibration_factor: Gain scaling factor for sensor transformer.

    Returns:
        float: Calculated True-RMS AC voltage in Volts AC.
    """
    if not samples:
        return 0.0

    sum_squares = sum((s - dc_offset) ** 2 for s in samples)
    mean_square = sum_squares / len(samples)
    rms_v = math.sqrt(mean_square)
    return rms_v * calibration_factor


def measure_zero_point(
    read_sample_fn: Callable[[], float],
    num_samples: int = 1000,
    sample_delay_sec: float = 0.001,
) -> float:
    """Measure the zero-point baseline voltage with 0 V AC applied.

    Args:
        read_sample_fn: Callable returning instantaneous ADC voltage.
        num_samples: Number of samples to average.
        sample_delay_sec: Time delay between samples.

    Returns:
        float: Baseline DC midpoint in Volts.
    """
    samples = []
    for _ in range(num_samples):
        samples.append(read_sample_fn())
        time.sleep(sample_delay_sec)
    return sum(samples) / len(samples)


if __name__ == "__main__":
    print("ZMPT101B AC Voltage Sensor Calibration")
    print(f"Default Calibration Factor: {VOLTAGE_CALIBRATION_FACTOR}")
    print(f"Default Baseline Midpoint: {VOLTAGE_BASELINE_MIDPOINT_V:.3f} V")
