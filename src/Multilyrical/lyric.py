import requests
from google.cloud import translate_v2 as translate

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
    lyrics_list = []
    url = "https://lrclib.net/api/search"

    params = {
        "track_name": title,
        "artist_name": artist
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    # the json has a boolean "instrumental" key, which could be used to display a message saying there's no lyrics
    # there's also a "duration" key i could use
    results = response.json()

    if not results:
        print("Lyrics not found.")
        return None

    # put plain lyrics into lyrics list, then separate by new lines
    plain_lyrics = results[0].get("plainLyrics")
    lyrics_list = plain_lyrics.splitlines()
    
    #return results[0]

    return lyrics_list

def search_songs(query):
    url = "https://lrclib.net/api/search"
    
    response = requests.get(
        url,
        params={"q": query},
        timeout=10
    )
    
    response.raise_for_status()
    
    return response.json()

def get_song_by_id(song_id):
    url = f"https://lrclib.net/api/get/{song_id}"
    
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    
    song = response.json()
    
    return song