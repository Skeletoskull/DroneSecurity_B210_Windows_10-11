#!/usr/bin/env python3
"""Diagnostic tool for USRP B210 SDR.

This script tests the B210 hardware and verifies it's working correctly
for DroneID reception.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from usrp_b210_receiver import USRPB210Receiver, DeviceNotFoundError, ConfigurationError


def test_device_detection():
    """Test 1: Verify B210 is detected."""
    print("\n" + "="*60)
    print("Test 1: Device Detection")
    print("="*60)
    
    try:
        receiver = USRPB210Receiver(sample_rate=50e6, gain=30)
        info = receiver.get_device_info()
        
        print("✓ USRP B210 detected successfully!")
        print(f"  Device: {info.get('device', 'Unknown')}")
        print(f"  Serial: {info.get('serial', 'Unknown')}")
        print(f"  Sample Rate: {info.get('sample_rate', 0)/1e6:.2f} MHz")
        print(f"  Antenna: {info.get('antenna', 'Unknown')}")
        
        receiver.close()
        return True
        
    except DeviceNotFoundError:
        print("✗ USRP B210 not found!")
        print("  Please check:")
        print("  - USB 3.0 connection")
        print("  - UHD drivers installed")
        print("  - Device powered on")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_frequency_tuning():
    """Test 2: Verify frequency tuning works."""
    print("\n" + "="*60)
    print("Test 2: Frequency Tuning")
    print("="*60)
    
    try:
        receiver = USRPB210Receiver(sample_rate=50e6, gain=30)
        
        # Test 2.4 GHz band (WiFi channels)
        test_frequencies = [
            (2412e6, "WiFi Channel 1"),
            (2437e6, "WiFi Channel 6"),
            (2462e6, "WiFi Channel 11"),
        ]
        
        all_passed = True
        for freq, name in test_frequencies:
            success = receiver.set_frequency(freq, settling_time=0.05)
            if success:
                actual = receiver.current_frequency
                error = abs(actual - freq) / 1e6
                print(f"✓ {name}: {freq/1e6:.2f} MHz (error: {error:.3f} MHz)")
            else:
                print(f"✗ {name}: Failed to tune")
                all_passed = False
        
        receiver.close()
        
        if all_passed:
            print("\n✓ All frequency tuning tests passed!")
        return all_passed
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_sample_reception():
    """Test 3: Verify sample reception works."""
    print("\n" + "="*60)
    print("Test 3: Sample Reception")
    print("="*60)
    
    try:
        receiver = USRPB210Receiver(sample_rate=50e6, gain=30)
        receiver.set_frequency(2437e6)  # WiFi Channel 6
        
        # Receive samples
        print("Receiving 1 million samples...")
        samples = receiver.receive_samples(1000000)
        
        if samples is None:
            print("✗ Failed to receive samples")
            receiver.close()
            return False
        
        # Analyze samples
        mean_power = np.mean(np.abs(samples))
        max_power = np.max(np.abs(samples))
        
        print(f"✓ Received {len(samples)} samples")
        print(f"  Mean power: {mean_power:.4f}")
        print(f"  Max power: {max_power:.4f}")
        
        # Check if samples look reasonable
        if mean_power < 0.001:
            print("  ⚠ Warning: Very low signal power - check antenna connection")
        elif mean_power > 0.9:
            print("  ⚠ Warning: Very high signal power - may be saturating")
        else:
            print("  Signal levels look good!")
        
        receiver.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_gain_control():
    """Test 4: Verify gain control works."""
    print("\n" + "="*60)
    print("Test 4: Gain Control")
    print("="*60)
    
    try:
        # Test manual gain
        print("Testing manual gain...")
        receiver = USRPB210Receiver(sample_rate=50e6, gain=40)
        info = receiver.get_device_info()
        print(f"✓ Manual gain: {info.get('gain', 'Unknown')} dB")
        receiver.close()
        
        # Test AGC
        print("Testing AGC...")
        receiver = USRPB210Receiver(sample_rate=50e6, gain=None)
        info = receiver.get_device_info()
        print(f"✓ AGC mode: {info.get('gain', 'Unknown')}")
        receiver.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all diagnostic tests."""
    print("\n" + "="*60)
    print("USRP B210 Diagnostic Tool")
    print("="*60)
    print("\nThis tool will test your B210 hardware for DroneID reception.")
    print("Make sure the B210 is connected via USB 3.0.\n")
    
    tests = [
        ("Device Detection", test_device_detection),
        ("Frequency Tuning", test_frequency_tuning),
        ("Sample Reception", test_sample_reception),
        ("Gain Control", test_gain_control),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except KeyboardInterrupt:
            print("\n\nTests interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Unexpected error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
        print("\nYour B210 is ready for DroneID reception.")
        print("Try running: python droneid_receiver_live.py --gain 40 --band-2-4-only")
    else:
        print("\n✗ Some tests failed!")
        print("\nPlease check:")
        print("  1. USB 3.0 connection (not USB 2.0)")
        print("  2. UHD drivers installed correctly")
        print("  3. Antenna connected to RX2 port")
        print("  4. No other software using the B210")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
