import socket
import time
import sys
import json
import struct
import threading
import redpitaya_scpi as scpi
from scpi_interface import acquire_data, output_feedback_voltage
from calculations import detect_peaks, calculate_sample_differences, calculate_error_correction

class DeviceManager:
    def __init__(self):
        # Create Variables
        self.trigger_level = 0
        self.decimation = 0
        self.data_slice = 1
        self.cluster_size = 0
        self.target_sample_diff = 0
        self.gain = 0
        self.feedback = 0
        self.SERVER_IP = ''
        self.SERVER_PORT = 0
        self.server_send_rate = 0
        self.send_counter = 0
        self.use_server = False
        self.run = True
        self.rp_s = None

        self.load_config_file()

        # Start a thread for handling user input
        self.input_thread = threading.Thread(target=self.handle_user_input)
        self.input_thread.daemon = True
        self.input_thread.start()
    
    # Main Locking Method
    def laser_lock(self, send_data):
        tic = time.perf_counter()
                
        # Acquire Data
        data1, data2 = acquire_data(self.rp_s, self.data_slice)
        # Detect Peaks
        peaks1 = detect_peaks(data1, 0.1, self.cluster_size)
        peaks2 = detect_peaks(data2, 0.1, self.cluster_size)
        # Calculate Time Difference
        sample_differences = calculate_sample_differences(peaks1, peaks2)
        # Error handling if sample_difference returns None
        if sample_differences is None:
            for attempt in range(5):
                data1, data2 = acquire_data(self.rp_s, self.data_slice)
                peaks1 = detect_peaks(data1, 0.1, self.cluster_size)
                peaks2 = detect_peaks(data2, 0.1, self.cluster_size)
                sample_differences = calculate_sample_differences(peaks1, peaks2)
                if sample_differences is not None:
                    break
        if sample_differences is None:
            print("Failed to calculate sample differences after 5 attempts. Exiting program.")
            sys.exit(1)

        # Calculate Error Correction
        self.feedback = calculate_error_correction(sample_differences, self.target_sample_diff, self.gain, self.feedback)
        print(self.target_sample_diff)
        # Output the feedback voltage
        voltage = output_feedback_voltage(self.rp_s, self.feedback)

        if send_data:
            return data1, data2, peaks1, peaks2, voltage
        else:
            return None

    def main_loop_with_server(self):
        print("Server functionality is enabled")
        client_socket = None
        try:
            # Set up socket communication
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client_socket.connect((self.SERVER_IP, self.SERVER_PORT))
            except socket.error as e:
                print(f"Socket connection error: {e}")
                sys.exit(1)

            while self.run:
                # Run Locking Scheme
                if self.send_counter == 0:
                    data1, data2, peaks1, peaks2, voltage = self.laser_lock(True)
                    # Prepare data to send
                    message = json.dumps({
                        'data1': data1.tolist(),
                        'peaks1': peaks1.tolist(),
                        'data2': data2.tolist(),
                        'peaks2': peaks2.tolist(),
                        'voltage': voltage
                    })
                    # Encode the message and get its length
                    message_bytes = message.encode('utf-8')
                    message_length = len(message_bytes)

                    # Pack the message length into 4 bytes (Big Endian)
                    header = struct.pack('>I', message_length)

                    # Send the header followed by the message
                    client_socket.sendall(header + message_bytes)
                    self.send_counter = self.server_send_rate
                else:
                    self.laser_lock(False)
                    self.send_counter -= 1
                if self.use_server:
                    break
        except KeyboardInterrupt:
            print("Scanning stopped by user.")
            sys.exit(0)
        except Exception as e:
            print(f"An error occurred: {e}")
            sys.exit(1)
        finally:
            if client_socket:
                client_socket.close()

    def main_loop_no_server(self):
        print("Server functionality is disabled.")
        while self.run:
            # Run Locking Scheme
            self.laser_lock(send_data=False)

    def load_config_file(self):
        # Load configuration from JSON file
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        # Set Parameters
        self.trigger_level = config["trigger_level"]
        self.decimation = config["decimation"]
        self.data_slice = config["data_slice"]
        self.target_sample_diff = config["target_sample_diff"]
        self.gain = config["gain"]
        self.feedback = config["feedback"]
        self.use_server = config["use_server"]
        self.SERVER_IP = config["server_ip"]
        self.SERVER_PORT = config["server_port"]
        self.server_send_rate = config["server_send_rate"]
        self.send_counter = config["server_send_rate"]
        
        self.cluster_size = 1000 / self.data_slice
        # Use localhost IP for onboard execution
        IP = config["IP"]
        self.rp_s = scpi.scpi(IP)

    # Update Parameter Functions
    def update_trigger_level(self, new_trigger_level):
        self.trigger_level = new_trigger_level
        self._update_config("trigger_level", new_trigger_level)
        print(f"trigger_level set to {new_trigger_level}")

    def update_decimation(self, new_decimation):
        self.decimation = new_decimation
        self._update_config("decimation", new_decimation)
        print(f"decimation set to {new_decimation}")

    def update_target(self, new_target_sample_diff):
        self.target_sample_diff = new_target_sample_diff
        self._update_config("target_sample_diff", new_target_sample_diff)
        print(f"target_sample_diff set to {new_target_sample_diff}")

    def update_gain(self, new_gain):
        self.gain = new_gain
        self._update_config("gain", new_gain)
        print(f"gain set to {new_gain}")

    def update_feedback(self, new_feedback):
        self.feedback = new_feedback
        self._update_config("feedback", new_feedback)
        print(f"feedback set to {new_feedback}")

    def update_server_port(self, new_server_port):
        self.SERVER_PORT = new_server_port
        self._update_config("server_port", new_server_port)
        print(f"server_port set to {new_server_port}")

    def update_server_send_rate(self, new_server_send_rate):
        self.server_send_rate = new_server_send_rate
        self._update_config("server_send_rate", new_server_send_rate)
        print(f"server_send_rate set to {new_server_send_rate}")

    # Updates the config file when there are paramater changes
    def _update_config(self, key, value):
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        config[key] = value
        with open('config.json', 'w') as config_file:
            json.dump(config, config_file, indent=4) 

    def handle_user_input(self):
        while True:
            # Example user input handling
            user_input = input("Enter command (e.g., 'update trigger_level 5' or 'get trigger_level'): ")
            command_parts = user_input.split()
            
            if len(command_parts) == 3 and command_parts[0] == 'update':
                param, value = command_parts[1], command_parts[2]
                if hasattr(self, f'update_{param}'):
                    try:
                        getattr(self, f'update_{param}')(float(value))
                    except ValueError:
                        print("Invalid value. Please enter a numeric value.")
                else:
                    print(f"Unknown parameter: {param}")
            
            elif len(command_parts) == 2 and command_parts[0] == 'get':
                param = command_parts[1]
                if hasattr(self, param):
                    print(f"{param} is {getattr(self, param)}")
                elif param == "target":
                    print(f"target is {self.target_sample_diff}")
                else:
                    print(f"Unknown parameter: {param}")
            elif len(command_parts) == 1 and command_parts[0] == "help":
                    print("\nAvailable commands:\n- Update parameters (e.g., 'update trigger_level 5')\n- Stop Program : 'stop'\n\nList of variables that can be changed: target, decimation, gain, feedback, server_port, server_send_rate\n")
            elif len(command_parts) == 1 and command_parts[0] == "help":
                    print("\nAvailable commands:\n- Update parameters (e.g., 'update trigger_level 5')\n- Stop Program : 'stop'\n\nList of variables that can be changed: target, decimation, gain, feedback, server_port, server_send_rate\n")
            elif len(command_parts) == 1 and command_parts[0] == "stop":
                    self.run = False
                    break
            else:
                print("Invalid command. Use 'update <param> <value>' or 'get <param>'.")
