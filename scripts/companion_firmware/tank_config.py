"""Configuration settings for the Wilo Water Pump Automation Receiver Station."""

# =============================================================================
# GPIO PIN ASSIGNMENTS (Raspberry Pi Zero 2W 40-Pin Header)
# =============================================================================
PIN_RELAY_PUMP = 17       # Physical Pin 11: Primary Pump Relay Control (Active-HIGH)
PIN_RELAY_VALVE = 27      # Physical Pin 13: Auxiliary Relay / Valve Control
PIN_BTN_FORCE_ON = 22     # Physical Pin 15: Manual Force-ON Button (Active-LOW, pull-up)
PIN_BTN_FORCE_OFF = 5     # Physical Pin 29: Manual Force-OFF Button (Active-LOW, pull-up)
PIN_LED_PUMP_STATUS = 6   # Physical Pin 31: Status Indicator LED (High = Pump Active)

RELAY_ACTIVE_LOW = False  # Active-HIGH logic for optocoupler driver

# LoRa SX1278 (Ai-Thinker Ra-02) SPI0 Pins
LORA_SPI_BUS = 0
LORA_SPI_DEVICE = 0
PIN_LORA_MISO = 9         # Physical Pin 21
PIN_LORA_MOSI = 10        # Physical Pin 19
PIN_LORA_SCLK = 11        # Physical Pin 23
PIN_LORA_NSS = 8          # Physical Pin 24 (CE0)
PIN_LORA_RESET = 25       # Physical Pin 22
PIN_LORA_DIO0 = 24        # Physical Pin 18 (Packet Interrupt)
LORA_FREQUENCY_MHZ = 433.0

# =============================================================================
# ADS1115 16-BIT ADC CONFIGURATION (I2C1 Bus)
# =============================================================================
ADS1115_I2C_BUS = 1
ADS1115_I2C_ADDRESS = 0x48  # ADDR pin tied to GND
ADC_CHANNEL_CURRENT = 0      # Channel A0: Motor Current (ACS712 or SCT-013)
ADC_CHANNEL_VOLTAGE = 1      # Channel A1: AC Voltage (ZMPT101B)
ADC_CHANNEL_EXP_A2 = 2       # Channel A2: Screw Terminal Expansion
ADC_CHANNEL_EXP_A3 = 3       # Channel A3: Screw Terminal Expansion

# =============================================================================
# VOLTAGE SENSOR CALIBRATION (ZMPT101B)
# =============================================================================
VOLTAGE_CALIBRATION_FACTOR = 209.09  # True-RMS scaling constant
VOLTAGE_BASELINE_MIDPOINT_V = 2.500  # Baseline DC midpoint at 0V AC
POWER_VOLTAGE_PROTECTION = True      # Enable undervoltage protection
VOLTAGE_MIN_THRESHOLD_VAC = 180.0    # Undervoltage cut-off (230V mains nominal)
VOLTAGE_FAULT_DURATION_SEC = 10.0    # Trip if voltage < 180V for > 10 seconds

# =============================================================================
# CURRENT SENSOR CALIBRATION (ACS712-30A / SCT-013-000 CT Clamp)
# =============================================================================
CURRENT_ZERO_OFFSET_V = 2.500        # Zero-point DC voltage at 0A load
ACS712_SENSITIVITY_V_PER_A = 0.066   # 66 mV/A for ACS712-30A
SCT013_BURDEN_RESISTOR_OHM = 33.0    # 33-ohm burden resistor across 50mA secondary
MOTOR_RATED_FLA = 11.4               # Kirloskar KDS-8 rated full-load amps (FLA)

# Protection Safety Thresholds
DRY_RUN_CURRENT_THRESHOLD_A = 1.5    # Cut-off when lower tank is empty
DRY_RUN_FAULT_DURATION_SEC = 2.0     # Trip if current < 1.5A for > 2 seconds

OVERLOAD_CURRENT_THRESHOLD_A = 13.7  # Overcurrent threshold (> 1.2 * FLA)
OVERLOAD_FAULT_DURATION_SEC = 3.0    # Trip if current > 13.7A for > 3 seconds
