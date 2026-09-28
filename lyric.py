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

    return results

def get_lyrics(title, artist):
    url = "https://lrclib.net/api/search"

    params = {
        "track_name": title,
        "artist_name": artist
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    results = response.json()

    if not results:
        print("Lyrics not found.")
        return None

    return results[0]

def choose_lang():
    languages = tr.get_languages(target_language="en")

    for i, language in enumerate(languages, start=1):
        print(f"{i}. {language['name']}")

    choice = int(input("\nEnter the number of your target language: "))

    selected = languages[choice - 1]

    return selected["language"]