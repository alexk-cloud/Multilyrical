import sounddevice as sd
import soundfile as sf
import re
import requests
import os
from shazamio import Serialize, Shazam
from pathlib import Path
from coverpy import CoverPy, NoResultsException
from api_client import session
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Optional

MAX_REC_SECS = 5
SAMPLE_RATE = 44100
FILE_NAME = "recording.wav"
FILE_PATH = Path(FILE_NAME)

track_info = None
artist = None
title = None
album = None
year = None

song_cache = {}
search_cache = {}
art_cache = {}
info_cache = {}

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
    track_info = None
    
    async with Shazam() as shazam:
        song = await shazam.recognize(FILE_NAME)

        if "track" in song:
            track_info = Serialize.full_track(song)
            return track_info
    
        print("Song could not be identified.")
        return None

"""
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
"""

def get_artist():
    global artist
    return artist

def get_title():
    global title
    return title

def get_album_and_year():
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
    if not artist or not title:
        print("Artist and/or title is missing.")
        return None

    cache_key = (artist.lower(), title.lower())

    if cache_key in art_cache:
        print("Using cached artwork.")
        return art_cache[cache_key]
    
    title = clean_title(title)
    client = CoverPy()
    art = None
    
    try:
        result = client.get_cover(f"{artist} {title}")
        art = result.artwork(1200)

    except NoResultsException:
        print("No cover results found.")
        
    except KeyError as e:
        print(f"CoverPy returned incomplete metadata: {e}")
        art = None
        
    except Exception as e:
        print(f"Artwork retrieval failed: {e}")
        art = None

    art_cache[cache_key] = art
    return art 

def get_song_data(title, artist):
    cache_key = (title.lower(), artist.lower())

    if cache_key in song_cache:
        print("Using cached song data.")
        return song_cache[cache_key]
    
    url = "https://lrclib.net/api/search"
    
    try:
        response = session.get(
            url,
            params={
                "track_name": title,
                "artist_name": artist
                },
            timeout=(3, 8)
        )
        
        response.raise_for_status()
        results = response.json()
        
        if results:
            return results[0]
        
        return None
    
    except requests.exceptions.RetryError as e:
        print(f"LRCLIB is unavailable after retries: {e}")
        return None

    except requests.exceptions.Timeout:
        print("LRCLIB song request timed out.")
        return None

    except requests.exceptions.HTTPError as e:
        print(f"LRCLIB returned an HTTP error: {e}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"LRCLIB song request failed: {e}")
        return None

    except ValueError as e:
        print(f"Could not process LRCLIB response: {e}")
        return None

def search_songs(query):
    if query in search_cache:
        print("Using cached search results.")
        return search_cache[query]

    url = "https://lrclib.net/api/search"

    try:
        response = session.get(
            url,
            params={"q": query},
            timeout=(3, 8)
        )
        
        response.raise_for_status()
        results = response.json()
        search_cache[query] = results

        return results
    
    except requests.exceptions.RetryError as e:
        print(f"LRCLIB is unavailable after retries: {e}")
        return None

    except requests.exceptions.Timeout:
        print("LRCLIB search request timed out.")
        return None

    except requests.exceptions.HTTPError as e:
        print(f"LRCLIB returned an HTTP error: {e}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"LRCLIB search request failed: {e}")
        return None

    except ValueError as e:
        print(f"Could not process LRCLIB response: {e}")
        return None
    
def get_song_by_id(song_id):
    if song_id in song_cache: 
        print("Using cached song.")
        return song_cache[song_id]
        
    url = f"https://lrclib.net/api/get/{song_id}"
    
    try:
        response = session.get(url, timeout=(3, 8))
        response.raise_for_status()
        
        song = response.json()
        song_cache[song_id] = song

        return song
    
    except requests.exceptions.RetryError as e:
        print(f"LRCLIB is unavailable after retries: {e}")
        return None

    except requests.exceptions.Timeout:
        print("LRCLIB request timed out.")
        return None

    except requests.exceptions.HTTPError as e:
        print(f"LRCLIB returned an HTTP error: {e}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve song: {e}")
        return None

    except ValueError as e:
        print(f"Could not process LRCLIB response: {e}")
        return None

class Summary(BaseModel):
    overview: str = Field(description="A brief overview of the song")
    themes: List[str] = Field(
        min_length=3,
        max_length=3,
        description="Exactly three major themes of the song (words only)"
        )

def generate_insights(title, artist, lyrics):
    cache_key = (title.lower(), artist.lower())

    if cache_key in info_cache:
        print("Using cached song insights.")
        return info_cache[cache_key]
    
    prompt = f"""
    Analyze this song and its lyrics.

    Title: {title}
    Artist: {artist}
    Lyrics:
    {lyrics}

    Provide:
    - A brief overview (maximum 3 sentences)
    - Three major themes (only the words, no description)

    Avoid generic interpretations that could
    apply to almost any song.
    """

    client = genai.Client(api_key=os.getenv("GEMINI_KEY"))

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Summary
        )
    )

    insights = Summary.model_validate_json(response.text)
    info_cache[cache_key] = {
        "overview": insights.overview,
        "themes": insights.themes,
    }
    
    return {
        "overview": insights.overview,
        "themes": insights.themes,
    }