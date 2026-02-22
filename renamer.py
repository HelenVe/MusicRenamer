import requests
from pathlib import Path
from mutagen import File
import time
import os
from dotenv import load_dotenv


def ask_llm_for_title(artist: str, all_artists: list):
    prompt = (
        f"You are a music metadata expert. Given that the artist is {artist}"\
        f"guess the most likely song title. So far, all the artists I have songs from are {all_artists}. Respond only using the candidate title"
        f" If you are not sure respond with None and no more words."
    )

    resp = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral:latest",
              "prompt": prompt,
              "max tokens": 5, "stream": False, "temperature": 0.3}
    )

    text = resp.json()["response"]
    return text

def ask_llm_for_artist(title: str, all_artists: list):
    prompt = (
        f"You are a music metadata expert. Given that the title is {title}" \
        f"guess the most likely artist. So far, all the artists I have songs from are {all_artists}. Respond only using the candidate artist, nothing more." \
        f" If you are not sure respond with None and no more words."
    )
    resp = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral:latest",
              "prompt": prompt, "max_tokens": 5, "stream": False, "temperature": 0.3}
    )

    text = resp.json()["response"]
    return text

def sanitize(name: str) -> str:
        """Remove characters that can't be used in filenames."""
        bad = '<>:"/\\|?*,.0123456789()'
        for c in bad:
            name = name.replace(c, '')
        return name.strip()


def build_new_filename(title, artist, ext):
    title_clean = sanitize(title)
    artist_clean = sanitize(artist)

    # Only append artist if it's not already in the title
    if artist_clean.lower() in title_clean.lower():
        new_name = f"{title_clean}{ext}"
    else:
        new_name = f"{title_clean} - {artist_clean}{ext}"
    return new_name

if __name__ == "__main__":
    load_dotenv()
    MUSIC_DIR = Path(os.getenv("MUSIC_PATH"))

    c = 0
    start_time = time.time()
    all_artists, all_titles = [], []
    for root, dirs, files in os.walk(MUSIC_DIR):
        for file in files:
            if not file.lower().endswith((".mp3", ".flac", ".m4a", ".wav", ".ogg")):
                continue

            path = os.path.join(root, file)
            audio = File(path, easy=True)

            if not audio:
                print(f"Cannot read tag: {file}")
                continue

            title = audio.get("Title", [None])[0]
            artist = audio.get("artist", [None])[0] or audio.get("albumartist", [None])[0]
            all_titles.append(title)
            all_artists.append(artist)

            # Skip if metadata missing
            if not title:
                title = ask_llm_for_title(artist=artist, all_artists=all_artists)
                if not title:
                    continue
            if not artist:
                artist = ask_llm_for_artist( title=title, all_artists=all_artists)
                if not artist:
                    continue

            ext = os.path.splitext(path)[1]
            new_name = build_new_filename(title, artist, ext)

            new_path = os.path.join(root, new_name)

            # Only rename if needed
            # If another file already exists with the same name delete it
            if path != new_path:
                print(f"🎵 Renaming:\n   {file}\n → {new_name}")
                try:
                    os.rename(path, new_path)
                except FileExistsError:
                    os.remove(path)
                except Exception as e:
                    print(e)
                    continue
            else:
                continue

    print(f"Time to process {c} files: {time.time()-start_time}")
