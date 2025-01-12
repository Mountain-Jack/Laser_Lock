import matplotlib.pyplot as plot
import numpy as np
def initialize_plot(zero_data, zero_peaks, target_sample_diff, y_min=-.25, y_max=1.5):
    """Initializes the plot with (likely zero) data for both datasets."""
    import matplotlib.pyplot as plt

    plt.ion()
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot the first dataset
    line1, = ax.plot(zero_data, label='Signal 1', color='blue')
    scatter1 = ax.scatter(zero_peaks, zero_data[zero_peaks.astype(int)], color='red', label='Peaks 1', s=100)
    
    # Plot the second dataset
    line2, = ax.plot(zero_data, label='Signal 2', color='green')
    scatter2 = ax.scatter(zero_peaks, zero_data[zero_peaks.astype(int)], color='orange', label='Peaks 2', s=100)
    
    ax.set_title('Comparison of Two Signals with Peaks')
    ax.set_xlabel('Time (Sample Number)')
    ax.set_ylabel('Amplitude')
    ax.legend()

    # Set y-axis limits
    ax.set_ylim(y_min, y_max)

    # Highlight the target sample difference offset from the first peak
    if len(zero_peaks) > 0:
        first_peak_index = zero_peaks[0].astype(int)
        target_index = first_peak_index + target_sample_diff
        if 0 <= target_index < len(zero_data):
            ax.axvline(x=target_index, color='purple', linestyle='--', label='Target Sample Offset')
            ax.scatter(target_index, zero_data[target_index], color='purple', s=100, zorder=5)
            ax.legend()

    # Add text annotation for feedback voltage
    feedback_text = ax.text(0.05, 0.95, '', transform=ax.transAxes, fontsize=12, verticalalignment='top')

    plt.show()
    return fig, ax, line1, scatter1, line2, scatter2, feedback_text

def update_plot(fig, line1, scatter1, new_data1, new_peaks1, line2, scatter2, new_data2, new_peaks2, feedback, feedback_text, target_sample_diff):
    """Updates the plot with new data for two datasets, feedback voltage, and highlights the target sample difference."""
    
    # Update the first dataset
    line1.set_ydata(new_data1)
    offsets1 = np.column_stack((new_peaks1.astype(int), new_data1[new_peaks1.astype(int)]))
    scatter1.set_offsets(offsets1)
    
    # Update the second dataset
    line2.set_ydata(new_data2)
    offsets2 = np.column_stack((new_peaks2.astype(int), new_data2[new_peaks2.astype(int)]))
    scatter2.set_offsets(offsets2)
    
    # Update the feedback voltage text
    feedback_text.set_text(f'Feedback Voltage: {feedback} V')

    # Highlight the target sample difference offset from the first peak
    if len(new_peaks1) > 0:
        first_peak_index = new_peaks1[0].astype(int)
        target_index = first_peak_index + target_sample_diff
        if 0 <= target_index < len(new_data1):
            # Remove previous target sample markers if any
            for line in fig.gca().lines:
                if line.get_label() == 'Target Sample Offset':
                    line.remove()
            for coll in fig.gca().collections:
                if coll.get_label() == 'Target Sample Offset':
                    coll.remove()
            
            # Add new target sample marker
            fig.gca().axvline(x=target_index, color='purple', linestyle='--', label='Target Sample Offset')
            fig.gca().scatter(target_index, new_data1[target_index], color='purple', s=100, zorder=5, label='Target Sample Offset')
            fig.gca().legend()

    # Redraw the figure
    fig.canvas.draw()
    fig.canvas.flush_events()