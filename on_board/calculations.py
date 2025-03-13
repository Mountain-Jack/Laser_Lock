import numpy as np
from scipy.signal import find_peaks
from scipy.ndimage import label

def detect_peaks(data, height, sample_threshold):
    peaks, _ = find_peaks(data, height)
 
    if len(peaks) > 2:
        # Calculate time differences between consecutive peaks
        time_diffs = np.diff(peaks)

        # Identify clusters based on sample_threshold
        clusters = time_diffs > sample_threshold
        
        # Use cumsum to identify unique clusters
        cluster_indices = np.concatenate(([0], np.cumsum(clusters)))
        # Calculate mean of peaks within each cluster
        unique_clusters = np.unique(cluster_indices)
        peaks = np.array([np.mean(peaks[cluster_indices == cluster]).astype(int) for cluster in unique_clusters])
    elif len(peaks) == 0:
        peaks = np.array([], dtype=int)  # Ensure an empty integer array is returned if no peaks are detected
    return peaks

def calculate_sample_differences(t_ref, t_s):
    # Note: t_ref is the reference laser, and t_s is the laser to be stabilized
    if len(t_ref) < 1 or len(t_s) < 1:
        print('Error: One or both peak(s) not detected')
        return None  # Not enough peaks detected in one or both datasets
    
    # Find the closest peak to the reference peak
    closest_peak = t_s[0]
    for peak in t_s:    
        diff = peak - t_ref[0] 
        if abs(diff) < abs(closest_peak - t_ref[0]):
            closest_peak = peak
    # Return sample difference between the two peaks
    sampling_difference = closest_peak - t_ref[0]
    return sampling_difference

def calculate_error_correction(sample_differences, target_sample_diff, gain, feedback):
    if sample_differences == 0:  # If only one peak is detected, feedback will not change
        return feedback
    try:
        # Calculate the error based on the difference in peaks and the target sample difference
        error = sample_differences - target_sample_diff
        # Update the feedback based on the error and gain
        new_feedback = feedback + gain * error
        # Clamp the feedback to be within -1000 and 1000
        clamped_feedback = np.clip(new_feedback, -1000, 1000)
    except TypeError:
        print("Error in calculating error correction. Setting sampling difference to 0.")
        clamped_feedback = feedback  # Return the current feedback if an error occurs
    return clamped_feedback