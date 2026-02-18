#!/usr/bin/python3
"""Hardware Detection Script - Detects connected SDR devices (USRP B210 and BladeRF).

This script helps identify which SDR hardware is currently connected to your system.
"""

import sys

def check_usrp_b210():
    """Check if USRP B210 is connected via UHD."""
    print("\n" + "="*60)
    print("Checking for USRP B210 (via UHD)...")
    print("="*60)
    
    try:
        import uhd
        print("✓ UHD library found")
        
        # Try to find USRP devices
        usrp_devices = uhd.find("")
        
        if len(usrp_devices) == 0:
            print("✗ No USRP devices found")
            return False
        
        print(f"✓ Found {len(usrp_devices)} USRP device(s):")
        for i, dev in enumerate(usrp_devices):
            print(f"\n  Device {i+1}:")
            for key, value in dev.to_dict().items():
                print(f"    {key}: {value}")
        
        # Check if any is B210
        b210_found = any('b210' in str(dev).lower() or 'b200' in str(dev).lower() 
                         for dev in usrp_devices)
        
        if b210_found:
            print("\n✓ USRP B210 detected!")
            return True
        else:
            print("\n⚠ USRP device found but may not be B210")
            return True
            
    except ImportError:
        print("✗ UHD library not installed")
        print("  Install with: conda install -c conda-forge uhd")
        return False
    except Exception as e:
        print(f"✗ Error checking USRP: {e}")
        return False


def check_bladerf():
    """Check if BladeRF is connected."""
    print("\n" + "="*60)
    print("Checking for BladeRF...")
    print("="*60)
    
    try:
        # Try osmosdr (GNU Radio)
        try:
            from gnuradio import osmosdr
            print("✓ gr-osmosdr library found")
            
            # Try to create a source to detect device
            try:
                source = osmosdr.source(args="bladerf=0")
                print("✓ BladeRF device detected via gr-osmosdr!")
                del source
                return True
            except Exception as e:
                print(f"✗ No BladeRF found via gr-osmosdr: {e}")
                return False
                
        except ImportError:
            print("✗ gr-osmosdr not installed")
            
        # Try bladeRF python bindings if available
        try:
            import bladerf
            print("✓ bladeRF Python library found")
            
            devices = bladerf.get_device_list()
            if len(devices) == 0:
                print("✗ No BladeRF devices found")
                return False
            
            print(f"✓ Found {len(devices)} BladeRF device(s):")
            for i, dev in enumerate(devices):
                print(f"  Device {i+1}: {dev}")
            return True
            
        except ImportError:
            print("✗ bladeRF Python library not installed")
            return False
            
    except Exception as e:
        print(f"✗ Error checking BladeRF: {e}")
        return False


def main():
    """Main detection routine."""
    print("\n" + "="*60)
    print("SDR Hardware Detection Tool")
    print("="*60)
    print("\nThis script will check for connected SDR devices:")
    print("  - USRP B210 (via UHD)")
    print("  - BladeRF (via gr-osmosdr or native library)")
    
    usrp_found = check_usrp_b210()
    bladerf_found = check_bladerf()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if usrp_found and bladerf_found:
        print("⚠ Both USRP B210 and BladeRF detected!")
        print("  The system may use either device depending on configuration.")
        print("\n  For B210 operation:")
        print("    python droneid_receiver_live.py --gain 40 --band-2-4-only")
        print("\n  Note: Make sure you're running the B210 version of the code.")
        
    elif usrp_found:
        print("✓ USRP B210 is connected and ready!")
        print("\n  To use B210:")
        print("    python droneid_receiver_live.py --gain 40 --band-2-4-only")
        print("\n  Expected startup message:")
        print("    'Initializing USRP B210...'")
        print("    '[INFO] [UHD] ...'")
        
    elif bladerf_found:
        print("✓ BladeRF is connected")
        print("\n  Note: BladeRF A4 has slower frequency scanning due to")
        print("        100ms settling time. B210 is recommended for faster detection.")
        print("\n  If you want to use B210 instead:")
        print("    1. Connect USRP B210 via USB 3.0")
        print("    2. Disconnect or disable BladeRF")
        print("    3. Run this script again to verify")
        
    else:
        print("✗ No SDR devices detected!")
        print("\n  Troubleshooting:")
        print("    1. Check USB connection (USB 3.0 recommended)")
        print("    2. Install required libraries:")
        print("       - For B210: conda install -c conda-forge uhd")
        print("       - For BladeRF: conda install -c conda-forge gnuradio-osmosdr")
        print("    3. Check device permissions (may need admin/sudo)")
        print("    4. Try unplugging and reconnecting the device")
    
    print("="*60 + "\n")
    
    return 0 if (usrp_found or bladerf_found) else 1


if __name__ == "__main__":
    sys.exit(main())
