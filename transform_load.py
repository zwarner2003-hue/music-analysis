import requests
import os
import json
import time
from dotenv import load_dotenv
import pandas as pd


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
    if os.path.exists(filepath):
        print("File already exists.")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        listeners = int(data.get('track', {}).get('listeners', '0'))
        playcount = int(data.get('track', {}).get('playcount', '0'))
        print(f"Listeners: {listeners}, Playcount: {playcount} for {artist} - {track}")