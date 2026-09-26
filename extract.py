import requests
import os
import json
import time
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

df = pd.read_csv('raw_ratings.csv')
indv_track = df[["artist_name" , "song_title"]].drop_duplicates().reset_index(drop=True)

os.makedirs("raw_jason", exist_ok=True)

api_key = os.getenv("LASTFM_API_KEY")
print("Loaded API Key:", api_key)
if api_key is None:
    raise ValueError("API key not found. Set LASTFM_API_KEY in your .env file.")

url = "http://ws.audioscrobbler.com/2.0/"
for index, row in indv_track.iterrows():
    artist = row['artist_name']
    track = row['song_title']
    filename = f"{artist}_{track}.json".replace(" ", "_").replace("/", "_")
    filepath = os.path.join("raw_jason", filename)
    params = {
        "method": "track.getInfo",
        "api_key": api_key,
        "artist": artist,
        "track": track,
        "format": "json" 
    }
    response = requests.get(url, params=params)

    #print("Status code:", response.status_code)
    #print("Content type:", response.headers.get('content-type'))

    if response.status_code == 200:
        data = response.json()
        with open(filepath, 'w') as f:
            json.dump(data,f,ensure_ascii=False, indent=4)
        print(f"Saved JSON for {artist} - {track} to {filepath}")

    time.sleep(1)