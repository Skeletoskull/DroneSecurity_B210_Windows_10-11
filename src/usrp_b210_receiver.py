#!/usr/bin/env python3
"""USRP B210 SDR Receiver Module for DroneID Detection.

This module provides a clean interface to the USRP B210 SDR for receiving
DroneID signals using UHD (USRP Hardware Driver).

The B210 offers:
- 56 MHz instantaneous bandwidth
- Better dynamic range than BladeRF
- Lower noise figure
- Dual RX channels (we use RX2)
"""

import numpy as np
import uhd
import time
from typing import Optional, Tuple


class DeviceNotFoundError(Exception):
    """Raised when USRP B210 device is not found."""
    pass


class DeviceBusyError(Exception):
    """Raised when USRP B210 device is busy or in use."""
    pass


class ConfigurationError(Exception):
    """Raised when USRP B210 configuration fails."""
    pass


class USRPB210Receiver:
    """Interface to USRP B210 SDR for DroneID signal reception.
    
    This class provides a simplified interface to the USRP B210, handling:
    - Device initialization and configuration
    - Frequency tuning with proper settling time
    - Sample reception with error handling
    - Gain control (AGC or manual)
    
    Attributes:
        sample_rate: Sample rate in Hz (default 50 MHz)
        gain: RX gain in dB (None for AGC, 0-76 for manual)
        usrp: UHD USRP source object
        streamer: UHD RX streamer
    """
    
    def __init__(self, sample_rate: float = 50e6, gain: Optional[float] = None,
                 device_args: str = "", antenna: str = "RX2"):
        """Initialize USRP B210 receiver.
        
        Args:
            sample_rate: Sample rate in Hz (default 50 MHz, max 56 MHz for B210)
            gain: RX gain in dB (None for AGC, 0-76 for manual)
            device_args: UHD device arguments (e.g., "serial=12345")
            antenna: Antenna port to use ("RX2" recommended for B210)
            
        Raises:
            DeviceNotFoundError: If B210 is not found
            ConfigurationError: If configuration fails
        """
        self.sample_rate = sample_rate
        self.gain = gain
        self.antenna = antenna
        self.current_frequency = None
        
        # Validate sample rate (B210 supports up to 56 MHz)
        if sample_rate > 56e6:
            raise ConfigurationError(
                f"Sample rate {sample_rate/1e6:.1f} MHz exceeds B210 maximum (56 MHz)"
            )
        
        # Validate gain range (B210: 0-76 dB)
        if gain is not None and (gain < 0 or gain > 76):
            raise ConfigurationError(
                f"Gain {gain} dB is out of range. Supported range: 0 dB to 76 dB"
            )
        
        try:
            # Create USRP object
            self.usrp = uhd.usrp.MultiUSRP(device_args)
            
            # Verify it's a B210
            device_name = self.usrp.get_mboard_name()
            if "B210" not in device_name and "B200" not in device_name:
                print(f"Warning: Expected B210, found {device_name}")
            
            # Configure sample rate
            self.usrp.set_rx_rate(sample_rate, 0)
            actual_rate = self.usrp.get_rx_rate(0)
            if abs(actual_rate - sample_rate) > 1:
                print(f"Warning: Requested {sample_rate/1e6:.2f} MHz, got {actual_rate/1e6:.2f} MHz")
            
            # Configure antenna
            self.usrp.set_rx_antenna(antenna, 0)
            
            # Configure gain
            if gain is None:
                # Enable AGC
                self.usrp.set_rx_agc(True, 0)
                print(f"USRP B210 initialized: {actual_rate/1e6:.2f} MHz sample rate, AGC enabled")
            else:
                # Manual gain
                self.usrp.set_rx_agc(False, 0)
                self.usrp.set_rx_gain(gain, 0)
                actual_gain = self.usrp.get_rx_gain(0)
                print(f"USRP B210 initialized: {actual_rate/1e6:.2f} MHz sample rate, {actual_gain:.1f} dB gain")
            
            # Create RX streamer
            stream_args = uhd.usrp.StreamArgs("fc32", "sc16")
            stream_args.channels = [0]
            self.streamer = self.usrp.get_rx_stream(stream_args)
            
            # Allocate buffer for receiving samples
            self.recv_buffer = np.zeros(100000, dtype=np.complex64)
            
        except RuntimeError as e:
            if "No UHD Devices Found" in str(e):
                raise DeviceNotFoundError(
                    "USRP B210 not found. Please check USB connection and drivers."
                ) from e
            else:
                raise ConfigurationError(f"Failed to initialize B210: {e}") from e
    
    def set_frequency(self, frequency: float, settling_time: float = 0.05) -> bool:
        """Set center frequency with proper settling time.
        
        The B210 needs time for the LO to lock after frequency changes.
        We use 50ms settling time (faster than BladeRF's 100ms).
        
        Args:
            frequency: Center frequency in Hz
            settling_time: Time to wait after tuning (seconds)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Tune to frequency
            tune_request = uhd.libpyuhd.types.tune_request(frequency)
            tune_result = self.usrp.set_rx_freq(tune_request, 0)
            
            # Verify tuning
            actual_freq = self.usrp.get_rx_freq(0)
            if abs(actual_freq - frequency) > 1e3:  # 1 kHz tolerance
                print(f"Warning: Requested {frequency/1e6:.2f} MHz, tuned to {actual_freq/1e6:.2f} MHz")
            
            self.current_frequency = actual_freq
            
            # Wait for LO to settle
            time.sleep(settling_time)
            
            return True
            
        except Exception as e:
            print(f"Error setting frequency: {e}")
            return False
    
    def receive_samples(self, num_samples: int, timeout: float = 5.0) -> Optional[np.ndarray]:
        """Receive IQ samples from B210.
        
        Args:
            num_samples: Number of complex samples to receive
            timeout: Timeout in seconds
            
        Returns:
            Complex64 numpy array of IQ samples, or None on error
        """
        try:
            # Allocate output buffer
            samples = np.zeros(num_samples, dtype=np.complex64)
            
            # Set up streaming
            stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.num_done)
            stream_cmd.num_samps = num_samples
            stream_cmd.stream_now = True
            self.streamer.issue_stream_cmd(stream_cmd)
            
            # Receive samples in chunks to avoid overflow
            samples_received = 0
            metadata = uhd.types.RXMetadata()
            max_samps_per_packet = self.streamer.get_max_num_samps()
            
            while samples_received < num_samples:
                # Calculate how many samples to request this iteration
                samps_to_recv = min(max_samps_per_packet, num_samples - samples_received)
                
                # Receive chunk
                samps = self.streamer.recv(
                    samples[samples_received:samples_received + samps_to_recv],
                    metadata,
                    timeout
                )
                
                # Check for errors (suppress overflow - it's normal and expected)
                if metadata.error_code != uhd.types.RXMetadataErrorCode.none:
                    if metadata.error_code != uhd.types.RXMetadataErrorCode.overflow:
                        print(f"RX error: {metadata.strerror()}")
                    # Overflow is normal with high sample rates - silently continue
                
                samples_received += samps
                
                if samps == 0:
                    break
            
            if samples_received == 0:
                return None
            
            # Return received samples (may be less than requested)
            return samples[:samples_received].copy()
            
        except Exception as e:
            print(f"Error receiving samples: {e}")
            return None
    
    def close(self):
        """Clean up USRP resources."""
        try:
            # Stop streaming
            stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont)
            self.streamer.issue_stream_cmd(stream_cmd)
        except Exception:
            pass
        
        # USRP object will be cleaned up by Python GC
        print("USRP B210 closed")
    
    def get_device_info(self) -> dict:
        """Get B210 device information.
        
        Returns:
            Dictionary with device information
        """
        try:
            return {
                "device": self.usrp.get_mboard_name(),
                "serial": self.usrp.get_mboard_serial(),
                "sample_rate": self.usrp.get_rx_rate(0),
                "gain": self.usrp.get_rx_gain(0) if self.gain is not None else "AGC",
                "antenna": self.usrp.get_rx_antenna(0),
                "frequency": self.current_frequency,
            }
        except Exception as e:
            return {"error": str(e)}


def test_b210():
    """Test B210 receiver functionality."""
    print("Testing USRP B210 receiver...")
    
    try:
        # Initialize with AGC
        receiver = USRPB210Receiver(sample_rate=50e6, gain=None)
        
        # Print device info
        info = receiver.get_device_info()
        print("\nDevice Info:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        # Test frequency tuning
        print("\nTesting frequency tuning...")
        test_freqs = [2412e6, 2437e6, 2462e6]  # WiFi channels 1, 6, 11
        
        for freq in test_freqs:
            print(f"  Tuning to {freq/1e6:.2f} MHz...")
            if receiver.set_frequency(freq):
                print(f"    ✓ Success")
            else:
                print(f"    ✗ Failed")
        
        # Test sample reception
        print("\nTesting sample reception...")
        samples = receiver.receive_samples(100000)
        
        if samples is not None:
            print(f"  ✓ Received {len(samples)} samples")
            print(f"  Sample stats: mean={np.mean(np.abs(samples)):.3f}, max={np.max(np.abs(samples)):.3f}")
        else:
            print(f"  ✗ Failed to receive samples")
        
        # Clean up
        receiver.close()
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    test_b210()
