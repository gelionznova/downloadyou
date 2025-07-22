import os
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory, make_response
from utils.search import search_piped
from utils.download import download_mp3, decode_cookies_from_env

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change_me")

DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "/tmp/downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

FFMPEG_PATH = os.getenv("FFMPEG_PATH")  # si usas NIXPACKS_PKGS=ffmpeg, deja None
COOKIEFILE = decode_cookies_from_env("/tmp/cookies.txt")  # opcional

@app.route("/", methods=["GET", "POST"])
def index():
    resultados = []
    if request.method == "POST":
        q = request.form.get("query", "").strip()
        if q:
            try:
                resultados = search_piped(q)
            except Exception as e:
                app.logger.error(f"Error en búsqueda: {e}")
                resultados = []
    ffmpeg_ok = bool(FFMPEG_PATH)  # informativo
    return render_template("index.html", resultados=resultados, ffmpeg_ok=ffmpeg_ok)

@app.route("/descargar", methods=["POST"])
def descargar():
    data = request.get_json(silent=True) or {}
    url = data.get("url")
    if not url:
        return jsonify({"success": False, "error": "URL no proporcionada"})
    try:
        filename = download_mp3(url, DOWNLOAD_DIR, ffmpeg_path=FFMPEG_PATH, cookiefile=COOKIEFILE)
        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        app.logger.exception("Error descargando")
        return jsonify({"success": False, "error": str(e)})

@app.route("/descargas/<path:filename>")
def download_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

# ---- Service Worker con Jinja ----
@app.route("/sw.js")
def sw():
    resp = make_response(render_template("sw.js"))
    resp.headers["Content-Type"] = "application/javascript"
    return resp

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
