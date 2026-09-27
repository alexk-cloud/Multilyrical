import asyncio

from lyric import translate
from song import record, identify, display_info

async def main():
    record()
    song = await identify()
    display_info(song)

if __name__ == "__main__":
    asyncio.run(main())