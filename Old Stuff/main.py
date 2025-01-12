import sys
import redpitaya_scpi as scpi
from on_board.scpi_interface import setup_redpitaya, acquire_data
from on_board.calculations import detect_peaks, calculate_time_differences, calculate_error_correction
from server.visualization import initialize_plot, update_plot

IP = "rp-f0ad99.local"
rp_s = scpi.scpi(IP)

# Set Parameters
trigger_level = 0 #Trigger position is at the center of the memory buffer
decimation = 8
target_sample_diff = 2000
gain = 1
feedback = 0

data_size = 16384   #Set up data size (depends on decimation)
target_sample_diff = 2000
# Setup Red Pitaya
setup_redpitaya(rp_s, trigger_level, decimation)

try:
    # Acquire Data
    data1, data2 = acquire_data(rp_s)

    # Detect Peaks
    peaks1 = detect_peaks(data1)
    peaks2 = detect_peaks(data2)
    # Calculate Time Difference
    time_differences = calculate_time_differences(peaks1, peaks2)
    # Calculate_error_correction
    feedback = calculate_error_correction(time_differences, target_sample_diff, feedback, gain)
    # Plot Results
    fig, ax, line1, scatter1, line2, scatter2, feedback_text = initialize_plot(zero_data, zero_peaks, target_sample_diff)
    
    while True:
        # Acquire Data
        data1, data2 = acquire_data(rp_s)

        # Detect Peaks
        peaks1 = detect_peaks(data1)
        peaks2 = detect_peaks(data2)
        # Calculate Time Difference
        time_differences = calculate_time_differences(peaks1, peaks2)

        #calculate_error_correction
        feedback = calculate_error_correction(time_differences, target_sample_diff, gain, feedback)

        # Plot Results
        update_plot(fig, line1, scatter1, data1, peaks1, line2, scatter2, data2, peaks2, feedback, feedback_text)

except KeyboardInterrupt:
    print("Scanning stopped by user.")
    sys.exit(0)
