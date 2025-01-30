#!/usr/bin/env python3
import socket
import time
import sys
import json
import struct
import redpitaya_scpi as scpi
from scpi_interface import setup_redpitaya, acquire_data, output_feedback_voltage
from calculations import detect_peaks, calculate_sample_differences, calculate_error_correction


# Load configuration from JSON file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Set Parameters
trigger_level = config["trigger_level"]
decimation = config["decimation"]
target_sample_diff = config["target_sample_diff"]
gain = config["gain"]
feedback = config["feedback"]
use_server = config["use_server"]

# Use localhost IP for onboard execution
IP = config["IP"]
rp_s = scpi.scpi(IP)

# Setup Red Pitaya
setup_redpitaya(rp_s, trigger_level, decimation)

if use_server:
    print("Server functionality is enabled")
    try:
        # Set up socket communication
        SERVER_IP = config["server_ip"]  # Replace with your server's IP (User Ethernet Adapter, and not Ethernet 4)
        SERVER_PORT = config["server_port"]

        # Create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((SERVER_IP, SERVER_PORT))
        except socket.error as e:
            print(f"Socket connection error: {e}")
            sys.exit(1)

        server_send_rate = config["server_send_rate"]
        send_counter = config["server_send_rate"]
        send_data = True
        while True:
            tic = time.perf_counter()

            # Acquire Data
            data1, data2 = acquire_data(rp_s)

            # Detect Peaks
            peaks1 = detect_peaks(data1, )
            peaks2 = detect_peaks(data2)

            # Calculate Time Difference
            sample_differences = calculate_sample_differences(peaks1, peaks2)

            # Error handeling if sample_difference returns None; if the sample_difference contintues to not be found, the program will exit
            if sample_differences == None:
                time.sleep(2)
                for attempt in range(5):    # Adjust the number of retrys as needed
                    data1, data2 = acquire_data(rp_s)
                    peaks1 = detect_peaks(data1, )
                    peaks2 = detect_peaks(data2)
                    sample_differences = calculate_sample_differences(peaks1, peaks2)
                    if sample_differences is not None:
                        break
                    time.sleep(1)
            if sample_differences is None:
                print("Failed to calculate sample differences after 5 attempts. Exiting program.")
                sys.exit(1)

            # Calculate Error Correction
            feedback = calculate_error_correction(sample_differences, target_sample_diff, gain, feedback)

            # Output the feedback voltage
            voltage = output_feedback_voltage(rp_s, feedback)

            toc = time.perf_counter()
            print(f"Time {toc - tic:0.4f} seconds")
            if send_counter == 0:
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
                send_counter = server_send_rate
            else:
                send_counter -= 1


    except KeyboardInterrupt:
        print("Scanning stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        client_socket.close()

else:
    print("Server functionality is disabled.")

    while True:
            tic = time.perf_counter()
            # Acquire Data
            data1, data2 = acquire_data(rp_s)

            # Detect Peaks
            peaks1 = detect_peaks(data1, )
            peaks2 = detect_peaks(data2)

            # Calculate Time Difference
            sample_differences = calculate_sample_differences(peaks1, peaks2)

            # Error handeling if sample_difference returns None; if the sample_difference contintues to not be found, the program will exit
            if sample_differences == None:
                time.sleep(2)
                for attempt in range(5):    # Adjust the number of retrys as needed
                    data1, data2 = acquire_data(rp_s)
                    peaks1 = detect_peaks(data1, )
                    peaks2 = detect_peaks(data2)
                    sample_differences = calculate_sample_differences(peaks1, peaks2)
                    if sample_differences is not None:
                        break
                    time.sleep(1)
            if sample_differences is None:
                print("Failed to calculate sample differences after 5 attempts. Exiting program.")
                sys.exit(1)

            # Calculate Error Correction
            feedback = calculate_error_correction(sample_differences, target_sample_diff, gain, feedback)

            # Output the feedback voltage
            voltage = output_feedback_voltage(rp_s, feedback)