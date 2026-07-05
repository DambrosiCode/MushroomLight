from time import sleep

import librosa
import numpy as np

song = "./Darude - Sandstorm.wav"
# Load your audio file (downmixes to mono and resamples to 22.05kHz by default)
y, sr = librosa.load(song, sr=None)

# Estimate tempo (BPM) and get the beat frame locations
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

# Convert the beat frames to timestamps (in seconds)
beat_times = librosa.frames_to_time(beat_frames, sr=sr)

onset_env = librosa.onset.onset_strength(y=y, sr=sr,
                                         hop_length=512,
                                         aggregate=np.median)
peaks = librosa.util.peak_pick(onset_env, pre_max=3, post_max=3, pre_avg=3, post_avg=5, delta=0.5, wait=10)

times = librosa.times_like(onset_env, sr=sr, hop_length=512)
peak_times = times[peaks]


print(f"Estimated Tempo: {tempo} BPM")
print("First 10 beat timestamps (seconds):", beat_times)
import sounddevice as sd
import soundfile as sf
import time

data, samplerate = sf.read(song)

sd.play(data, samplerate)

# Give the audio thread time to actually begin
time.sleep(0.02)

start = time.perf_counter()
sd.play(data, samplerate)

beat_count = 0
serial_on = '255'
import serial

arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)
while sd.get_stream().active:
    elapsed = time.perf_counter() - start
    while beat_count < len(peak_times) and elapsed >= peak_times[beat_count]:
        print(beat_count)

        #send on data to arduino/neopixel
        if serial_on == '255':
            serial_on = '0'
            arduino.write(f"{serial_on}\n".encode())
        else:
            serial_on = '255'
            arduino.write(f"{serial_on}\n".encode())
        beat_count += 1


