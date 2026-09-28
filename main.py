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

    print("*" * 50)
    print(lyrics["plainLyrics"])
    
if __name__ == "__main__":
    asyncio.run(main())