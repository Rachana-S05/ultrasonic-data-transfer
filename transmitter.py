
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
def generate_tone(frequency, duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    tone = 0.5 * np.sin(2 * np.pi * frequency * t)
    return tone.astype(np.float32)
def generate_silence(duration):
    return np.zeros(int(SAMPLE_RATE * duration), dtype=np.float32)
def char_to_bits(char):
    return format(ord(char), '08b')
def calculate_checksum(text):
    return sum(ord(c) for c in text) % 256
def send_message(text, freq_0, freq_1):
    print(f"[TX] Message to send: {text}")
    print(f"[TX] Using frequencies: {freq_0} Hz (0), {freq_1} Hz (1)")
    checksum = calculate_checksum(text)
    checksum_char = chr(checksum)
    full_data = text + checksum_char
    print(f"[TX] Checksum: {checksum}")
    gap = generate_silence(GAP_DURATION)
    signal = generate_tone(START_MARKER_FREQ, BIT_DURATION)
    signal = np.concatenate([signal, gap])
    for char in full_data:
        signal = np.concatenate([signal, generate_tone(SYNC_FREQ, SYNC_DURATION), gap])
        for bit in char_to_bits(char):
            freq = freq_1 if bit == '1' else freq_0
            signal = np.concatenate([signal, generate_tone(freq, BIT_DURATION), gap])
    signal = np.concatenate([signal, generate_tone(END_MARKER_FREQ, BIT_DURATION)])
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=SAMPLE_RATE, output=True)
    print("[TX] Playing sound now...")
    stream.write(signal.tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("[TX] Done sending.")
    print("[TX] Opening waveform graph... (close the graph window to continue)")
    plot_signal(signal, SAMPLE_RATE, title=f"Transmitted Signal: '{text}'")
if __name__ == "__main__":
    choice = input("Send (1) a text message or (2) a text file? Enter 1 or 2: ").strip()
    if choice == "2":
        file_path = input("Enter the path to the .txt file: ").strip()
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
        except Exception as e:
            print(f"[TX] Could not read file: {e}")
            exit()
        import os
        filename = os.path.basename(file_path)
        # Special header so the receiver knows this is a FILE, not a plain message
        message = f"FILE:{filename}:{file_content}"
        print(f"[TX] Sending file '{filename}' ({len(file_content)} characters)")
    else:
        message = input("Enter message to send: ")
    freq_0, freq_1 = choose_best_frequency_pair()
    print(f"[TX] IMPORTANT: tell the receiver these frequencies if it asks: {freq_0}, {freq_1}")
    send_message(message, freq_0, freq_1)
    