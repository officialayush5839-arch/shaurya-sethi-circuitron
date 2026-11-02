"""Motor Current Sensor (ACS712 / SCT-013) Measurement & Trip Protection.

Provides real-time RMS current computation, zero-point calibration,
dry-run protection (< 1.5A for > 2s) and overload trip protection (> 13.7A for > 3s).
"""
import time
import math
from typing import Callable, Literal
from scripts.companion_firmware.tank_config import (
    CURRENT_ZERO_OFFSET_V,
    ACS712_SENSITIVITY_V_PER_A,
    DRY_RUN_CURRENT_THRESHOLD_A,
    DRY_RUN_FAULT_DURATION_SEC,
    OVERLOAD_CURRENT_THRESHOLD_A,
    OVERLOAD_FAULT_DURATION_SEC,
)

TripStatus = Literal["NORMAL", "DRY_RUN_TRIP", "OVERLOAD_TRIP"]


def compute_current_rms(
    samples: list[float],
    dc_offset: float = CURRENT_ZERO_OFFSET_V,
    sensitivity: float = ACS712_SENSITIVITY_V_PER_A,
) -> float:
    """Compute True-RMS current in Amperes from instantaneous voltage samples.

    Args:
        samples: List of instantaneous voltage samples from ADC Channel A0.
        dc_offset: DC zero-point offset voltage (typically ~2.5V).
        sensitivity: Sensor sensitivity in Volts per Ampere (0.066 V/A for ACS712-30A).

    Returns:
        float: Calculated RMS current in Amperes.
    """
    if not samples or sensitivity <= 0.0:
        return 0.0

    sum_squares = sum(((s - dc_offset) / sensitivity) ** 2 for s in samples)
    mean_square = sum_squares / len(samples)
    return math.sqrt(mean_square)


class MotorProtectionMonitor:
    """Stateful protection monitor for dry-run and overload conditions."""

    def __init__(self) -> None:
        self.dry_run_timer: float | None = None
        self.overload_timer: float | None = None

    def evaluate_current(self, current_rms: float, now: float | None = None) -> TripStatus:
        """Evaluate RMS current against safety trip thresholds with persistence timers.

        Args:
            current_rms: Current reading in Amperes.
            now: Current timestamp (defaults to time.time()).

        Returns:
            TripStatus: 'NORMAL', 'DRY_RUN_TRIP', or 'OVERLOAD_TRIP'.
        """
        if now is None:
            now = time.time()

        # 1. Overload Check (> 13.7A for > 3s)
        if current_rms >= OVERLOAD_CURRENT_THRESHOLD_A:
            if self.overload_timer is None:
                self.overload_timer = now
            elif (now - self.overload_timer) >= OVERLOAD_FAULT_DURATION_SEC:
                return "OVERLOAD_TRIP"
        else:
            self.overload_timer = None

        # 2. Dry-Run Check (< 1.5A for > 2s while pump running)
        if current_rms < DRY_RUN_CURRENT_THRESHOLD_A:
            if self.dry_run_timer is None:
                self.dry_run_timer = now
            elif (now - self.dry_run_timer) >= DRY_RUN_FAULT_DURATION_SEC:
                return "DRY_RUN_TRIP"
        else:
            self.dry_run_timer = None

        return "NORMAL"


if __name__ == "__main__":
    print("Motor Current Sensor & Safety Trip Monitor Initialized.")
    print(f"Dry-Run Threshold: < {DRY_RUN_CURRENT_THRESHOLD_A} A for > {DRY_RUN_FAULT_DURATION_SEC} s")
    print(f"Overload Threshold: > {OVERLOAD_CURRENT_THRESHOLD_A} A for > {OVERLOAD_FAULT_DURATION_SEC} s")
