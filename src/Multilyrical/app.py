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
    target_lang = request.form.get("target_lang", "en")
    
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
        target_lang=target_lang,
        error=error
    )

@app.route("/search", methods=["POST"])
def search():
    query = ""
    
    if request.method == "POST":
        query = request.form.get("query", "").strip()
    
    results = []
    error = None
    
    if query: 
        try:
            results = l.search_songs(query)
            
            if not results:
                error = "No matching songs found."
        except Exception as e:
            print(f"Song search failed: {e}")
            error = "Could not search for songs."
    
    return render_template(
        "search_results.html",
        query=query,
        results=results,
        error=error
    )

@app.route("/song/<int:song_id>", methods=["GET", "POST"])
def results_by_id(song_id):
    try:
        song = l.get_song_by_id(song_id)
        
        lyrics = song.get("plainLyrics")
        
        if lyrics:
            lyrics = lyrics.splitlines()
        else:
            lyrics = []
        
        translated_lyrics = []
        target_lang = request.form.get("target_lang", "en")
        
        if request.method == "POST":
            if target_lang and lyrics:
                translated_lyrics = l.translate(lyrics, target_lang=target_lang)
                
        #FIXME method not allowed on this url when translating
        #FIXME year not included
        return render_template(
            "results.html",
            artist=song.get("artistName"),
            title=song.get("trackName"),
            album=song.get("albumName"),
            lyrics=lyrics,
            langs=l.get_langs(),
            translated_lyrics=translated_lyrics,
            target_lang=target_lang,
            error=None
        )
    except Exception as e:
        print(f"Failed to retrieve song: {e}")
        return "Unable to retrieve this song's information.", 500
            
if __name__ == "__main__":
    app.run(debug=True)