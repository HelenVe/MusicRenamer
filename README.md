🎵 Music Renamer with Metadata

Automatically rename your music files based on embedded metadata (Title and Artist).
This script ensures clean filenames, avoids duplicates, and handles existing files safely


🔹 Features

Reads Title and Artist from metadata (ID3 for MP3, FLAC, M4A, OGG).
Renames files to: Title - Artist.extension
If a title or artist is not present, it uses Mistral to try and find out. 
If the new filename already exists, then the old file gets deleted from your folder.

🔹 Safety Notes

Make sure your music folder is backed up before running the script.
The script deletes destination files if they already exist to avoid conflicts.
Some files are skipped - usually when the LLM blabbers.

🔹 Requirements

Python 3.8+

Mutagen

Ollama

To use Ollama, first download it. Then use a cmd and type pull mistral to download the latest mistral. 
You can replace Mistral with any other model 