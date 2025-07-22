import os
from yt_dlp import YoutubeDL

def decode_cookies_from_env(path):
    import base64, os
    b64 = os.getenv("YT_COOKIES_B64")
    if not b64:
        return None
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64))
    return path

def download_mp3(url, out_dir, ffmpeg_path=None, cookiefile=None):
    opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "noplaylist": True,
        "outtmpl": os.path.join(out_dir, "%(title)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "retries": 5,
        "sleep_requests": 1,
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
    }
    if ffmpeg_path:
        opts["ffmpeg_location"] = ffmpeg_path
    if cookiefile:
        opts["cookiefile"] = cookiefile

    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = f"{info.get('title','audio')}.mp3"
        return filename

