# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-02-18

### Added
- **USRP B210 support** - Full Windows and Linux support via UHD/GNU Radio
- **Windows compatibility** - Native Windows 10/11 support using radioconda
- **GNU Radio integration** - Seamless integration with GNU Radio ecosystem
- **Comprehensive testing** - Unit tests for all major components
- **Hardware detection** - Automatic SDR hardware detection and diagnostics
- **Spectrum analyzer** - Real-time spectrum visualization tool
- **Frequency scanner** - Multi-band scanning with frequency locking
- **Performance optimizations** - 2-3x faster detection vs BladeRF A4

### Changed
- **Refactored receiver architecture** - Modular hardware abstraction layer
- **Improved error handling** - Better diagnostics and user feedback
- **Updated documentation** - Comprehensive Windows setup guide
- **Optimized signal processing** - Faster STFT and packet detection

### Fixed
- **Path handling** - Cross-platform path compatibility using pathlib
- **USB stability** - Better handling of USB overflows on Windows
- **CRC validation** - Improved packet validation and error reporting

### Documentation
- Added WINDOWS_SETUP.md - Complete Windows installation guide
- Added HARDWARE_COMPARISON.md - SDR performance comparison
- Added QUICKSTART_B210.md - Quick start guide for B210
- Updated README.md - Modern, professional documentation

## [1.0.0] - 2023-02-XX

### Initial Release
- Original DroneSecurity implementation by RUB-SysSec
- BladeRF support
- Linux-only support
- NDSS 2023 paper publication

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backwards compatible manner
- **PATCH** version for backwards compatible bug fixes

## Links

- [Original Repository](https://github.com/RUB-SysSec/DroneSecurity)
- [NDSS 2023 Paper](https://www.ndss-symposium.org/wp-content/uploads/2023/02/ndss2023_f217_paper.pdf)
