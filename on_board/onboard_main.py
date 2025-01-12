#!/usr/bin/env python3
import time
import sys
import json
import struct
import redpitaya_scpi as scpi
from scpi_interface import setup_redpitaya, acquire_data, output_feedback_voltage
from calculations import detect_peaks, calculate_sample_differences, calculate_error_correction

# Use localhost IP for onboard execution
IP = "127.0.0.1"
rp_s = scpi.scpi(IP)

# Set Parameters
trigger_level = 0  # Trigger position is at the center of the memory buffer
decimation = 8
target_sample_diff = 2000
gain = .5
feedback = 0
    
# Setup Red Pitaya
setup_redpitaya(rp_s, trigger_level, decimation)

try:
    # Set up socket communication
    import socket
    SERVER_IP = ''  # Replace with your server's IP (User Ethernet Adapter, and not Ethernet 4)
    SERVER_PORT = 65432


    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))

    while True:
        # Acquire Data
        data1, data2 = acquire_data(rp_s)

        # Detect Peaks
        peaks1 = detect_peaks(data1, )
        peaks2 = detect_peaks(data2)

        # Calculate Time Difference
        sample_differences = calculate_sample_differences(peaks1, peaks2)

        # Calculate Error Correction
        feedback = calculate_error_correction(sample_differences, target_sample_diff, gain, feedback)

        # Output the feedback voltage
        voltage = output_feedback_voltage(rp_s, feedback)

        # Prepare data to send
        message = json.dumps({
        'data1': data1.tolist(),  # Convert NumPy array to list
        'peaks1': peaks1.tolist(),  # Convert NumPy array to list
        'data2': data2.tolist(),  # Convert NumPy array to list
        'peaks2': peaks2.tolist(),  # Convert NumPy array to list
        'voltage' : voltage
        })

        # Encode the message and get its length
        message_bytes = message.encode('utf-8')
        message_length = len(message_bytes)

        # Pack the message length into 4 bytes (Big Endian)
        header = struct.pack('>I', message_length)

        # Send the header followed by the message
        client_socket.sendall(header + message_bytes)

        time.sleep(.5)  # Adjust as needed

except KeyboardInterrupt:
    print("Scanning stopped by user.")
    sys.exit(0)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
finally:
    client_socket.close()