import socket
import sys
import json
import struct
import numpy as np
from visualization import initialize_plot, update_plot

def receive_data_from_onboard(conn):
    # Read message length first (4 bytes)
    header_length = 4
    header = b''
    while len(header) < header_length:
        chunk = conn.recv(header_length - len(header))
        if not chunk:
            return None
        header += chunk
    message_length = struct.unpack('>I', header)[0]

    # Now read the actual message data based on the length
    data = b''
    while len(data) < message_length:
        chunk = conn.recv(message_length - len(data))
        if not chunk:
            return None
        data += chunk

    # Decode and deserialize the JSON message
    message = json.loads(data.decode('utf-8'))
    return message

SERVER_IP = '169.254.166.5'  # Listen on all interfaces
SERVER_PORT = 65432
data_slice = 2 # Set up data slice
data_size = 16384 // data_slice   #Set up data size (depends on data slice)
target_sample_diff = 1200
try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()

    print("Server listening on port", SERVER_PORT)

    conn, addr = server_socket.accept()
    print('Connected by', addr)

    zero_data = np.zeros(data_size)
    zero_peaks = np.array([], dtype=int)
    fig, ax, line1, scatter1, line2, scatter2, feedback_text = initialize_plot(zero_data, zero_peaks, target_sample_diff)

    while True:
        message = receive_data_from_onboard(conn)
        if message is None:
            break
        data1 = np.array(message['data1'])
        peaks1 = np.array(message['peaks1'], dtype=int)
        data2 = np.array(message['data2'])
        peaks2 = np.array(message['peaks2'], dtype=int)
        feedback = message['voltage']
        update_plot(fig, line1, scatter1, data1, peaks1, line2, scatter2, data2, peaks2, feedback, feedback_text, target_sample_diff)

except KeyboardInterrupt:
    print("Server stopped by user.")
    sys.exit(0)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
finally:
    conn.close()
    server_socket.close()