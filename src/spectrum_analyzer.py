#!/usr/bin/env python3
"""Simple spectrum analyzer to see what signals are present.

This tool helps diagnose reception issues by showing the actual
spectrum being received, regardless of DroneID decoding.
"""

import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for Windows
import matplotlib.pyplot as plt
from usrp_b210_receiver import USRPB210Receiver
import sys

def analyze_spectrum(center_freq=2.45e9, sample_rate=20e6, gain=45, duration=1.0):
    """Capture and display spectrum.
    
    Args:
        center_freq: Center frequency in Hz
        sample_rate: Sample rate in Hz
        gain: RX gain in dB
        duration: Capture duration in seconds
    """
    print(f"Initializing USRP B210...")
    print(f"Center: {center_freq/1e6:.2f} MHz")
    print(f"Sample Rate: {sample_rate/1e6:.2f} MHz")
    print(f"Gain: {gain} dB")
    print(f"Duration: {duration} seconds")
    
    try:
        receiver = USRPB210Receiver(sample_rate=sample_rate, gain=gain)
    except Exception as e:
        print(f"Error initializing B210: {e}")
        return
    
    # Set frequency
    if not receiver.set_frequency(center_freq):
        print("Failed to set frequency")
        return
    
    # Capture samples
    num_samples = int(sample_rate * duration)
    print(f"\nCapturing {num_samples} samples...")
    samples = receiver.receive_samples(num_samples)
    
    if samples is None or len(samples) == 0:
        print("No samples received!")
        return
    
    print(f"Received {len(samples)} samples")
    
    # Compute power spectrum
    print("Computing FFT...")
    fft = np.fft.fftshift(np.fft.fft(samples))
    freqs = np.fft.fftshift(np.fft.fftfreq(len(samples), 1/sample_rate))
    power_db = 20 * np.log10(np.abs(fft) + 1e-10)
    
    # Compute statistics
    avg_power = np.mean(power_db)
    max_power = np.max(power_db)
    noise_floor = np.percentile(power_db, 10)
    
    print(f"\nSpectrum Statistics:")
    print(f"  Average Power: {avg_power:.1f} dB")
    print(f"  Peak Power: {max_power:.1f} dB")
    print(f"  Noise Floor (10th percentile): {noise_floor:.1f} dB")
    print(f"  Dynamic Range: {max_power - noise_floor:.1f} dB")
    
    # Find peaks
    threshold = noise_floor + 10  # 10 dB above noise floor
    peaks = power_db > threshold
    peak_freqs = freqs[peaks]
    peak_powers = power_db[peaks]
    
    if len(peak_freqs) > 0:
        print(f"\nDetected {len(peak_freqs)} signals above {threshold:.1f} dB:")
        # Group nearby peaks
        peak_groups = []
        current_group = [peak_freqs[0]]
        for i in range(1, len(peak_freqs)):
            if abs(peak_freqs[i] - current_group[-1]) < 1e6:  # Within 1 MHz
                current_group.append(peak_freqs[i])
            else:
                peak_groups.append(current_group)
                current_group = [peak_freqs[i]]
        peak_groups.append(current_group)
        
        for i, group in enumerate(peak_groups[:10]):  # Show first 10 groups
            center = np.mean(group)
            bw = (max(group) - min(group))
            abs_freq = (center_freq + center) / 1e6
            print(f"  Signal {i+1}: {abs_freq:.2f} MHz (BW: {bw/1e6:.2f} MHz, Offset: {center/1e6:+.2f} MHz)")
    else:
        print(f"\n⚠️  No signals detected above noise floor!")
        print(f"    This suggests:")
        print(f"    1. Antenna not connected")
        print(f"    2. Wrong antenna port (use RX2)")
        print(f"    3. Drone not transmitting")
        print(f"    4. Gain too low (try 50-60 dB)")
    
    # Plot spectrum
    print("\nGenerating plot...")
    plt.figure(figsize=(12, 6))
    plt.plot(freqs/1e6, power_db, linewidth=0.5)
    plt.axhline(y=noise_floor, color='r', linestyle='--', label=f'Noise Floor ({noise_floor:.1f} dB)')
    plt.axhline(y=threshold, color='g', linestyle='--', label=f'Detection Threshold ({threshold:.1f} dB)')
    plt.xlabel('Frequency Offset (MHz)')
    plt.ylabel('Power (dB)')
    plt.title(f'Spectrum at {center_freq/1e6:.2f} MHz (Gain: {gain} dB)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    print("Displaying plot... (close window to continue)")
    plt.show()
    
    receiver.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Spectrum Analyzer for USRP B210")
    parser.add_argument('-f', '--frequency', type=float, default=2450,
                       help="Center frequency in MHz (default: 2450)")
    parser.add_argument('-s', '--sample-rate', type=float, default=20,
                       help="Sample rate in MHz (default: 20)")
    parser.add_argument('-g', '--gain', type=float, default=45,
                       help="RX gain in dB (default: 45)")
    parser.add_argument('-d', '--duration', type=float, default=1.0,
                       help="Capture duration in seconds (default: 1.0)")
    
    args = parser.parse_args()
    
    analyze_spectrum(
        center_freq=args.frequency * 1e6,
        sample_rate=args.sample_rate * 1e6,
        gain=args.gain,
        duration=args.duration
    )
