import numpy as np
from scipy.signal import find_peaks
from scipy.ndimage import label

def detect_peaks(data, height=0.3, sample_threshold=1000):
    peaks, _ = find_peaks(data, height=height)
    if len(peaks) > 2:
        time_diffs = np.diff(peaks)
        clusters = time_diffs > sample_threshold
        cluster_indices = np.concatenate(([0], np.cumsum(clusters)))
        unique_clusters = np.unique(cluster_indices)
        peaks = np.array([int(np.mean(peaks[cluster_indices == cluster])) for cluster in unique_clusters])
    else:
        peaks = np.array([], dtype=int)  # Ensure an empty integer array is returned if no peaks are detected
    return peaks

def calculate_sample_differences(peaks1, peaks2):
    if len(peaks1) < 1 or len(peaks2) < 1:
        print('Error: One or both peak(s) not detected')
        return 0  # Not enough peaks detected in one or both datasets
    
    # Calculate the difference between the first peak of each dataset
    sampling_difference = peaks2[0] - peaks1[0]
    return sampling_difference

def calculate_error_correction(sample_differences, target_sample_diff, gain, feedback):
    if(sample_differences == 0):    # If only one peak is detected, feedback will not change
        return feedback
    try:
        # Calculate the error based on the difference in peaks and the target sample difference
        error = sample_differences - target_sample_diff
        print(f"sample error: {error}")
        # Update the feedback based on the error and gain
        new_feedback = feedback + gain * error
        print(f"feedback adj:{new_feedback}")
        # Clamp the feedback to be within -1000 and 1000
        clamped_feedback = np.clip(new_feedback, -1000, 1000)
        print(f"feedback post clip:{feedback}")
    except TypeError:
        print("Error in calculating error correction. Setting sampling difference to 0.")
    return clamped_feedback