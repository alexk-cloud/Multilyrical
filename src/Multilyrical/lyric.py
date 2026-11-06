import requests
from google.cloud import translate_v2 as translate
from api_client import session

lyrics_cache = {}

tr = translate.Client()

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
    