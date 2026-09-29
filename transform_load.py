import duckdb
import os
import json
from dotenv import load_dotenv
import pandas as pd





records = []
df = pd.read_csv('raw_ratings.csv').dropna(subset=['artist_name', 'song_title'])
for index, row in df.iterrows():
    artist = row['artist_name']
    track = row['song_title']
    rating = row['rating']
    submitter = row['submitter']
    rater = row['rater']
    notes = row['notes']

    text_columns  = ['artist_name', 'song_title', 'submitter', 'rater', 'notes']
    for col in text_columns:
        df[col] = df[col].str.strip()
        
    filename = f"{artist}_{track}.json".replace(" ", "_").replace("/", "_").replace("?","_")
    filepath = os.path.join("raw_jason", filename)
    if not os.path.exists(filepath):
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


    records.append({
        'artist_name': artist,
        'song_title': track,
        'listeners': listeners,
        'playcount': playcount,
        'genres': genre_list,
        'rating': rating,
        'submitter': submitter,
        'rater': rater,
        'notes': notes
    })

#print(pd.DataFrame(records).loc[:,['artist_name', 'genres']].head())






clean_dataframe = pd.DataFrame(records)

conn = duckdb.connect('music_data.duckdb')

conn.execute("CREATE OR REPLACE TABLE temp_tracks AS SELECT * FROM clean_dataframe")


conn.execute("""CREATE OR REPLACE TABLE artists AS SELECT
                ROW_NUMBER() OVER () AS artist_id,
                artist_name FROM (SELECT DISTINCT artist_name FROM temp_tracks) """)

#tracks and ratings were duplicating so add QUALIFY clause, -> splits 60 rows into 30 mini 2 rows. then labels 1 and 2, then only keeps labeled 1
conn.execute("""CREATE OR REPLACE TABLE tracks AS 
                WITH unique_tracks AS ( 
                    SELECT * FROM temp_tracks QUALIFY ROW_NUMBER() OVER (
                        PARTITION BY artist_name, song_title
                        ORDER BY artist_name
                    ) =1 
                )
                SELECT
                ROW_NUMBER() OVER () AS track_id,
                artists.artist_id,
                unique_tracks.song_title,
                unique_tracks.listeners,
                unique_tracks.playcount,
                unique_tracks.genres,
                FROM unique_tracks
                JOIN artists ON unique_tracks.artist_name = artists.artist_name""")

conn.execute("""CREATE OR REPLACE TABLE ratings AS SELECT
                ROW_NUMBER() OVER () AS rating_id,
                tracks.track_id,
                temp_tracks.rating,
                temp_tracks.submitter,
                temp_tracks.rater,
                temp_tracks.notes
                FROM temp_tracks
                JOIN artists ON temp_tracks.artist_name = artists.artist_name
                JOIN tracks ON tracks.artist_id = artists.artist_id AND tracks.song_title = temp_tracks.song_title""")

conn.execute("DROP TABLE temp_tracks")

print("Individual tables created successfully.")
conn.close()





#questions to be answered:
#who is the strictest rater? (e.g. lowest average rating given)      SELECT ROUND(AVG(rating),2) as avg_rating, rater FROM ratings GROUP BY rater ORDER BY avg_rating ASC  

#genre preferences   
#who has the nichest taste? (e.g. something like 1/ listeners/playcount * rating)   IF someone submits more niche than another, they are at disadvantage - FIX, small songs at 500 listeners too heavily biased compared to 10,000+ listener - FIX, someones standard deviation has an effect, e.g. someones 1 rating at 9/10 is not the same as someone else's 10 ratings of 9/10 (z-score normalisation)
# ranked most liked songs on average and also whos suggestions are best
# songs where there is the highest disagreement between raters






