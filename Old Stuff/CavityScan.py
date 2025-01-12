import time
#!/usr/bin/env python3

# Setup Import
import sys
import redpitaya_scpi as scpi
import matplotlib.pyplot as plot
import matplotlib.animation as animation
import numpy as np
import scipy as scipy
from scipy.signal import find_peaks
from scipy.ndimage import label

IP = "rp-f0ad99.local"
rp_s = scpi.scpi(IP)

# Set Paramaters
wave_form = 'TRIANGLE'
freq = 500
ampl = 1
trigger_level = .5
decimation = 8 # A declimation of 8 results in 15.5MS/s, and a buffer length of 1.049ms
##Set target time difference in 
target_sample_diff = 7000

rp_s.tx_txt('GEN:RST')

rp_s.tx_txt('SOUR1:FUNC ' + str(wave_form).upper())
rp_s.tx_txt('SOUR1:FREQ:FIX ' + str(freq))
rp_s.tx_txt('SOUR1:VOLT ' + str(ampl))

# Enable output
rp_s.tx_txt('OUTPUT1:STATE ON')
rp_s.tx_txt('SOUR1:TRig:INT')

# Enable Inputs
rp_s.tx_txt('ACQ:RST') # Reset acquisition setting to default
rp_s.tx_txt('ACQ:DATA:FORMAT ASCII') # Configure data to be sent as text
rp_s.tx_txt('ACQ:DATA:Units VOLTS') # Set units
rp_s.tx_txt('ACQ:DEC ' + str(decimation)) # Set Decimation factor
rp_s.tx_txt('ACQ:TRig:LEV '+ str(trigger_level)) # Set trigger level

try:
    rp_s.tx_txt('ACQ:START') # Start Aquisiton
    rp_s.tx_txt('ACQ:TRig CH2_PE') # Set tigger source to channel 2, on a postive edge

    # Wait for Trigger with timeout
    start_time = time.time()
    while time.time() - start_time < 5:  # 5 seconds timeout
        rp_s.tx_txt('ACQ:TRig:STAT?')
        if rp_s.rx_txt() == 'TD':
            break
    else:
        print("Timeout waiting for trigger")
        # Handle timeout scenario

    # Wait for Buffer to Fill with timeout
    start_time = time.time()
    while time.time() - start_time < 5:  # 5 seconds timeout
        rp_s.tx_txt('ACQ:TRig:FILL?')
        if rp_s.rx_txt() == '1':
            break
    else:
        print("Timeout waiting for buffer to fill")
        # Handle timeout scenario

except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)

rp_s.tx_txt('ACQ:SOUR1:DATA?') # Save Data from Channel 1 on the Upward Slope
buff_string = rp_s.rx_txt()
buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')
data = np.array(list(map(float, buff_string)))

#Peak Detection
peaks, _= find_peaks(data, height = 0.5)
#Filter to get the Two Main Peaks
if len(peaks) > 2: 
    # Assuming there's a significant gap between the clusters
    time_threshold = 1000

    # Compute time differences between consecutive peaks
    time_diffs = np.diff(peaks)
    print(time_diffs)
    # Identify the separation points (clusters) based on the threshold
    clusters = time_diffs > time_threshold
    print(clusters)
    # Label the clusters
    labels, num_clusters = label(clusters)
    print(labels)
    print(num_clusters)
    # Add an extra cluster label for the last set of peaks
    cluster_indices = np.concatenate(([0], np.cumsum(clusters)))

    # Calculate the average peak for each cluster
    unique_clusters = np.unique(cluster_indices)
    peaks = [int(np.mean(peaks[cluster_indices == cluster])) for cluster in unique_clusters]

    # Display the averaged peaks
    print("Averaged Peaks:", peaks)
# Calculate Time Difference 
sample_dif = peaks[1] - peaks[0]
print("Sample Diff " + str(sample_dif))
error = sample_dif - target_sample_diff
print(error)

# Display Results
plot.figure(figsize=(12, 6))
plot.plot(data, label='Signal')
plot.scatter(peaks, data[peaks], color='red', label='Averaged Peaks', s=200)
plot.title('Averaged Peaks by Clusters')
plot.xlabel('Time (Sample Number)')
plot.ylabel('Amplitude')
plot.legend()
plot.show()