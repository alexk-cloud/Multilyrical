import asyncio
import sounddevice as sd
import soundfile as sf
import re
from shazamio import Serialize, Shazam
from pathlib import Path
from coverpy import CoverPy, NoResultsException

MAX_REC_SECS = 5
SAMPLE_RATE = 44100
FILE_NAME = "recording.wav"
#FILE_NAME = "Ash.mp3"
FILE_PATH = Path(FILE_NAME)

track_info = None
artist = None
title = None
album = None
year = None

def record():
    duration = MAX_REC_SECS
    sample_rate = SAMPLE_RATE

    print("Now recording...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)

    sd.wait()

    sf.write(FILE_NAME, audio, sample_rate)

    print("Audio saved!")

async def identify():
    global track_info
    shazam = Shazam()

    song = await shazam.recognize(FILE_NAME)

    if "track" in song:
        track_info = Serialize.full_track(song)
    else:
        print("Song could not be identified.")
    
    return track_info

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
        
        print(f"\nRAW DATA:\n{track_info}")

def get_artist():
    global artist
    return artist

def get_title():
    global title
    return title

def get_info():
    # album, release year
    global track_info
    global album
    global year
    info = []
    
    for section in track_info.track.sections:
        if section.type == "SONG":
            for metadata in section.metadata:
                if metadata.title == "Album":
                    album = metadata.text
                if metadata.title == "Released":
                    year = metadata.text
    
    info.append(album)
    info.append(year)
    
    return info

def clean_title(title):
    title = re.sub(
        r"\s*\((?:[^)]*\bcover\b[^)]*|[^)]*\bkaraoke\b[^)]*)\)",
        "",
        title,
        flags=re.IGNORECASE
    )
    
    return title.strip()
    
def get_song_art(artist, title):
    if artist is None or title is None:
        print("Artist and/or title is None.")
        return
    
    title = clean_title(title)
    client = CoverPy()
    art = None
    
    try:
        result = client.get_cover(f"{artist} {title}")
    except NoResultsException:
        print("No cover results found.")
    else:
        art = result.artwork(1200)
        return art
            
        