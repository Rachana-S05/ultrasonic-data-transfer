import numpy as np
import matplotlib.pyplot as plt
def plot_signal(audio_data, sample_rate, title="Signal", save_path=None):
    """
    Shows two graphs side by side:
    1. Waveform - the raw sound wave over time
    2. Spectrogram - which frequencies were present at each moment
       (this is the most visually impressive one for a demo - you can
       SEE the different tones as horizontal bands changing over time)
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7))
    fig.suptitle(title, fontsize=14, fontweight='bold')

    # ---- Plot 1: Waveform ----
    time_axis = np.linspace(0, len(audio_data) / sample_rate, num=len(audio_data))
    ax1.plot(time_axis, audio_data, linewidth=0.5, color='#2563eb')
    ax1.set_xlabel("Time (seconds)")
    ax1.set_ylabel("Amplitude")
    ax1.set_title("Waveform (the raw sound signal)")
    ax1.grid(True, alpha=0.3)

    # ---- Plot 2: Spectrogram ----
    ax2.specgram(audio_data, Fs=sample_rate, cmap='viridis')
    ax2.set_xlabel("Time (seconds)")
    ax2.set_ylabel("Frequency (Hz)")
    ax2.set_title("Spectrogram (you can SEE each tone as a horizontal band)")
    ax2.set_ylim(0, 12000)  # focus on the range we actually use

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=120)
        print(f"[PLOT] Saved graph to {save_path}")

    plt.show()