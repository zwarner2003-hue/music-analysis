import duckdb
import streamlit as st

st.title("Who's Music Taste is Best?")
st.text('what does this do?')

duckdb_conn = duckdb.connect( "music_data.duckdb", read_only=True)

disparity = duckdb_conn.sql("""
SELECT
    tracks.song_title,
    artists.artist_name,
    MAX(ratings.rating) - MIN(ratings.rating) AS rating_disparity
FROM ratings
JOIN tracks
    ON tracks.track_id = ratings.track_id
JOIN artists
    ON artists.artist_id = tracks.track_id
GROUP BY tracks.track_id, tracks.song_title, artists.artist_name
ORDER BY rating_disparity Desc, tracks.song_title
LIMIT 5;
""").df()

st.subheader("Most Controversial Songs")
st.dataframe(disparity, hide_index= True,
             column_config = {
                 "song_title": "Song",
                 "artist_name": "Artist",
                 "rating_disparity": "Difference Of Rating" 
             },)



best_suggestor = duckdb_conn.sql("""
SELECT
    ratings.submitter,
    AVG(rating) as average_rating
FROM ratings
JOIN tracks
    ON ratings.track_id = tracks.track_id
GROUP BY
    ratings.submitter
ORDER BY
    average_rating Desc
""").df()

st.subheader("Who Suggests The Best Songs?")
st.dataframe(best_suggestor, hide_index = True,
             column_config = {
                 "submitter": "Songs Submitted By",
                 "average_rating": "Average Rating"
         },)

