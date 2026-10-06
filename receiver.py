import numpy as np
import pyaudio
from noise_scanner import choose_best_frequency_pair, SAMPLE_RATE
from visualizer import plot_signal
SYNC_FREQ = 2000
BIT_DURATION = 0.15
SYNC_DURATION = 0.08
GAP_DURATION = 0.02
START_MARKER_FREQ = 9000
END_MARKER_FREQ = 9500
BIT_TONE_FRAMES = int(SAMPLE_RATE * BIT_DURATION)
BIT_READ_FRAMES = int(SAMPLE_RATE * (BIT_DURATION + GAP_DURATION))
SYNC_TONE_FRAMES = int(SAMPLE_RATE * SYNC_DURATION)
SYNC_READ_FRAMES = int(SAMPLE_RATE * (SYNC_DURATION + GAP_DURATION))
FREQ_TOLERANCE = 150
VOLUME_THRESHOLD = 0.01
def detect_frequency(audio_chunk, tone_frames):
    tone_part = audio_chunk[:tone_frames]
    n = len(tone_part)
    middle = tone_part[int(n * 0.25):int(n * 0.75)]
    fft_result = np.fft.rfft(middle)
    fft_freqs = np.fft.rfftfreq(len(middle), d=1.0 / SAMPLE_RATE)
    peak_index = np.argmax(np.abs(fft_result))
    return fft_freqs[peak_index]
def close_to(freq, target, tolerance=FREQ_TOLERANCE):
    return abs(freq - target) <= tolerance
def read_chunk(stream, size):
    raw = stream.read(size, exception_on_overflow=False)
    return np.frombuffer(raw, dtype=np.float32)
def calculate_checksum(text):
    return sum(ord(c) for c in text) % 256
def listen_for_message(freq_0, freq_1):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=SAMPLE_RATE,
                     input=True, frames_per_buffer=BIT_READ_FRAMES)
    print(f"[RX] Using frequencies: {freq_0} Hz (0), {freq_1} Hz (1)")
    print("[RX] Listening for a message... (Ctrl+C to stop)")

    try:
        while True:
            chunk = read_chunk(stream, BIT_READ_FRAMES)
            freq = detect_frequency(chunk, BIT_TONE_FRAMES)
            volume = np.abs(chunk[:BIT_TONE_FRAMES]).mean()
            if volume < VOLUME_THRESHOLD or not close_to(freq, START_MARKER_FREQ):
                continue
            print("[RX] Start marker detected. Receiving message...")
            received_chars = []
            recorded_audio = [chunk]   
            while True:
                marker_chunk = read_chunk(stream, SYNC_READ_FRAMES)
                recorded_audio.append(marker_chunk)
                marker_freq = detect_frequency(marker_chunk, SYNC_TONE_FRAMES)
                marker_volume = np.abs(marker_chunk[:SYNC_TONE_FRAMES]).mean()
                if marker_volume < VOLUME_THRESHOLD:
                    continue
                if close_to(marker_freq, END_MARKER_FREQ, tolerance=300):
                    print("[RX] End marker detected. Message complete.")
                    break
                if close_to(marker_freq, SYNC_FREQ, tolerance=300):
                    bits = ""
                    for _ in range(8):
                        bit_chunk = read_chunk(stream, BIT_READ_FRAMES)
                        recorded_audio.append(bit_chunk)
                        bit_freq = detect_frequency(bit_chunk, BIT_TONE_FRAMES)
                        if close_to(bit_freq, freq_1):
                            bits += "1"
                        else:
                            bits += "0"
                    char = chr(int(bits, 2))
                    received_chars.append(char)
                    print(f"[RX] Character received: {char!r}  (bits: {bits})")
            if len(received_chars) < 1:
                print("[RX] Nothing usable received.")
                continue
            message = ''.join(received_chars[:-1])
            received_checksum = ord(received_chars[-1]) if received_chars else None
            expected_checksum = calculate_checksum(message)
            print(f"[RX] Decoded message: {message}")
            if received_checksum == expected_checksum:
                print("[RX] Checksum OK - message verified correct.")
                if message.startswith("FILE:"):
                    try:
                        _, filename, file_content = message.split(":", 2)
                        with open(f"received_{filename}", "w", encoding="utf-8") as f:
                            f.write(file_content)
                        print(f"[RX] File saved as: received_{filename}")
                    except Exception as e:
                        print(f"[RX] Could not save file: {e}")
            else:
                print(f"[RX] CHECKSUM MISMATCH! (expected {expected_checksum}, got {received_checksum}) "
                      f"- message may be corrupted.")
            print("[RX] Opening waveform graph... (close the graph window to keep listening)")
            full_audio = np.concatenate(recorded_audio)
            plot_signal(full_audio, SAMPLE_RATE, title=f"Received Signal: '{message}'")
    except KeyboardInterrupt:
        print("\n[RX] Stopped listening.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
if __name__ == "__main__":
    freq_0, freq_1 = choose_best_frequency_pair()
    listen_for_message(freq_0, freq_1)