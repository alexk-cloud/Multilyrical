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

def choose_lang():
    languages = tr.get_languages(target_language="en")

    for i, language in enumerate(languages, start=1):
        print(f"{i}. {language['name']}")

    choice = int(input("\nEnter the number of your target language: "))

    selected = languages[choice - 1]

    return selected["language"]

def get_langs():
    return tr.get_languages(target_language="en")