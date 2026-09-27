import asyncio
import sounddevice as sd
import soundfile as sf
import os
from shazamio import Serialize, Shazam
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MAX_REC_SECS = 5
SAMPLE_RATE = 44100
FILE_NAME = "recording.wav"
FILE_PATH = Path(FILE_NAME)

def record():
    duration = MAX_REC_SECS
    sample_rate = SAMPLE_RATE

    print("Now recording...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)

    sd.wait()

    sf.write(FILE_NAME, audio, sample_rate)

    print("Audio saved!")

async def identify():
    shazam = Shazam()

    song = await shazam.recognize(FILE_NAME)

    if "track" in song:
        print("SONG NAME: ")
        print(f"{Serialize.full_track(song).track.subtitle} - {Serialize.full_track(song).track.title}\n\n")
        print(Serialize.full_track(song).track.sections)
    else:
        print("Song could not be identified.")

async def main():
    record()

    await identify()

    #if FILE_PATH.is_file():
    #    print("File exists")
    #else:
    #    print("No such file")

if __name__ == "__main__":
    asyncio.run(main())