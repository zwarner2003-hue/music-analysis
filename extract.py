import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("LASTFM_API_KEY")
print("Loaded API Key:", api_key)
if api_key is None:
    raise ValueError("API key not found. Please set LASTFM_API_KEY in your .env file.")

url = "http://ws.audioscrobbler.com/2.0/"

params = {
    "method": "track.getInfo",
    "api_key": api_key,
    "artist": "Beatles",
    "track": "Hey Jude",
    "format": "json" 
}


response = requests.get(url, params=params)

print("Status code:", response.status_code)
print("Content type:", response.headers.get('content-type'))

if response.status_code == 200:
    data = response.json()
    print(data)