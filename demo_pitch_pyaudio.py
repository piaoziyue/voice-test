import pyaudio
import sys
import numpy as np
import aubio
import time
from matplotlib import pyplot as plt

# initialise pyaudio
p = pyaudio.PyAudio()

# open stream
buffer_size = 1024
pyaudio_format = pyaudio.paFloat32
n_channels = 1
samplerate = 44100
stream = p.open(format=pyaudio_format,
                channels=n_channels,
                rate=samplerate,
                input=True,
                frames_per_buffer=buffer_size)

if len(sys.argv) > 1:
    # record 5 seconds
    output_filename = sys.argv[1]
    record_duration = 5  # exit 1
    outputsink = aubio.sink(sys.argv[1], samplerate)
    total_frames = 0
else:
    # run forever
    outputsink = None
    record_duration = None

# setup pitch
tolerance = 0.8
win_s = 4096  # fft size
sum_t = 0
hop_s = buffer_size  # hop size
pitch_o = aubio.pitch("default", win_s, hop_s, samplerate)
pitch_o.set_unit("midi")
pitch_o.set_tolerance(tolerance)

ax = []
ay = []
plt.ion()

print("*** starting recording")
while True:
    try:
        time_start = time.time()
        audiobuffer = stream.read(buffer_size, exception_on_overflow=False)
        signal = np.fromstring(audiobuffer, dtype=np.float32)

        pitch = pitch_o(signal)[0]
        confidence = pitch_o.get_confidence()

        if outputsink:
            outputsink(signal, len(signal))

        if record_duration:
            total_frames += len(signal)
            if record_duration * samplerate < total_frames:
                break

        time_end = time.time()
        sum_t = (time_end - time_start)+sum_t
        print("{} / {} / {}".format(confidence, pitch, sum_t, signal))

        ax.append(sum_t)
        ay.append(pitch)
        plt.clf()
        plt.ylim(60, 72)
        plt.plot(ax, ay)
        plt.pause(0.0000000001)
        # plt.ioff()

    except KeyboardInterrupt:
        print("*** Ctrl+C pressed, exiting")
        break

print("*** done recording")
stream.stop_stream()
stream.close()
p.terminate()
