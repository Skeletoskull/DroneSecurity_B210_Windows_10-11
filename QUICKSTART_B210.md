# USRP B210 Quick Start Guide

## Overview

The USRP B210 is the **recommended SDR** for DroneID reception, offering:
- **2x faster frequency scanning** (50ms vs 100ms settling time)
- **Better sensitivity** (0-76 dB gain range vs 0-60 dB)
- **Lower noise figure** (~5 dB vs ~7 dB)
- **Higher sample rates** (up to 56 MHz vs 40 MHz)

## Hardware Detection

First, verify your B210 is connected:

```bash
cd src
python detect_hardware.py
```

Expected output:
```
✓ USRP B210 is connected and ready!
  Product: B210
  Serial: 3189F10
```

## Comprehensive Diagnostics

Run full hardware tests:

```bash
python diagnose_b210.py
```

This runs 4 tests:
1. Device detection
2. Frequency tuning (2.4 GHz band)
3. Sample reception (1M samples)
4. Gain control (manual and AGC)

## Running the Receiver

### Fast Detection Mode (Recommended)

Optimized for quick detection with Mini 2, Air 2, and similar drones:

```bash
python droneid_receiver_live.py --gain 40
```

This uses:
- **20 MHz sample rate** (stable on Windows USB)
- **0.5s capture duration** (fast scanning)
- **2.4 GHz only** (most DJI drones use this band)
- **Prioritized frequencies** (2459.5 MHz checked first - most common)
- **No file saving** (maximum speed, console output only)

### Legacy Drone Support

For Mavic Pro, Mavic 2, and Mavic Air 3:

```bash
python droneid_receiver_live.py --gain 50 --legacy
```

### With File Saving

If you want to save decoded packets and raw samples for analysis:

```bash
python droneid_receiver_live.py --gain 40 --save-files
```

Files saved:
- `decoded_bits_MMDD_HHMM.bin` - Decoded packet data
- `ext_drone_id_20000000_MMDD_HHMM.raw` - Last 10 raw packets (rotating)
- `receive_test_MMDD_HHMM.raw` - Latest capture (overwritten)

### Custom Parameters

```bash
# Higher gain for weak signals (distant drones)
python droneid_receiver_live.py --gain 55

# Lower gain for strong signals (close drones)
python droneid_receiver_live.py --gain 30

# Longer capture for difficult conditions
python droneid_receiver_live.py --gain 40 --duration 0.8

# Higher sample rate (Linux only - Windows limited to 20 MHz)
python droneid_receiver_live.py --gain 40 --sample_rate 50e6

# Include 5.8 GHz band (slower scanning, rarely needed)
python droneid_receiver_live.py --gain 40 --no-band-2-4-only

# Verbose output (shows processing stages)
python droneid_receiver_live.py --gain 40 --verbose
```

## What to Expect

### Startup (2-3 seconds)
```
Session started at: 2026-01-23 10:59:45
File saving: DISABLED (use --save-files to enable)
Running in maximum performance mode - all output to console only
Initializing USRP B210...
[INFO] [UHD] Win32; Microsoft Visual C++ version 14.2...
[INFO] [B200] Detected Device: B210
[INFO] [B200] Operating over USB 3.
USRP B210 initialized: 20.00 MHz sample rate, 40.0 dB gain
Start receiving...
```

### Scanning (cycling through frequencies)
```
Scanning: 2459.50 MHz @ 20.00 MHz
Scanning: 2444.50 MHz @ 20.00 MHz
Scanning: 2429.50 MHz @ 20.00 MHz
```

The system checks the most common frequency (2459.5 MHz) first. Detection time depends on signal strength and interference.

**Typical detection time:**
- Strong signal (< 10m): 5-15 seconds
- Medium signal (10-50m): 15-30 seconds
- Weak signal (> 50m): 30-60 seconds

### Detection and Lock
```
🎯 LOCKED to 2459.50 MHz - continuous monitoring

============================================================
{
  "timestamp": "2026-01-23T10:59:45.123456",
  "reception_time_utc": "2026-01-23T09:59:45.123456Z",
  "frequency_mhz": 2459.5,
  "telemetry": {
    "serial_number": "3NZCK1A0445Q5L",
    "device_type": "Mini 2",
    "position": {
      "latitude": 33.9607466782786,
      "longitude": 71.57866420676892,
      "altitude_m": 125.5,
      "height_m": 50.2
    },
    "velocity": {
      "north": 5,
      "east": -2,
      "up": 1
    },
    "home_position": {
      "latitude": 33.9600000000000,
      "longitude": 71.5780000000000
    },
    "operator_position": {
      "latitude": 33.9607466782786,
      "longitude": 71.57866420676892
    },
    "gps_time": 1723542961753,
    "sequence_number": 3031,
    "uuid": "1770032869329911808"
  },
  "crc_valid": true,
  "crc_packet": "e316",
  "crc_calculated": "e316"
}
============================================================
✅ CRC validation passed
```

Once locked, the system stays on that frequency for continuous monitoring. After 10 consecutive captures with no detection, it resumes scanning.

## Troubleshooting

### USB Overflow Warnings

If you see continuous "O" characters in the output, this indicates USB buffer overflow (samples being dropped). This is a **Windows USB limitation** and is expected behavior.

**What it means:**
- Windows USB stack cannot sustain high-bandwidth streaming reliably
- Some samples are dropped, but system continues to work
- Detection still works but with reduced performance

**Solutions:**
- Already using 20 MHz (lowest stable rate for Windows)
- Close other USB devices and applications
- Use a dedicated USB 3.0 controller (motherboard ports preferred)
- **Best solution:** Migrate to Linux for 50 MHz sample rate and no overflows

### Slow Detection or No Detection

**If drone is powered on but not detecting:**

1. **Verify drone is transmitting**: 
   - Mini 2 transmits even when powered on (not just flying)
   - Mavic 2/3 may require flight mode
   - Use spectrum analyzer: `python spectrum_analyzer.py -f 2459.5 -g 50`
   
2. **Check antenna**:
   - Must be connected to **RX2 port** (not RX1)
   - Antenna must cover 2.4-2.5 GHz range
   - Check SMA connector is tight
   - Try a different antenna if available

3. **Try different gain values**:
   - Close range (< 1m): Try `--gain 20` or `--gain 30`
   - Medium range (1-10m): Try `--gain 40` or `--gain 50`
   - Far range (> 10m): Try `--gain 55` or `--gain 60`
   - Very far (> 50m): Try `--gain 70` (max 76 dB)

4. **Check actual frequency**:
   - Run spectrum analyzer to see what frequencies have signals
   - Drone might be on different frequency than expected
   - Common frequencies: 2459.5, 2444.5, 2434.5, 2429.5 MHz

5. **Try legacy mode**:
   - Mavic 2, Mavic Pro, Mavic Air 3 require `--legacy` flag
   - `python droneid_receiver_live.py --gain 50 --legacy`

### Spectrum Analyzer Tool

To see what signals are actually being received:

```bash
python spectrum_analyzer.py -f 2450 -g 50
```

This shows:
- All signals in the spectrum (visual plot)
- Signal bandwidth (DroneID = ~10 MHz, WiFi = ~20 MHz)
- Noise floor and SNR
- Peak frequencies and power levels

**Expected for DroneID:**
- Signal bandwidth: 8-12 MHz
- Signal at 2459.5, 2444.5, 2434.5, or 2429.5 MHz
- Peak power 20-30 dB above noise floor

**If you see 20 MHz wide signals:**
- This is WiFi interference, not DroneID
- Try different frequencies or move away from WiFi routers
- Test outdoors for cleaner spectrum

### CRC Errors

If packets are detected but have CRC errors:

1. **Signal too weak**: Increase gain (`--gain 50` or `--gain 55`)
2. **Signal too strong**: Decrease gain if drone very close (`--gain 30`)
3. **Interference**: Test outdoors away from WiFi and other 2.4 GHz devices
4. **Multipath**: Indoor reflections cause timing errors - test outdoors
5. **USB sample loss**: Windows USB limitations - migrate to Linux for best results

### USB Errors

If you see `LIBUSB_TRANSFER_NO_DEVICE` or similar USB errors:
1. Unplug and reconnect B210 (wait 5 seconds between)
2. Try a different USB 3.0 port (motherboard ports preferred over hubs)
3. Restart the script
4. Check Windows Device Manager for USB controller issues
5. Update USB 3.0 controller drivers
6. Try a different USB 3.0 cable

### No Signals Detected at All

If spectrum analyzer shows no signals above noise floor:

1. **Antenna not connected** - Check RX2 port
2. **Wrong antenna port** - Use RX2, not RX1
3. **Drone not transmitting** - Verify drone is powered on and flying
4. **Gain too low** - Try 50-60 dB
5. **Out of range** - Move closer (within 50 meters)
6. **Frequency mismatch** - Scan all frequencies with spectrum analyzer

## Performance Notes

### Windows vs Linux

| Metric | Windows | Linux |
|--------|---------|-------|
| Sample Rate | 20 MHz | 50-56 MHz |
| USB Stability | Moderate (overflows common) | Excellent |
| Detection Speed | Variable | Consistent |
| Recommended For | Development/Testing | Production |

**For production use, Linux is strongly recommended.**

### B210 vs BladeRF A4

| Feature | BladeRF A4 | USRP B210 |
|---------|-----------|-----------|
| Frequency Settling | 100ms | 50ms (2x faster) |
| Gain Range | 0-60 dB | 0-76 dB |
| Noise Figure | ~7 dB | ~5 dB |
| Max Sample Rate | 40 MHz | 56 MHz |
| Windows USB | Good | Better |

B210 is superior in all technical aspects.

## Diagnostic Tools

### 1. Hardware Detection
```bash
python detect_hardware.py
```
Verifies B210 is connected and shows device info.

### 2. B210 Diagnostics
```bash
python diagnose_b210.py
```
Runs 4 comprehensive tests:
- Device detection
- Frequency tuning
- Sample reception
- Gain control

### 3. Spectrum Analyzer
```bash
python spectrum_analyzer.py -f 2459.5 -g 50
```
Shows actual received spectrum - most useful for debugging reception issues.

### 4. Offline Decoder Test
```bash
python droneid_receiver_offline.py -i receive_test.raw
```
Tests decoder with known good sample file.

## Next Steps

1. **Verify hardware**: Run `python detect_hardware.py`
2. **Test reception**: Run `python spectrum_analyzer.py -f 2459.5 -g 50`
3. **Start receiver**: Run `python droneid_receiver_live.py --gain 40`
4. **Adjust gain**: Based on signal strength and distance
5. **Monitor output**: Watch for JSON telemetry data

For production deployment, consider migrating to Linux for optimal performance.
