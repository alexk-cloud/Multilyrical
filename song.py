import asyncio
import sounddevice as sd
import soundfile as sf
from shazamio import Serialize, Shazam

MAX_REC_SECS = 5
SAMPLE_RATE = 44100

def record():
    duration = MAX_REC_SECS
    sample_rate = SAMPLE_RATE

    print("Now recording...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)

    sd.wait()

    sf.write("recording.mp3", audio, sample_rate)

    print("recording.mp3 saved!")

def main():
    record()

#asyncio.run(main())

if __name__ == "__main__":
    main()