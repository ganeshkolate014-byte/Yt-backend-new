from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from ytmusicapi import YTMusic
import yt_dlp

app = FastAPI()
ytmusic = YTMusic()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔍 SEARCH SONGS
@app.get("/search")
def search(q: str = Query(...)):
    results = ytmusic.search(q, filter="songs", limit=10)
    songs = []

    for s in results:
        songs.append({
            "title": s["title"],
            "videoId": s["videoId"],
            "artist": s["artists"][0]["name"],
            "thumb": s["thumbnails"][-1]["url"]
        })

    return songs


# ▶️ STREAM URL
from functools import lru_cache

@lru_cache(maxsize=200)
def get_stream_url(videoId: str):
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio",
        "quiet": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "noplaylist": True,
        "extract_flat": False,
        "skip_download": True,
        "cachedir": False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(
            f"https://music.youtube.com/watch?v={videoId}",
            download=False
        )
        return info["url"]


@app.get("/stream")
def stream(videoId: str):
    return {
        "url": get_stream_url(videoId)
    }
# 🎧 RECOMMENDATIONS / RELATED SONGS
@app.get("/recommendations")
def recommendations(videoId: str):
    data = ytmusic.get_watch_playlist(videoId=videoId, limit=20)

    recs = []

    for track in data.get("tracks", []):
        if not track.get("videoId"):
            continue

        recs.append({
            "title": track["title"],
            "videoId": track["videoId"],
            "artist": track["artists"][0]["name"] if track.get("artists") else "Unknown",
            "thumb": track["thumbnail"][-1]["url"]
        })

    return recs
