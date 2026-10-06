"""
Run this once to see all audio devices your laptop has registered.
This helps us pick the CORRECT microphone and speaker if the default
ones aren't working.
"""

import pyaudio

p = pyaudio.PyAudio()

print(f"\nTotal devices found: {p.get_device_count()}\n")
print("=" * 70)

for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    kind = []
    if info['maxInputChannels'] > 0:
        kind.append("INPUT (mic)")
    if info['maxOutputChannels'] > 0:
        kind.append("OUTPUT (speaker)")

    print(f"Index {i}: {info['name']}")
    print(f"   Type: {', '.join(kind)}")
    print(f"   Default Sample Rate: {info['defaultSampleRate']}")
    print("-" * 70)

print("\nDefault INPUT device (mic) Python will use:")
try:
    print("  ", p.get_default_input_device_info()['name'])
except Exception as e:
    print("   Could not find one:", e)

print("\nDefault OUTPUT device (speaker) Python will use:")
try:
    print("  ", p.get_default_output_device_info()['name'])
except Exception as e:
    print("   Could not find one:", e)

p.terminate()