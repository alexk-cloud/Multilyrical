import requests
from google.cloud import translate_v2 as translate
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

lyrics_cache = {}
song_cache = {}

tr = translate.Client()
session = requests.Session()
retries = Retry(
    total=2,
    connect=2,
    read=2,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET"],
    respect_retry_after_header=True
)

session.mount("https://", HTTPAdapter(max_retries=retries))

def translate(text: str | list[str], 
            orig_lang: str | None = None, 
            target_lang: str = "en"
            ) -> dict:
    
    global tr

    if isinstance(text, str):
        text = [text]

    results = tr.translate(
        values=text,
        target_language=target_lang,
        source_language=orig_lang,
        format_="text"
    )

    return [item["translatedText"] for item in results]

def get_langs():
    return tr.get_languages(target_language="en")

def get_song_data(title, artist):
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

def get_lyrics(title, artist):
    url = "https://lrclib.net/api/search"

    cache_key = (title.lower(), artist.lower())
    
    if cache_key in lyrics_cache:
        print("Using cached lyrics.")
        return lyrics_cache[cache_key]
    
    params = {
        "track_name": title,
        "artist_name": artist
    }
    
    try: 
        response = session.get(url, params=params, timeout=(3, 8))
        response.raise_for_status()

        # the json has a boolean "instrumental" key, which could be used to display a message saying there's no lyrics
        # there's also a "duration" key i could use
        results = response.json()

        if not results:
            print("Lyrics not found.")
            return None

        # put plain lyrics into lyrics list, then separate by new lines
        plain_lyrics = results[0].get("plainLyrics")
        
        if not plain_lyrics:
            print("No plain lyrics available.")
            return None
        
        lyrics_list = plain_lyrics.splitlines()
        lyrics_cache[cache_key] = lyrics_list

        return lyrics_list
    
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
        print(f"LRCLIB request failed: {e}")
        return None

    except ValueError as e:
        print(f"Could not process LRCLIB response: {e}")
        return None

def search_songs(query):
    url = "https://lrclib.net/api/search"
    
    try:
        response = session.get(
            url,
            params={"q": query},
            timeout=(3, 8)
        )
        
        response.raise_for_status()
        
        return response.json()
    
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
    