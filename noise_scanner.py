"""
NOISE SCANNER
Listens to the room for ~1.5 seconds, measures how much noise energy
exists at several candidate frequency pairs, and picks the CLEANEST
pair to use for this transmission session.

This is the "adaptive" part of the project - instead of always using
the same fixed frequencies, the system checks the room first and
avoids frequency ranges that are currently noisy (fans, AC, chatter).

Both transmitter and receiver import this so they agree on which
frequencies to use.
"""

import numpy as np
import pyaudio

SAMPLE_RATE = 44100
SCAN_DURATION = 1.5   # seconds to listen before deciding

# Candidate frequency pairs to choose between: (freq_for_0, freq_for_1)
CANDIDATE_PAIRS = [
    (3000, 4000),
    (4500, 5500),
    (6000, 7000),
]


def measure_noise_at(frequencies, audio_data):
    """Given recorded audio, measure how much energy exists at each
    frequency (i.e. how 'noisy'/busy that frequency currently is)."""
    fft_result = np.abs(np.fft.rfft(audio_data))
    fft_freqs = np.fft.rfftfreq(len(audio_data), d=1.0 / SAMPLE_RATE)

    energies = []
    for target_freq in frequencies:
        # find the FFT bin closest to this frequency
        idx = np.argmin(np.abs(fft_freqs - target_freq))
        # look at a small window around it, not just one exact bin
        window = fft_result[max(0, idx - 5):idx + 5]
        energies.append(window.mean())

    return energies


def choose_best_frequency_pair():
    """Listen to the room, then return the (freq_0, freq_1) pair
    that currently has the LEAST background noise."""
    p = pyaudio.PyAudio()
    frames_needed = int(SAMPLE_RATE * SCAN_DURATION)
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=SAMPLE_RATE,
                     input=True, frames_per_buffer=frames_needed)

    print(f"[SCAN] Listening to room noise for {SCAN_DURATION} seconds...")
    raw = stream.read(frames_needed, exception_on_overflow=False)
    audio_data = np.frombuffer(raw, dtype=np.float32)

    stream.stop_stream()
    stream.close()
    p.terminate()

    best_pair = None
    best_score = float('inf')

    print("[SCAN] Noise level at each candidate frequency pair:")
    for freq_0, freq_1 in CANDIDATE_PAIRS:
        noise_0, noise_1 = measure_noise_at([freq_0, freq_1], audio_data)
        total_noise = noise_0 + noise_1
        print(f"   {freq_0}/{freq_1} Hz  ->  noise score: {total_noise:.5f}")

        if total_noise < best_score:
            best_score = total_noise
            best_pair = (freq_0, freq_1)

    print(f"[SCAN] Chosen frequencies: {best_pair[0]} Hz (for 0), {best_pair[1]} Hz (for 1)  "
          f"(cleanest option)")
    return best_pair


if __name__ == "__main__":
    # quick standalone test
    choose_best_frequency_pair()