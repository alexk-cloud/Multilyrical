import requests
import os
from api_client import session

lyrics_cache = {}

def translate(
    text: str | list[str],
    orig_lang: str | None = None,
    target_lang: str = "en"
) -> list[str]:

    api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY")

    if not api_key:
        raise RuntimeError("GOOGLE_TRANSLATE_API_KEY not found.")

    if isinstance(text, str):
        text = [text]

    response = requests.post(
        "https://translation.googleapis.com/language/translate/v2",
        headers={
            "X-Goog-Api-Key": api_key,
            "Content-Type": "application/json",
        },
        json={
            "q": text,
            "target": target_lang,
            "format": "text",
            **({"source": orig_lang} if orig_lang else {}),
        },
        timeout=20,
    )

    response.raise_for_status()

    translations = response.json()["data"]["translations"]
    return [item["translatedText"] for item in translations]

def get_langs():
    api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY")

    if not api_key:
        raise RuntimeError("GOOGLE_TRANSLATE_API_KEY not found.")

    response = requests.get(
        "https://translation.googleapis.com/language/translate/v2/languages",
        headers={"X-Goog-Api-Key": api_key},
        params={"target": "en"},
        timeout=20,
    )
    response.raise_for_status()

    return response.json()["data"]["languages"]

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
    