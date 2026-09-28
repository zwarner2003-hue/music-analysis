import requests
import os
import json
import time
from dotenv import load_dotenv
import pandas as pd
from rapidfuzz import fuzz, process


df = pd.read_csv('raw_ratings.csv').dropna(subset=['artist_name', 'song_title'])
text_columns  = ['artist_name', 'song_title', 'submitter', 'rater', 'notes']

for col in text_columns:
    df[col] = df[col].str.strip()


df = df[["artist_name" , "song_title"]].drop_duplicates().reset_index(drop=True)

for index, row in df.iterrows():
    artist = row['artist_name']
    track = row['song_title']
    filename = f"{artist}_{track}.json".replace(" ", "_").replace("/", "_").replace("?","_")
    filepath = os.path.join("raw_jason", filename)
    if not os.path.exists(filepath):                # probs dont need
        print(f"Track file does not exist.")
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        listeners = int(data.get('track', {}).get('listeners', '0'))
        playcount = int(data.get('track', {}).get('playcount', '0'))
        genre = data.get('track', {}).get('toptags', {}).get('tag', [])

        if not genre:
            filename = f"{artist.lower().strip()}_info.json".replace(" ", "_").replace("/", "_").replace("?","_")
            filepath = os.path.join("raw_jason", filename)
            
            if not os.path.exists(filepath):
                main_artist = artist.split(" and ")[0].strip()  
                filename = f"{main_artist}_info.json".replace(" ", "_").replace("/", "_").replace("?","_")
                filepath = os.path.join("raw_jason", filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    genre = data.get('artist', {}).get('tags', {}).get('tag', [])
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                genre = data.get('artist', {}).get('tags', {}).get('tag', [])
    print(f"Listeners: {listeners}, Playcount: {playcount} for {artist} - {track}")
    genre_list = [g['name'] for g in genre] if genre else "unknown"
    genre_list = ', '.join(genre_list) if isinstance(genre_list, list) else genre_list
    print(f"Genre for {artist} - {track}:  Genres: {genre_list}")