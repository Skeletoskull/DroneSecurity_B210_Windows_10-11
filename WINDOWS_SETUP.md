# Windows Setup Guide - USRP B210 with GNU Radio

Complete guide for running DroneSecurity on Windows using USRP B210 via GNU Radio/radioconda.

## Why GNU Radio for Windows?

GNU Radio provides a complete SDR ecosystem for Windows including:
- **UHD drivers** - USRP Hardware Driver for B210
- **Python bindings** - Direct hardware access from Python
- **Pre-compiled binaries** - No manual compilation needed
- **radioconda** - All-in-one installer with dependencies

## Installation Steps

### 1. Install radioconda

radioconda is a conda distribution specifically for SDR applications.

**Download:**
- Visit: https://github.com/ryanvolz/radioconda/releases
- Download latest Windows installer (e.g., `radioconda-2024.XX.XX-Windows-x86_64.exe`)
- Run installer and follow prompts

**Default installation path:**
```
C:\Users\<YourUsername>\radioconda\
```

### 2. Verify UHD Installation

Open PowerShell and test UHD:

```powershell
# Check UHD version
C:\Users\<YourUsername>\radioconda\Scripts\conda.exe run -n base uhd_find_devices
```

**Expected output:**
```
--------------------------------------------------
-- UHD Device 0
--------------------------------------------------
Device Address:
    serial: 3189F10
    name: RIO0
    product: B210
    type: b200

[INFO] [UHD] Win32; Microsoft Visual C++ version 14.2; Boost_108200; UHD_4.6.0.0-release
```

### 3. Clone Repository

```powershell
git clone https://github.com/Skeletoskull/DroneSecurity-B210.git
cd DroneSecurity-B210
```

### 4. Install Python Dependencies

```powershell
# Activate radioconda base environment
C:\Users\<YourUsername>\radioconda\Scripts\activate.bat

# Install requirements
pip install -r requirements.txt
```

**requirements.txt includes:**
- `numpy`, `scipy` - Signal processing
- `matplotlib` - Visualization
- `bitarray`, `crcmod` - Data processing
- `hypothesis`, `pytest` - Testing

Note: `uhd` is already included in radioconda, no need to install separately.

### 5. Hardware Setup

**Connect USRP B210:**
1. Connect B210 to USB 3.0 port (blue port, not USB 2.0)
2. Connect antenna to **RX2** port (not RX1)
3. Wait for Windows to recognize device

**Verify connection:**
```powershell
conda run -n base uhd_find_devices
```

### 6. Run Diagnostics

```powershell
# Detect hardware
python src\detect_hardware.py

# Run B210 diagnostics
python src\diagnose_b210.py
```

**Expected output:**
```
✓ USRP B210 is connected and ready!
  Product: B210
  Serial: 3189F10
  Sample Rate: 20000000.0 Hz
  Center Frequency: 2437000000.0 Hz
  Gain: 30 dB
```

## Running the Receiver

### Basic Usage

```powershell
# Run from radioconda environment
conda run -n base python src\droneid_receiver_live.py --gain 40
```

### Recommended Settings

**For DJI Mini 2, Mavic Air 2 (2.4 GHz only):**
```powershell
conda run -n base python src\droneid_receiver_live.py --gain 40 --band-2-4-only
```

**For legacy drones (Mavic Pro, Mavic 2):**
```powershell
conda run -n base python src\droneid_receiver_live.py --gain 50 --legacy
```

**With file saving (for debugging):**
```powershell
conda run -n base python src\droneid_receiver_live.py --gain 40 --save-files
```

### Creating a Batch File

For easier execution, create `run_receiver.bat`:

```batch
@echo off
C:\Users\<YourUsername>\radioconda\Scripts\conda.exe run -n base python src\droneid_receiver_live.py --gain 40 --band-2-4-only
pause
```

Then simply double-click `run_receiver.bat` to start.

## Performance Tuning

### Windows Limitations

| Parameter | Windows | Linux |
|-----------|---------|-------|
| Max Sample Rate | 20 MHz | 50-56 MHz |
| USB Stability | Moderate | Excellent |
| Detection Speed | 10-30s | 5-15s |

**Why the difference?**
- Windows USB stack has higher latency
- No real-time kernel support
- Background processes interfere

### Optimization Tips

**1. Reduce USB load:**
```powershell
# Lower sample rate
conda run -n base python src\droneid_receiver_live.py --sample_rate 15e6
```

**2. Reduce CPU load:**
```powershell
# Fewer worker processes
conda run -n base python src\droneid_receiver_live.py --workers 1
```

**3. Disable file saving (default):**
```powershell
# Don't use --save-files flag
conda run -n base python src\droneid_receiver_live.py --gain 40
```

**4. Close background applications:**
- Close Chrome, Discord, Steam
- Disable Windows Defender real-time scanning temporarily
- Close other SDR applications (GNU Radio Companion, SDR#)

## Troubleshooting

### "No devices found" Error

**Symptoms:**
```
Configuration Error: Failed to initialize B210: LookupError: KeyError: No devices found
```

**Solutions:**

1. **Check USB connection:**
   - Use USB 3.0 port (blue port)
   - Try different USB 3.0 port
   - Avoid USB hubs

2. **Verify UHD can see device:**
   ```powershell
   conda run -n base uhd_find_devices
   ```

3. **Check Windows Device Manager:**
   - Open Device Manager
   - Look for "Universal Software Radio Peripheral"
   - If yellow warning, update driver

4. **Restart device:**
   - Unplug B210
   - Wait 10 seconds
   - Plug back in

5. **Run from radioconda environment:**
   ```powershell
   # WRONG - won't work
   python src\droneid_receiver_live.py
   
   # CORRECT - works
   conda run -n base python src\droneid_receiver_live.py
   ```

### USB Overflow Warnings

**Symptoms:**
```
OOOOOOOOOO
```

**Explanation:**
- "O" = USB overflow (samples dropped)
- Normal on Windows at high sample rates
- System continues to work but with reduced performance

**Solutions:**
1. Lower sample rate: `--sample_rate 15e6`
2. Use USB 3.0 port directly on motherboard
3. Close background applications
4. For best performance, use Linux

### No Packets Detected

**Symptoms:**
```
Scanning 2437.0 MHz...
No packets detected
```

**Solutions:**

1. **Verify drone is flying:**
   - DroneID only transmits during flight
   - Power on + takeoff required

2. **Increase gain:**
   ```powershell
   conda run -n base python src\droneid_receiver_live.py --gain 55
   ```

3. **Check antenna:**
   - Connected to RX2 port (not RX1)
   - Antenna covers 2.4 GHz
   - Antenna not damaged

4. **Use spectrum analyzer:**
   ```powershell
   conda run -n base python src\spectrum_analyzer.py -f 2459.5 -g 50
   ```
   - Look for signal spikes
   - Adjust frequency if needed

5. **Try legacy mode:**
   ```powershell
   conda run -n base python src\droneid_receiver_live.py --gain 50 --legacy
   ```

6. **Move closer to drone:**
   - Within 50 meters line-of-sight
   - Outdoor environment preferred

### CRC Errors

**Symptoms:**
```
## Drone-ID Payload ##
{...}
CRC error!
```

**Explanation:**
- Packet detected but corrupted
- Signal too weak or too strong

**Solutions:**

1. **Signal too weak:**
   - Increase gain: `--gain 55`
   - Move closer to drone

2. **Signal too strong:**
   - Decrease gain: `--gain 25`
   - Move away from drone

3. **Interference:**
   - Test outdoors away from WiFi
   - Avoid indoor environments

### High CPU Usage

**Symptoms:**
- CPU at 100%
- System sluggish

**Solutions:**

1. **Reduce workers:**
   ```powershell
   conda run -n base python src\droneid_receiver_live.py --workers 1
   ```

2. **Reduce sample rate:**
   ```powershell
   conda run -n base python src\droneid_receiver_live.py --sample_rate 15e6
   ```

3. **Disable debug output:**
   ```powershell
   # Don't use --debug or --verbose flags
   conda run -n base python src\droneid_receiver_live.py --gain 40
   ```

## Environment Variables

Add radioconda to PATH for easier access:

**PowerShell:**
```powershell
$env:PATH += ";C:\Users\<YourUsername>\radioconda\Scripts"
```

**System Environment Variables:**
1. Open "Edit environment variables"
2. Edit "Path" variable
3. Add: `C:\Users\<YourUsername>\radioconda\Scripts`
4. Restart PowerShell

Then you can run:
```powershell
conda run -n base python src\droneid_receiver_live.py
```

## Testing Offline Decoder

Test without hardware using sample files:

```powershell
# Test with Mini 2 sample
python src\droneid_receiver_offline.py -i samples\mini2_sm

# Test with Mavic Air 2 sample
python src\droneid_receiver_offline.py -i samples\mavic_air_2

# With debug visualization
python src\droneid_receiver_offline.py -i samples\mini2_sm --debug
```

## Next Steps

- Read [QUICKSTART_B210.md](QUICKSTART_B210.md) for detailed usage
- Check [HARDWARE_COMPARISON.md](HARDWARE_COMPARISON.md) for performance data
- See [DRONEID_SIGNAL_PROCESSING.md](DRONEID_SIGNAL_PROCESSING.md) for technical details

## Support

For issues specific to:
- **UHD/radioconda:** https://github.com/ryanvolz/radioconda/issues
- **This project:** https://github.com/Skeletoskull/DroneSecurity-B210/issues
- **Original research:** https://github.com/RUB-SysSec/DroneSecurity

---

**Tested on:** Windows 11 with USRP B210 (Serial: 3189F10) via radioconda 2024.10.0
