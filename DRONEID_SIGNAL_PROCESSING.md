# DJI DroneID Signal Processing - Technical Overview

**Last Updated:** January 26, 2026

---

## Table of Contents
1. [DroneID Packet Structure](#droneid-packet-structure)
2. [RF Signal Characteristics](#rf-signal-characteristics)
3. [Signal Processing Pipeline](#signal-processing-pipeline)
4. [Detection Algorithm](#detection-algorithm)
5. [OFDM Demodulation](#ofdm-demodulation)
6. [QPSK Decoding](#qpsk-decoding)
7. [Packet Parsing](#packet-parsing)

---

## DroneID Packet Structure

### Physical Layer (RF)

```
┌─────────────────────────────────────────────────────────────┐
│                    RF Burst (650 μs)                         │
├─────────────────────────────────────────────────────────────┤
│  ZC-600  │  Data  │  Data  │  Data  │  ZC-147  │  Data ... │
│ (sync 1) │ Symbol │ Symbol │ Symbol │ (sync 2) │  Symbols  │
└─────────────────────────────────────────────────────────────┘
     ↓          ↓        ↓        ↓         ↓          ↓
  OFDM      OFDM     OFDM     OFDM      OFDM       OFDM
  Symbol    Symbol   Symbol   Symbol    Symbol     Symbols
```

**Key Parameters:**
- **Modulation:** OFDM (LTE-based)
- **Bandwidth:** ~9-10 MHz
- **Duration:** 630-665 μs (standard) or 565-600 μs (legacy)
- **Center Frequencies:** 2.4 GHz or 5.8 GHz bands
- **Symbols:** 8-9 OFDM symbols per packet

### OFDM Symbol Structure

```
┌────────────────────────────────────────────────┐
│         Single OFDM Symbol                      │
├────────────────────────────────────────────────┤
│  Cyclic    │         FFT Window (1024)         │
│  Prefix    │      (601 active carriers)        │
│  (72-80)   │                                    │
└────────────────────────────────────────────────┘
     ↓                      ↓
  Guard              Data Carriers
  Interval           (QPSK modulated)
```

**OFDM Parameters:**
- **FFT Size:** 1024 points
- **Active Carriers:** 601 (LTE standard)
- **Cyclic Prefix:** 72 samples (normal), 80 samples (first symbol)
- **Sample Rate:** 15.36 MHz (after resampling from 50 MHz)
- **Subcarrier Spacing:** 15 kHz

### Data Layer (After Demodulation)

```
┌─────────────────────────────────────────────────────────────┐
│                  DroneID Packet (91 bytes)                   │
├──────────┬──────────┬──────────────────────────────────────┤
│  Header  │  Payload │            CRC (2 bytes)             │
│ (5 bytes)│(84 bytes)│                                      │
└──────────┴──────────┴──────────────────────────────────────┘
```

### Detailed Packet Structure (91 bytes total)

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 1 | `pkt_len` | Packet length (91) |
| 1 | 1 | `unk` | Unknown field |
| 2 | 1 | `version` | Protocol version |
| 3 | 2 | `sequence_number` | Packet sequence counter |
| 5 | 2 | `state_info` | Drone state flags (16 bits) |
| 7 | 16 | `serial_number` | Drone serial number (ASCII) |
| 23 | 4 | `longitude` | Drone longitude (int32, scaled) |
| 27 | 4 | `latitude` | Drone latitude (int32, scaled) |
| 31 | 2 | `altitude` | Altitude above sea level (int16, feet) |
| 33 | 2 | `height` | Height above takeoff (int16, feet) |
| 35 | 2 | `v_north` | Velocity north (int16, cm/s) |
| 37 | 2 | `v_east` | Velocity east (int16, cm/s) |
| 39 | 2 | `v_up` | Velocity up (int16, cm/s) |
| 41 | 2 | `d_1_angle` | Unknown angle field |
| 43 | 8 | `gps_time` | GPS timestamp (uint64, milliseconds) |
| 51 | 4 | `app_lat` | Operator latitude (int32, scaled) |
| 55 | 4 | `app_lon` | Operator longitude (int32, scaled) |
| 59 | 4 | `longitude_home` | Home point longitude (int32, scaled) |
| 63 | 4 | `latitude_home` | Home point latitude (int32, scaled) |
| 67 | 1 | `device_type` | Drone model ID (see lookup table) |
| 68 | 1 | `uuid_len` | UUID length |
| 69 | 20 | `uuid` | Unique identifier (ASCII) |
| 89 | 2 | `crc` | CRC-16 checksum |

**Coordinate Scaling:**
```
Actual Latitude/Longitude = Raw Value / 174533.0
```

**State Info Flags (16 bits):**
```
Bit 15: Altitude valid
Bit 14: GPS valid
Bit 13: In air
Bit 12: Motor on
Bit 11: UUID set
Bit 10: Home point set
Bit 9:  Private mode disabled
Bit 8:  Serial number valid
Bits 0-7: Reserved/Unknown
```

---

## RF Signal Characteristics

### Frequency Bands

**2.4 GHz Band (Most Common):**
- 2414.5 MHz
- 2429.5 MHz
- 2434.5 MHz
- 2444.5 MHz
- **2459.5 MHz** ← Most common
- 2474.5 MHz

**5.8 GHz Band (Less Common):**
- 5721.5 - 5831.5 MHz (10 frequencies)

### Signal Properties

```
Power Spectrum:
    ^
    │     ┌─────────────┐
    │     │             │
    │     │   ~10 MHz   │
    │     │   bandwidth │
    │     │             │
    │─────┘             └─────
    └──────────────────────────> Frequency
         Center ± 5 MHz
```

**Distinguishing Features:**
- **Bandwidth:** 8-12 MHz (narrower than WiFi's 20 MHz)
- **Duration:** 630-665 μs bursts (very short)
- **Repetition:** Periodic bursts every ~100-200 ms
- **Power:** Typically -40 to -80 dBm at receiver

---

## Signal Processing Pipeline

### Complete Flow (IQ Samples → JSON Output)

```
┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: RF ACQUISITION                                      │
├─────────────────────────────────────────────────────────────┤
│  USRP B210 → IQ Samples (complex64, 20-50 MHz)             │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 2: PACKET DETECTION (SpectrumCapture)                 │
├─────────────────────────────────────────────────────────────┤
│  • STFT (Short-Time Fourier Transform)                      │
│  • Power analysis in time-frequency domain                   │
│  • Detect bursts matching 630-665 μs duration               │
│  • Filter by bandwidth (8-12 MHz)                           │
│  • Extract candidate packets                                 │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 3: COARSE FREQUENCY CORRECTION (SpectrumCapture)      │
├─────────────────────────────────────────────────────────────┤
│  • Welch PSD (Power Spectral Density)                       │
│  • Estimate carrier frequency offset (CFO)                  │
│  • Shift signal to baseband (frequency mixing)              │
│  • Resample: 50 MHz → 15.36 MHz                            │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 4: OFDM DEMODULATION (Packet class)                   │
├─────────────────────────────────────────────────────────────┤
│  • Find packet start (cyclic prefix correlation)            │
│  • Estimate fine frequency offset (FFO)                     │
│  • Extract OFDM symbols (remove cyclic prefix)              │
│  • 1024-point FFT per symbol                                │
│  • Extract 601 active carriers                              │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 5: SYNCHRONIZATION (Packet class)                     │
├─────────────────────────────────────────────────────────────┤
│  • Detect Zadoff-Chu sequences (ZC-600, ZC-147)            │
│  • Correlation with known ZC sequences                       │
│  • Estimate channel response from ZC symbols                │
│  • Equalize data symbols (channel correction)               │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 6: QPSK DEMODULATION (Decoder class)                  │
├─────────────────────────────────────────────────────────────┤
│  • Brute-force 4 phase alignments (0°, 90°, 180°, 270°)   │
│  • Map QPSK symbols to bits (2 bits per symbol)            │
│  • Descramble using Gold sequence (seed: 0x12345678)       │
│  • Turbo decode (3GPP LTE turbo decoder)                   │
│  • Find DUML magic bytes (DJI protocol marker)             │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 7: PACKET PARSING (DroneIDPacket class)               │
├─────────────────────────────────────────────────────────────┤
│  • Unpack 91-byte structure                                 │
│  • Validate CRC-16 (poly: 0x11021, init: 0x3692)          │
│  • Scale coordinates (divide by 174533.0)                   │
│  • Convert units (feet → meters)                            │
│  • Lookup device type from ID                               │
│  • Format as JSON                                           │
└────────────────────────┬────────────────────────────────────┘
                         ▼
                   JSON Output
```

---

## Detection Algorithm

### Stage 2: Packet Detection (SpectrumCapture.py)

**Goal:** Find DroneID bursts in continuous IQ stream

**Method:** STFT-based time-frequency analysis

```python
# Pseudocode
def detect_packets(iq_samples, sample_rate):
    # 1. Compute STFT (Short-Time Fourier Transform)
    f, t, Zxx = stft(iq_samples, 
                     fs=sample_rate,
                     nperseg=64,      # FFT size
                     noverlap=0)      # No overlap for speed
    
    # 2. Calculate power in time-frequency domain
    power = np.abs(Zxx) ** 2
    
    # 3. Find time bins with high power
    power_per_time = np.sum(power, axis=0)  # Sum across frequency
    threshold = np.mean(power_per_time) + 3 * np.std(power_per_time)
    
    # 4. Detect bursts
    candidates = []
    for burst in find_bursts(power_per_time > threshold):
        duration = burst.length / sample_rate
        
        # 5. Filter by duration (630-665 μs for standard drones)
        if 630e-6 <= duration <= 665e-6:
            # 6. Extract samples for this burst
            start_sample = burst.start_time * sample_rate
            end_sample = burst.end_time * sample_rate
            packet_samples = iq_samples[start_sample:end_sample]
            
            # 7. Estimate bandwidth using Welch PSD
            f, psd = welch(packet_samples, fs=sample_rate, nfft=2048)
            bandwidth = estimate_bandwidth(psd)
            
            # 8. Filter by bandwidth (8-12 MHz for DroneID)
            if 8e6 <= bandwidth <= 12e6:
                candidates.append(packet_samples)
    
    return candidates
```

**Key Parameters:**
- **STFT Window:** 64 samples (optimized for speed)
- **Overlap:** 0 samples (33% faster than 32-sample overlap)
- **Duration Filter:** 630-665 μs (standard) or 565-600 μs (legacy)
- **Bandwidth Filter:** 8-12 MHz (rejects WiFi at 20 MHz)

**Why This Works:**
- DroneID bursts are **very short** (650 μs) compared to WiFi packets (>1 ms)
- DroneID bandwidth is **narrower** (10 MHz) than WiFi (20 MHz)
- Time-frequency analysis captures both characteristics simultaneously

---

## OFDM Demodulation

### Stage 4: OFDM Symbol Extraction (Packet.py)

**Goal:** Convert time-domain IQ samples to frequency-domain symbols

```python
# Pseudocode
def demodulate_ofdm(packet_samples):
    # 1. Find packet start using cyclic prefix correlation
    cp_correlation = correlate_cyclic_prefix(packet_samples)
    packet_start = np.argmax(cp_correlation)
    
    # 2. Estimate fine frequency offset (FFO)
    # Use phase difference between repeated cyclic prefix
    ffo = estimate_fine_frequency_offset(packet_samples, packet_start)
    
    # 3. Correct frequency offset
    corrected = frequency_shift(packet_samples, -ffo)
    
    # 4. Extract OFDM symbols
    symbols = []
    position = packet_start
    
    for i, cp_length in enumerate(CP_LENGTHS):
        # Skip cyclic prefix
        position += cp_length
        
        # Extract FFT window (1024 samples)
        symbol_samples = corrected[position:position + 1024]
        
        # 5. FFT to frequency domain
        fft_result = np.fft.fft(symbol_samples, n=1024)
        
        # 6. Extract 601 active carriers (centered)
        # Carriers: [-300 to +300] around DC
        active_carriers = extract_active_carriers(fft_result, 601)
        
        symbols.append(active_carriers)
        position += 1024
    
    return symbols  # List of 8-9 symbols, each with 601 carriers
```

**Cyclic Prefix Correlation:**
```
Signal:  [... CP | DATA | CP | DATA | CP | DATA ...]
                  ↑           ↑           ↑
                  └─ CP is copy of end of DATA
                  
Correlation finds where CP matches end of symbol
→ Gives precise symbol boundaries
```

**Fine Frequency Offset Estimation:**
```
Phase difference between CP and its original:
FFO = (phase_difference / (2π)) * (sample_rate / FFT_size)
```

---

## Synchronization

### Stage 5: Zadoff-Chu Sequence Detection (Packet.py)

**Goal:** Find known synchronization sequences for channel estimation

**Zadoff-Chu (ZC) Sequences:**
- **ZC-600:** First sync sequence (coarse synchronization)
- **ZC-147:** Second sync sequence (fine synchronization)

```python
# Pseudocode
def detect_zc_sequences(ofdm_symbols):
    # 1. Generate known ZC sequences
    zc_600 = generate_zadoff_chu(root=600, length=601)
    zc_147 = generate_zadoff_chu(root=147, length=601)
    
    # 2. Correlate each symbol with ZC sequences
    zc_positions = []
    
    for i, symbol in enumerate(ofdm_symbols):
        # Correlate with ZC-600
        corr_600 = np.abs(np.correlate(symbol, zc_600))
        
        # Correlate with ZC-147
        corr_147 = np.abs(np.correlate(symbol, zc_147))
        
        # 3. Check if correlation peak is strong enough
        threshold = 1.15  # Confidence ratio
        if corr_600 > threshold * np.mean(np.abs(symbol)):
            zc_positions.append((i, 600))
        elif corr_147 > threshold * np.mean(np.abs(symbol)):
            zc_positions.append((i, 147))
    
    # 4. Validate: Must find both ZC-600 and ZC-147
    if not (600 in [z[1] for z in zc_positions] and 
            147 in [z[1] for z in zc_positions]):
        raise ValueError("ZC sequences not found")
    
    return zc_positions
```

**Channel Estimation:**
```python
def estimate_channel(received_zc, known_zc):
    # Channel response = Received / Transmitted
    channel = received_zc / known_zc
    return channel

def equalize_symbols(data_symbols, channel):
    # Correct for channel distortion
    equalized = data_symbols / channel
    return equalized
```

**Why ZC Sequences:**
- **Constant amplitude** in frequency domain
- **Perfect autocorrelation** (easy to detect)
- **Low cross-correlation** (distinguishable)
- Used in LTE for synchronization

---

## QPSK Decoding

### Stage 6: Symbol-to-Bits Conversion (qpsk.py)

**Goal:** Convert QPSK symbols to binary data

**QPSK Constellation:**
```
     Q (Imaginary)
        ↑
   01   │   00
    ●   │   ●
        │
────────┼────────→ I (Real)
        │
    ●   │   ●
   11   │   10
        │
```

**Problem:** Unknown phase rotation (0°, 90°, 180°, or 270°)

**Solution:** Brute force all 4 possibilities

```python
# Pseudocode
def decode_qpsk(equalized_symbols):
    # Try all 4 phase rotations
    for phase_rotation in [0, 90, 180, 270]:
        # 1. Rotate constellation
        rotated = equalized_symbols * np.exp(1j * phase_rotation * np.pi / 180)
        
        # 2. Map symbols to bits (2 bits per symbol)
        bits = []
        for symbol in rotated:
            # Quadrant detection
            if symbol.real > 0 and symbol.imag > 0:
                bits.extend([0, 0])  # Quadrant I
            elif symbol.real < 0 and symbol.imag > 0:
                bits.extend([0, 1])  # Quadrant II
            elif symbol.real < 0 and symbol.imag < 0:
                bits.extend([1, 1])  # Quadrant III
            else:
                bits.extend([1, 0])  # Quadrant IV
        
        # 3. Descramble using Gold sequence
        descrambled = descramble_gold(bits, seed=0x12345678)
        
        # 4. Turbo decode (error correction)
        decoded = turbo_decode(descrambled)
        
        # 5. Look for DUML magic bytes (DJI protocol marker)
        if find_duml_magic(decoded):
            return decoded  # Success!
    
    return None  # Failed all phase rotations
```

**Gold Sequence Descrambling:**
```python
def descramble_gold(bits, seed):
    # Generate Gold sequence (pseudo-random)
    gold = generate_gold_sequence(seed, length=len(bits))
    
    # XOR with received bits
    descrambled = bits ^ gold
    
    return descrambled
```

**Turbo Decoding:**
- 3GPP LTE turbo code
- Rate matching and de-interleaving
- Iterative decoding for error correction
- Significantly improves reliability

---

## Packet Parsing

### Stage 7: Binary to JSON (droneid_packet.py)

**Goal:** Extract telemetry from 91-byte packet

```python
# Pseudocode
def parse_droneid_packet(raw_bytes):
    # 1. Unpack binary structure (little-endian)
    fields = struct.unpack("<BBBHH16siihhhhhhQiiiiBB20sH", raw_bytes[0:91])
    
    # 2. Extract and scale fields
    packet = {
        "pkt_len": fields[0],
        "version": fields[2],
        "sequence_number": fields[3],
        "state_info": fields[4],
        "serial_number": fields[5].decode('utf-8').rstrip('\x00'),
        
        # Coordinates (scaled by 174533.0)
        "longitude": fields[6] / 174533.0,
        "latitude": fields[7] / 174533.0,
        
        # Altitude (feet to meters)
        "altitude": round(fields[8] / 3.281, 2),
        "height": round(fields[9] / 3.281, 2),
        
        # Velocity (cm/s)
        "v_north": fields[10],
        "v_east": fields[11],
        "v_up": fields[12],
        
        # Timestamps and positions
        "gps_time": fields[14],
        "app_lat": fields[15] / 174533.0,
        "app_lon": fields[16] / 174533.0,
        "longitude_home": fields[17] / 174533.0,
        "latitude_home": fields[18] / 174533.0,
        
        # Device type (lookup from table)
        "device_type": DRONE_TYPES.get(str(fields[19])),
        
        # UUID
        "uuid_len": fields[20],
        "uuid": fields[21].decode('utf-8').rstrip('\x00'),
        
        # CRC
        "crc_packet": "%04x" % fields[22]
    }
    
    # 3. Calculate and verify CRC
    crc_calculated = calculate_crc16(raw_bytes[0:89])
    packet["crc_calculated"] = "%04x" % crc_calculated
    packet["crc_valid"] = (packet["crc_packet"] == packet["crc_calculated"])
    
    return packet
```

**CRC-16 Validation:**
```python
def calculate_crc16(data):
    # Polynomial: 0x11021 (CRC-16-CCITT)
    # Initial value: 0x3692
    crc = crcmod.mkCrcFun(0x11021, initCrc=0x3692, rev=True)
    return crc(data)
```

---

## Summary: IQ Samples → JSON

**Complete Pipeline in One View:**

```
Raw IQ Samples (50 MHz, complex64)
    ↓ STFT + Power Analysis
Detected Bursts (630-665 μs, 8-12 MHz)
    ↓ Welch PSD + Frequency Shift
Baseband Signal (15.36 MHz, CFO corrected)
    ↓ CP Correlation + FFT
OFDM Symbols (8-9 symbols × 601 carriers)
    ↓ ZC Correlation + Channel Estimation
Equalized Symbols (channel corrected)
    ↓ QPSK Demodulation + Phase Alignment
Raw Bits (brute-force 4 rotations)
    ↓ Gold Descrambling + Turbo Decode
DUML Payload (91 bytes)
    ↓ Struct Unpack + CRC Validation
JSON Telemetry (GPS, altitude, velocity, etc.)
```

**Key Success Factors:**
1. **Timing:** 650 μs burst detection
2. **Bandwidth:** 8-12 MHz filtering (rejects WiFi)
3. **Synchronization:** ZC-600 and ZC-147 detection
4. **Phase Recovery:** Brute-force 4 QPSK rotations
5. **Error Correction:** Turbo decoding
6. **Validation:** CRC-16 checksum

**Typical Processing Time:**
- Packet detection: ~50 ms
- OFDM demodulation: ~100 ms
- QPSK decoding: ~50 ms
- **Total:** ~200 ms per packet

---

**Document Prepared By:** AI System Analysis  
**Based On:** NDSS'23 Research Paper + Source Code Analysis  
**Last Updated:** January 26, 2026
