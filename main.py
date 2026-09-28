import asyncio
import song as s
import lyric as l

async def main():
    s.record()
    song = await s.identify()
    s.display_info(song)

    artist = s.get_artist()
    title = s.get_title()

    lyrics = l.get_lyrics(title, artist)

    target_lang = l.choose_lang()

    translated = l.translate(lyrics["plainLyrics"], target_lang=target_lang)

    print("*" * 50)
    print(f"{lyrics["plainLyrics"]}\n")

    print("*" * 50)
    print(f"\n{translated[0]["translatedText"]}")

if __name__ == "__main__":
    asyncio.run(main())