import asyncio
import song as s
import lyric as l
import os
import tempfile

from flask import Flask, render_template, jsonify, request, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

FLASK_KEY = os.getenv("FLASK_KEY")
app = Flask(__name__)
app.secret_key = FLASK_KEY

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

@app.after_request
def add_csp(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:;"
    )

    return response

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/identify", methods=["POST"])
@limiter.limit("20 per minute; 100 per hour")
def id():
    audio = request.files.get("audio")

    if not audio:
        return jsonify({"error": "No audio recording received."}), 400

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".webm",
        delete=False
    )

    audio_path = temp_file.name

    try:
        audio.save(audio_path)
        temp_file.close()

        track_info = asyncio.run(s.identify(audio_path))

        if track_info is None:
            return jsonify({
                "error": "Song could not be identified."
            }), 404

        artist = track_info.track.subtitle
        title = track_info.track.title
        image_url = s.get_song_art(artist, title)

        return jsonify({
            "artist": artist,
            "title": title,
            "image_url": image_url
        })

    except Exception as e:
        print(f"Song identification failed: {e}")

        return jsonify({
            "error": "Song identification failed."
        }), 500

    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)

"""
@app.route("/cancel", methods=["POST"])
@limiter.limit("30 per minute; 200 per hour")
def cancel():
    try:
        s.cancel_recording()
        FILE_PATH.unlink(missing_ok=True)

        return jsonify({"status": "cancelled"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""

@app.route("/results", methods=["GET", "POST"])
@limiter.limit("10 per minute; 50 per hour")
def results():
    artist = request.args.get("artist") or request.form.get("artist", "")
    title = request.args.get("title") or request.form.get("title", "")
    target_lang = request.form.get("target_lang", "en")
    
    song = s.get_song_data(title, artist)
    
    if song is None:
        return render_template(
            "error.html",
            error="Could not get song data."
        )
    
    song_id = song.get("id")

    release_info = s.get_album_and_year()
    album = release_info[0]
    year = release_info[1]

    image_url = s.get_song_art(artist, title)
    
    lyrics = None
    translated_lyrics = []
    error = None

    try:
        lyrics = song.get("plainLyrics", "").splitlines()

        if not lyrics:
            error = "Lyrics could not be found. Please try again later."
        else:
            insights = s.generate_insights(title, artist, lyrics)

            if request.method == "POST" and target_lang and lyrics:
                translated_lyrics = l.translate(lyrics, target_lang=target_lang)

        #TODO: maybe add condition and message for instrumental songs
    except Exception as e:
        print(f"Lyrics lookup or translation failed: {e}")
        error = "Can't retrieve lyrics."
        insights = {"overview": "", "themes": []}

    return render_template(
        "results.html",
        song_id=song_id,
        artist=artist,
        title=title,
        album=album,
        image_url=image_url,
        overview=insights["overview"],
        themes=insights["themes"],
        year=year,
        lyrics=lyrics,
        langs=l.get_langs(),
        translated_lyrics=translated_lyrics,
        target_lang=target_lang,
        error=error
    )

@app.route("/search", methods=["POST"])
@limiter.limit("30 per minute; 200 per hour")
def search():
    query = ""
    
    if request.method == "POST":
        query = request.form.get("query", "").strip()
    
    results = []
    artwork = {}
    error = None
    
    if query: 
        try:
            results = s.search_songs(query)

            if results is None:
                error = "Song search is temporarily unavailable. Please try again later."
                return render_template(
                    "error.html",
                    error=error
                ), 503

        except Exception as e:
            print(f"Song search failed: {e}")
            error = "Could not search for songs."
    
    return render_template(
        "search_results.html",
        query=query,
        results=results,
        artwork=artwork,
        error=error
    )

@app.route("/artwork")
@limiter.limit("60 per minute; 300 per hour")
def get_artwork():
    artist = request.args.get("artist")
    title = request.args.get("title")

    art = s.get_song_art(artist, title)

    return jsonify({"art": art})

@app.route("/song/<int:song_id>", methods=["GET", "POST"])
@limiter.limit("10 per minute; 50 per hour")
def results_by_id(song_id):
    try:
        song = s.get_song_by_id(song_id)
        
        if song is None:
            return render_template(
                "error.html",
                error="Unable to retrieve this song right now. Please try again later."
            ), 503
            
        artist = song.get("artistName")
        title = song.get("trackName")
        album = song.get("albumName")
        image_url = s.get_song_art(artist, title)
        
        lyrics = song.get("plainLyrics")
        
        recent_songs = session.get("recent_songs", [])
        recent_songs = [
            item for item in recent_songs
            if item["id"] != song_id
        ]   
        
        recent_songs.insert(0, {
            "id": song_id,
            "title": song.get("trackName"),
            "artist": song.get("artistName"),
            "album": song.get("albumName"),
            "image_url": image_url
        })

        #keep only the 10 most recent songs
        session["recent_songs"] = recent_songs[:10]

        if not lyrics:
            lyrics = []
        else:
            lyrics = lyrics.splitlines()
            insights = s.generate_insights(title, artist, lyrics)
        
        translated_lyrics = []
        target_lang = request.form.get("target_lang", "en")
        
        if request.method == "POST":
            if target_lang and lyrics:
                translated_lyrics = l.translate(lyrics, target_lang=target_lang)

        return render_template(
            "results.html",
            song_id=song_id,
            artist=artist,
            title=title,
            album=album,
            image_url=image_url,
            overview=insights["overview"],
            themes=insights["themes"],
            lyrics=lyrics,
            langs=l.get_langs(),
            translated_lyrics=translated_lyrics,
            target_lang=target_lang,
            error=None
        )
    except Exception as e:
        print(f"Failed to retrieve song: {e}")
        return render_template(
            "error.html",
            error="Unable to retrieve this song right now. Please try again later."
        ), 503

@app.route("/recent")
def recently_viewed():
    recent_songs = session.get("recent_songs", [])

    return render_template(
        "recent.html",
        recent_songs=recent_songs
    )
    
@app.route("/saved")
def saved():
    return render_template("saved.html")

@app.route("/playlists")
def playlists():
    return render_template("playlists.html")

if __name__ == "__main__":
    app.run(debug=True)