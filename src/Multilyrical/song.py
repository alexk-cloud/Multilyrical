import asyncio
import sounddevice as sd
import soundfile as sf
#import os
from shazamio import Serialize, Shazam
from pathlib import Path

MAX_REC_SECS = 5
SAMPLE_RATE = 44100
FILE_NAME = "recording.wav"
#FILE_NAME = "Ash.mp3"
FILE_PATH = Path(FILE_NAME)

track_info = None
artist = None
title = None

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
        track_info = Serialize.full_track(song)
        return track_info
    else:
        print("Song could not be identified.")
        return None

def display_info(track_info):
    if track_info is not None:
        global artist
        artist = track_info.track.subtitle
        global title 
        title = track_info.track.title
        album = None
        year = None
        label = None
        
        print("-" * 50)
        print(f"SONG NAME: {artist} - {title}")
        print("-" * 50)

        for section in track_info.track.sections:
            if section.type == "SONG":
                for metadata in section.metadata:
                    if metadata.title == "Album":
                        album = metadata.text
                    if metadata.title == "Released":
                        year = metadata.text
                    if metadata.title == "Label":
                        label = metadata.text

        print(f"Album: {album}")
        print(f"Released: {year}")
        print(f"Label: {label}")

def get_artist():
    global artist
    return artist

def get_title():
    global title
    return title