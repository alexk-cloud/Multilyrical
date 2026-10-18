import asyncio
import song as s
import lyric as l

from flask import Flask, render_template, jsonify, request
from pathlib import Path

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/identify", methods=["POST"])
def id():
    try:
        s.record()
        track_info = asyncio.run(s.identify())

        # delete recording once song recognition is done
        FILE_PATH = Path("recording.wav")
        FILE_PATH.unlink(missing_ok=True)

        if track_info is None:
            return jsonify({"error": "Song could not be identified."}), 404

        artist = track_info.track.subtitle
        title = track_info.track.title
    
        return jsonify({
            "artist": artist,
            "title": title
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/results", methods=["GET", "POST"])
def results():
    artist = request.args.get("artist") or request.form.get("artist", "")
    title = request.args.get("title") or request.form.get("title", "")
    
    song_info = s.get_info()
    
    album = song_info[0]
    year = song_info[1]
    
    lyrics = None
    translated_lyrics = []
    error = None

    try:
        lyrics = l.get_lyrics(title, artist)

        if not lyrics:
            error = "Lyrics could not be found."
        elif request.method == "POST":
            target_lang = request.form.get("target_lang", "")
            
            if target_lang and lyrics:
                translated_lyrics = l.translate(lyrics, target_lang=target_lang)

        #TODO: maybe add condition and message for instrumental songs
    except Exception as e:
        print(f"Lyrics lookup or translation failed: {e}")
        error = "Can't retrieve lyrics."

    return render_template(
        "results.html",
        artist=artist,
        title=title,
        album=album,
        year=year,
        lyrics=lyrics,
        langs=l.get_langs(),
        translated_lyrics=translated_lyrics,
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)