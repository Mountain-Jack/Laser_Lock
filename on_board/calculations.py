import numpy as np
from scipy.signal import find_peaks
from scipy.ndimage import label

def detect_peaks(data, height=0.1, sample_threshold=1000):
    peaks, _ = find_peaks(data, height=height)
    if len(peaks) > 2:
        time_diffs = np.diff(peaks)
        clusters = time_diffs > sample_threshold
        cluster_indices = np.concatenate(([0], np.cumsum(clusters)))
        unique_clusters = np.unique(cluster_indices)
        peaks = np.array([np.mean(peaks[cluster_indices == cluster]).astype(int) for cluster in unique_clusters])
    else:
        peaks = np.array([], dtype=int)  # Ensure an empty integer array is returned if no peaks are detected
    return peaks

def calculate_sample_differences(t_ref, t_s):
    # Note: t_ref is the refrence laser, and t_s is the laser to be stabalized
    if len(t_ref) < 1 or len(t_s) < 1:
        print('Error: One or both peak(s) not detected')
        return 0  # Not enough peaks detected in one or both datasets
    
    # Calculate the difference between the first peak of each dataset
    # Ensure that sample difference is the difference between the first t_ref peak to the next t_s peak
    if t_ref[0] > t_s[0]:
        try: 
            sampling_difference = t_s[1] - t_ref[0]
        except IndexError: 
            print("Second t_s peak not detected")
            return None
    else: 
        sampling_difference = t_s[0] - t_ref[0]
    return sampling_difference

def calculate_error_correction(sample_differences, target_sample_diff, gain, feedback):
    if(sample_differences == 0):    # If only one peak is detected, feedback will not change
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
    return clamped_feedback