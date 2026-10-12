import asyncio
import song as s
import lyric as l

from flask import Flask, render_template, jsonify

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

if __name__ == "__main__":
    app.run(debug=True)