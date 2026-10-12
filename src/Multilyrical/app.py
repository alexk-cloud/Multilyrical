import asyncio
import song as s
import lyric as l

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/identify", methods=["POST"])
def id():
    try:
        s.record()
        track_info = asyncio.run(s.identify())

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

@app.route("/results")
def results():
    artist = request.args.get("artist", "")
    title = request.args.get("title", "")

    lyrics = None
    error = None

    try:
        track = l.get_lyrics(title, artist)

        if track:
            lyrics = track.get("plainLyrics")

            if not lyrics:
                error = "No plain lyrics available for this song."
        else:
            error = "Lyrics could not be found."
    except Exception as e:
        print(f"Lyrics lookup failed: {e}")
        error = "Can't retrieve lyrics."

    return render_template(
        "results.html",
        artist=artist,
        title=title,
        lyrics=lyrics,
        error=error
    )
                              

if __name__ == "__main__":
    app.run(debug=True)