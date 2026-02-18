# DroneSecurity - Windows Port with USRP B210 Support

<p align="center">
  <img src="./img/result.png" width="600" alt="Decoded DroneID Payload">
</p>

**Windows-compatible fork** of [RUB-SysSec/DroneSecurity](https://github.com/RUB-SysSec/DroneSecurity) with USRP B210 support via GNU Radio/UHD.

This receiver decodes DJI's proprietary DroneID protocol (OcuSync 2.0) to extract real-time telemetry including GPS coordinates, altitude, velocity, and serial numbers from DJI drones.

## 🎯 Key Features

- ✅ **Windows Support** - Full Windows 10/11 compatibility using GNU Radio/radioconda
- ✅ **USRP B210** - Primary SDR with superior performance (2-3x faster than BladeRF A4)
- ✅ **BladeRF A4** - Legacy support maintained
- ✅ **Live & Offline** - Real-time reception or post-processing of captures
- ✅ **Multi-drone** - Supports Mini 2, Mavic Air 2, Mavic 3, and legacy models

## 📖 Original Research

Based on NDSS 2023 paper: [Drone Security and the Mysterious Case of DJI's DroneID](https://www.ndss-symposium.org/wp-content/uploads/2023/02/ndss2023_f217_paper.pdf)

## 🚀 Quick Start

### Prerequisites

**Hardware:**
- USRP B210 SDR (recommended) or BladeRF A4
- USB 3.0 port
- Antenna covering 2.4 GHz and/or 5.8 GHz

**Software:**
- Windows 10/11 or Linux
- Python 3.8+
- GNU Radio / radioconda (for USRP B210)

### Installation

**1. Install GNU Radio with UHD support:**

Download and install [radioconda](https://github.com/ryanvolz/radioconda/releases) which includes UHD drivers and all dependencies.

**2. Clone this repository:**

```bash
git clone https://github.com/Skeletoskull/DroneSecurity-B210.git
cd DroneSecurity-B210
```

**3. Install Python dependencies:**

```bash
# Activate radioconda environment
C:\Users\<YourUsername>\radioconda\Scripts\activate.bat

# Install requirements
pip install -r requirements.txt
```

**4. Verify hardware:**

```bash
# Check if B210 is detected
conda run -n base uhd_find_devices

# Run diagnostics
python src/detect_hardware.py
python src/diagnose_b210.py
```

### Running the Receiver

**Live reception (USRP B210):**

```bash
# Run from radioconda environment
conda run -n base python src/droneid_receiver_live.py --gain 40
```

**Offline decoding (test with sample):**

```bash
python src/droneid_receiver_offline.py -i samples/mini2_sm
```

## 📊 Hardware Comparison

| Feature | BladeRF A4 | USRP B210 |
|---------|-----------|-----------|
| Detection Speed | 30-60s | 10-30s ⚡ |
| Frequency Settling | 100ms | 50ms ⚡ |
| Gain Range | 0-60 dB | 0-76 dB ⚡ |
| Max Sample Rate | 40 MHz | 56 MHz ⚡ |
| Windows Support | Native | Via GNU Radio |

## 🎛️ Command-Line Options

```bash
python src/droneid_receiver_live.py [OPTIONS]

Options:
  --gain GAIN              RX gain in dB (default: 30, range: 0-76 for B210)
  --sample_rate RATE       Sample rate in Hz (default: 20e6)
  --workers N              Parallel worker processes (default: 2)
  --duration SECS          Capture duration per frequency (default: 0.5)
  --legacy                 Support Mavic Pro, Mavic 2 (older drones)
  --save-files             Enable file saving (disabled by default)
  --band-2-4-only          Only scan 2.4 GHz band (default: True)
  --debug                  Enable debug output and visualization
  --verbose                Show detailed processing stages
```

## 📁 Project Structure

```
DroneSecurity-B210/
├── src/
│   ├── droneid_receiver_live.py      # Live SDR receiver
│   ├── droneid_receiver_offline.py   # Offline decoder
│   ├── usrp_b210_receiver.py         # USRP B210 driver
│   ├── bladerf_receiver.py           # BladeRF A4 driver
│   ├── spectrum_analyzer.py          # Spectrum visualization
│   ├── frequency_scanner.py          # Multi-band scanner
│   └── droneid_packet.py             # Packet parser
├── tests/                            # Unit tests
├── samples/                          # Sample captures
├── img/                              # Documentation images
└── requirements.txt                  # Python dependencies
```

## 🔧 Troubleshooting

**"No devices found" error:**
- Ensure B210 is connected to USB 3.0 port
- Run from radioconda environment: `conda run -n base python ...`
- Verify with: `conda run -n base uhd_find_devices`

**No packets detected:**
- Increase gain: `--gain 50` or `--gain 55`
- Verify drone is powered on
- Check antenna is connected to RX2 port
- Use spectrum analyzer: `python src/spectrum_analyzer.py -f 2459.5 -g 50`

**USB overflow warnings:**
- Normal on Windows due to USB stack limitations
- Reduce sample rate: `--sample_rate 25e6`
- Use Linux for best performance (50 MHz stable)

## 📚 Documentation

- [QUICKSTART_B210.md](QUICKSTART_B210.md) - Detailed setup guide
- [HARDWARE_COMPARISON.md](HARDWARE_COMPARISON.md) - SDR performance comparison
- [DRONEID_SIGNAL_PROCESSING.md](DRONEID_SIGNAL_PROCESSING.md) - Technical details
- [B210_MIGRATION_COMPLETE.md](B210_MIGRATION_COMPLETE.md) - Migration notes

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/test_signal_processing.py
pytest tests/test_bladerf_receiver.py
```

## 🤝 Contributing

This is a research tool. Contributions welcome for:
- Bug fixes
- Documentation improvements
- Additional SDR hardware support
- Performance optimizations

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 🙏 Credits

- **Original Research:** RUB-SysSec team (NDSS 2023)
- **Original Repository:** [RUB-SysSec/DroneSecurity](https://github.com/RUB-SysSec/DroneSecurity)
- **Windows Port & B210 Support:** Skeletoskull

## 📖 Citation

```bibtex
@inproceedings{schiller2023drone,
  title={Drone Security and the Mysterious Case of DJI's DroneID},
  author={Schiller, Nico and Chlosta, Merlin and Schloegel, Moritz and Bars, Nils and Eisenhofer, Thorsten and Scharnowski, Tobias and Domke, Felix and Sch{\"o}nherr, Lea and Holz, Thorsten},
  booktitle={Network and Distributed System Security Symposium (NDSS)},
  year={2023}
}
```

## ⚠️ Disclaimer

This software is for **research and educational purposes only**. Users are responsible for complying with local laws and regulations regarding radio frequency monitoring and privacy.

---

**Status:** ✅ Tested on Windows 10 and 11 with USRP B210 via GNU Radio/radioconda
