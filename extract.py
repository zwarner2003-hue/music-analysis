import requests
import os
import json
import time
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

df = pd.read_csv('raw_ratings.csv').dropna(subset=['artist_name', 'song_title'])
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
    filename = f"{artist}_{track}.json".replace(" ", "_").replace("/", "_").replace("?","_")       #special characters were causing issues with file naming
    filepath = os.path.join("raw_jason", filename)
    if os.path.exists(filepath):
        print(f"File already exists: {filepath}")
        continue
    params = {
        "method": "track.getInfo",
        "api_key": api_key,
        "artist": artist,
        "track": track,
        "autocorrect": 1,
        "format": "json" 
    }
    response = requests.get(url, params=params)

    #print("Status code:", response.status_code)
    #print("Content type:", response.headers.get('content-type'))

    if response.status_code == 200:
        data = response.json()

        listeners = int(data.get('track', {}).get('listeners', 'N/A'))
        if listeners < 300 and " and " in artist:
            main_artist = artist.split(" and ")[0].strip()  
            params["artist"] = main_artist
            retry_response = requests.get(url, params=params)
            if retry_response.status_code == 200:
                data = retry_response.json()
                print(f"Retry successful for {main_artist} - {track}")
           
        with open(filepath, 'w', encoding='utf-8') as f:              #without encoding='utf-8', some characters were not being saved correctly in the JSON file
            json.dump(data,f,ensure_ascii=False, indent=4)
        print(f"Saved JSON for {artist} - {track} to {filepath}")

    time.sleep(1)