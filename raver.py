import os
import random

import sounddevice as sd
import soundfile as sf
import time

import librosa
import numpy as np
import serial

import threading

class Raver:
    def __init__(self):
        self.thread = None
        self.stop_event = threading.Event()
        self.data = None
        self.samplerate = None
        self.arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)

    def set_song(self, song):
        # Play music
        self.data, self.samplerate = sf.read(song)

    def stop_music(self):
        self.stop_event.set()
        sd.stop()

    def play_music(self, song):
        self.stop_music()  # stop previous song
        self.stop_event.clear()

        self.thread = threading.Thread(
            target=self._play_worker,
            args=(song,),
            daemon=True,
        )
        self.thread.start()

    def set_color(self, R, G, B, brightness=1, mode=0):
        self.arduino.write(f"{brightness},{mode},{R},{G},{B}\n".encode())

    def set_rainbow(self, brightness, mode):
        self.arduino.write(f"{brightness},{mode},{0},{0},{0}\n".encode())

    def _play_worker(self, song):
        print(f"starting {song}")
        f_name = song.replace(".wav", ".txt")
        peak_times = []
        # if song has already been analysed load it
        if not os.path.exists(f_name):
            print(f'generating {f_name}')
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

            with open(f_name, 'w') as f:
                for line in peak_times:
                    f.write("%s\n" % line)
        else:
            print(f"loading {f_name}")
            with open(f_name, 'r') as f:
                peak_times = [float(line) for line in f.read().splitlines()]



        self.set_song(song)
        data = self.data
        samplerate = self.samplerate

        # Give the audio thread time to actually begin
        start = time.perf_counter()
        sd.play(data, samplerate)

        beat_count = 0

        off_beat = 0
        off_beat_count = 0

        while sd.get_stream().active and not self.stop_event.is_set():
            elapsed = time.perf_counter() - start
            while beat_count < len(peak_times) and elapsed >= peak_times[beat_count]:
                mode = random.choice(['RGB', 'RAINBOW'])
                #send on data to arduino/neopixel
                if off_beat_count == off_beat and off_beat != 0:
                    brightness = 0
                    off_beat_count = 0
                else:
                    off_beat_count += 1
                    brightness = 1

                if mode == 'RGB':
                    mode = 0
                    r = random.randint(0, 255)*brightness
                    g = random.randint(0, 255-r)*brightness
                    b = random.randint(0, 255-g)*brightness
                    self.set_color(r, g, b, brightness, mode)
                    print(f"{brightness},{mode},{r},{g},{b}\n".encode())
                elif mode == 'RAINBOW':
                    mode = 1
                    self.set_rainbow(brightness, mode)

                beat_count += 1
            time.sleep(0.001)

