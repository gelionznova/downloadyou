import os
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory, make_response, url_for
from yt_dlp import YoutubeDL

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change_me")

FFMPEG_PATH = os.getenv("FFMPEG_PATH")  # optional
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "/tmp/downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def buscar_videos(query: str):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "default_search": "ytsearch10",
        "extract_flat": False,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            app.logger.info(f"Buscando videos: {query}")
            info = ydl.extract_info(query, download=False)
            videos = []
            for entry in info.get("entries", []):
                url = entry.get("webpage_url")
                if url:
                    videos.append({"title": entry.get("title", "Sin título"), "link": url})
        app.logger.info(f"Videos encontrados: {len(videos)}")
        return videos
    except Exception as e:
        app.logger.error(f"Error buscando videos: {e}")
        return []

@app.route("/", methods=["GET", "POST"])
def index():
    resultados = []
    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if query:
            resultados = buscar_videos(query)
    ffmpeg_ok = bool(FFMPEG_PATH)
    return render_template("index.html", resultados=resultados, ffmpeg_ok=ffmpeg_ok)

@app.route("/descargar", methods=["POST"])
def descargar():
    url = request.json.get("url")
    if not url:
        return jsonify({"success": False, "error": "URL no proporcionada"})

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "quiet": True,
        "noplaylist": True,
    }
    if FFMPEG_PATH:
        ydl_opts["ffmpeg_location"] = FFMPEG_PATH

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = f"{info_dict.get('title', 'audio')}.mp3"
        app.logger.info(f"Descarga completa: {filename}")
        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        app.logger.error(f"Error descargando audio: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route("/descargas/<path:filename>")
def download_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

# -------- Service Worker served through template to allow url_for --------
@app.route("/sw.js")
def sw():
    response = make_response(render_template("sw.js"))
    response.headers["Content-Type"] = "application/javascript"
    return response

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
