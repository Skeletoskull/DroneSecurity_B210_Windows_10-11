# Quick Reference Card

Essential commands and information for DroneSecurity-B210.

## 🚀 Quick Start Commands

### Windows (USRP B210)

```powershell
# Run live receiver
conda run -n base python src\droneid_receiver_live.py --gain 40

# Test with sample file
python src\droneid_receiver_offline.py -i samples\mini2_sm

# Check hardware
conda run -n base uhd_find_devices
python src\detect_hardware.py

# Spectrum analyzer
conda run -n base python src\spectrum_analyzer.py -f 2459.5 -g 50
```

### Linux (USRP B210)

```bash
# Run live receiver (high performance)
python3 src/droneid_receiver_live.py --gain 40 --sample_rate 50e6

# Test with sample file
python3 src/droneid_receiver_offline.py -i samples/mini2_sm

# Check hardware
uhd_find_devices
python3 src/detect_hardware.py
```

## 📡 Frequency Bands

| Band | Frequency | Drone Models |
|------|-----------|--------------|
| 2.4 GHz | 2400-2483.5 MHz | Mini 2, Air 2, Mavic 3 |
| 5.8 GHz | 5725-5850 MHz | Mavic Pro, Mavic 2 (legacy) |

**Default:** 2.4 GHz only (`--band-2-4-only`)

## 🎚️ Gain Settings

| Scenario | Recommended Gain |
|----------|------------------|
| Close range (<50m) | 25-35 dB |
| Medium range (50-100m) | 35-45 dB |
| Long range (>100m) | 45-55 dB |
| Very long range | 55-65 dB |
| Maximum sensitivity | 70-76 dB |

**Start with:** `--gain 40`

## ⚙️ Common Options

```bash
# Fast detection (2.4 GHz only)
--gain 40 --band-2-4-only

# Legacy drones (Mavic Pro, Mavic 2)
--gain 50 --legacy

# High sample rate (Linux only)
--sample_rate 50e6

# Save files for debugging
--save-files

# Reduce CPU usage
--workers 1

# Debug mode with visualization
--debug

# Verbose output
--verbose
```

## 🔍 Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| "No devices found" | Run from radioconda: `conda run -n base python ...` |
| No packets detected | Increase gain: `--gain 55` |
| CRC errors | Adjust gain (too high or too low) |
| USB overflows | Lower sample rate: `--sample_rate 15e6` |
| High CPU | Reduce workers: `--workers 1` |

## 📊 Expected Output

**Successful detection:**
```json
{
    "serial_number": "3NZCK1A0445Q5L",
    "device_type": "Mini 2",
    "latitude": 51.446866,
    "longitude": 7.267960,
    "altitude": 39.32,
    "height": 5.49,
    "app_lat": 43.268264,
    "app_lon": 6.640125,
    "crc-packet": "c935",
    "crc-calculated": "c935"
}
```

**Detection stats:**
```
Frame detection: 10 candidates
Decoder: 9 total, CRC OK: 7 (2 CRC errors)
```

## 🛠️ Hardware Ports

**USRP B210:**
- **RX2** - Connect antenna here (primary)
- RX1 - Not used
- TX1/TX2 - Not used (receive only)

**USB:**
- Use **USB 3.0** port (blue)
- Avoid USB hubs
- Prefer motherboard ports

## 📁 Output Files

When using `--save-files`:

| File | Description |
|------|-------------|
| `decoded_bits_MMDD_HHMM.bin` | Decoded packet data |
| `ext_drone_id_*.raw` | Last 10 raw packets |
| `receive_test_MMDD_HHMM.raw` | Latest capture |

**Location:** `src/` folder (or `--output-dir`)

## 🧪 Testing Commands

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_signal_processing.py

# Run with verbose output
pytest tests/ -v

# Run offline decoder test
python src/droneid_receiver_offline.py -i samples/mini2_sm
```

## 📦 Installation Quick Check

```powershell
# 1. Check radioconda
conda --version

# 2. Check UHD
conda run -n base uhd_find_devices

# 3. Check Python packages
pip list | findstr numpy scipy matplotlib

# 4. Check hardware
python src\detect_hardware.py

# 5. Run diagnostics
python src\diagnose_b210.py
```

## 🔗 Important Links

- **Original Paper:** https://www.ndss-symposium.org/wp-content/uploads/2023/02/ndss2023_f217_paper.pdf
- **Original Repo:** https://github.com/RUB-SysSec/DroneSecurity
- **radioconda:** https://github.com/ryanvolz/radioconda
- **UHD Manual:** https://files.ettus.com/manual/

## 📞 Getting Help

1. Check [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for detailed setup
2. Check [QUICKSTART_B210.md](QUICKSTART_B210.md) for usage guide
3. Check [HARDWARE_COMPARISON.md](HARDWARE_COMPARISON.md) for performance
4. Open issue on GitHub
5. Check original repo issues

## ⚡ Performance Tips

**Windows:**
- Use 20 MHz sample rate (max stable)
- Close background applications
- Use USB 3.0 port on motherboard
- Disable Windows Defender temporarily

**Linux:**
- Use 50 MHz sample rate
- Install real-time kernel for best performance
- Run with elevated priority: `sudo nice -n -20 python3 ...`

## 🎯 Supported Drones

| Drone Model | Band | Legacy Mode |
|-------------|------|-------------|
| DJI Mini 2 | 2.4 GHz | No |
| DJI Mavic Air 2 | 2.4 GHz | No |
| DJI Mavic 3 | 2.4 GHz | No |
| DJI Mavic Pro | 5.8 GHz | Yes (`--legacy`) |
| DJI Mavic 2 | 5.8 GHz | Yes (`--legacy`) |

## 📝 Quick Notes

- DroneID only transmits during flight (not when powered on ground)
- Best results outdoors with line-of-sight
- Indoor environments have multipath interference
- CRC errors are normal (expect 20-30% error rate)
- Detection time: 10-30 seconds typical

---

**Print this page for quick reference while operating!**
