import duckdb
import streamlit as st
import plotly.express as px


st.title("Who's Music Taste is Best?")
st.text('WRITE DESCRIPTION HERE')

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
                 "song_title": "Song Title",
                 "artist_name": "Artist",
                 "rating_disparity": "Difference Of Rating" 
             },)



best_suggestor = duckdb_conn.sql("""
SELECT
    ratings.submitter AS "Songs Submitted By",
    AVG(rating) AS "Average Rating"
FROM ratings
JOIN tracks
    ON ratings.track_id = tracks.track_id
GROUP BY
    ratings.submitter
ORDER BY
    "Average Rating" Desc
""").df()

st.subheader("Who Suggests The Best Songs?")
fig = px.bar(
    best_suggestor,
    x="Average Rating",
    y="Songs Submitted By",
    orientation="h",
    text="Average Rating",
    color="Average Rating",
    color_continuous_scale=["#282828", "#1DB954"]
)

# 3. Clean up formatting
fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
fig.update_layout(
    xaxis=dict(range=[0, 10]),  # Rating scale capped at 10
    yaxis_title="",
    xaxis_title="Average Rating",
    height=280,
    margin=dict(l=0, r=20, t=10, b=10),
    coloraxis_showscale= False
)
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width= True)

pop_songs = duckdb_conn.sql("""
SELECT
    tracks.song_title,
    artists.artist_name,
    AVG(rating) as average_rating
FROM ratings
JOIN tracks
    ON ratings.track_id = tracks.track_id
JOIN artists
    ON artists.artist_id = tracks.track_id
GROUP BY song_title, artists.artist_name
ORDER BY
    average_rating Desc,
    song_title
LIMIT 10
""").df()

st.subheader("Highest Rated Songs")
st.dataframe(pop_songs , hide_index= True,
            column_config = {
                "song_title": "Song TItle",
                "artist_name":"Artist",
                "average_rating":"Average Rating"
            })


best_genre = duckdb_conn.sql("""
WITH unnest_genres AS (
    SELECT
        ratings.rater,
        ratings.rating,
        trim(lower(unnest(string_split(tracks.genres, ',')))) AS clean_genre
    FROM tracks
    JOIN ratings
        ON tracks.track_id = ratings.track_id
    WHERE tracks.genres != 'unknown'
)
SELECT
    rater,
    clean_genre,
    ROUND(AVG(rating), 2) AS avg_rating,
    COUNT(*) AS rating_count
FROM unnest_genres
GROUP BY
    rater,
    clean_genre
HAVING COUNT(*) >= 2
QUALIFY ROW_NUMBER() OVER (PARTITION BY rater ORDER BY avg_rating DESC) <=3
ORDER BY
    rater,
    avg_rating DESC,
    clean_genre

""").df()

st.subheader("What's Everyone's Favourite Genre")
st.dataframe(best_genre, hide_index= True,
             column_config= {
                "rater": "Rated By",
                "clean_genre":"Genre",
                 "avg_rating":"Average Rating",
                 "rating_count":"Times Rated"
             })

other_genre = duckdb_conn.sql("""
WITH unnest_genres AS (
    SELECT
        ratings.rater,
        ratings.rating,
        trim(lower(unnest(string_split(tracks.genres, ',')))) AS clean_genre
    FROM tracks
    JOIN ratings
        ON tracks.track_id = ratings.track_id
    WHERE tracks.genres != 'unknown'
)
SELECT
    clean_genre,
    ROUND(AVG(rating), 2) AS avg_rating,
    COUNT(*) AS rating_count
FROM unnest_genres
GROUP BY
    clean_genre
HAVING COUNT(*) >= 2
ORDER BY
    avg_rating DESC,
    clean_genre
LIMIT 5
""").df()

st.subheader("Which Genre Is The Best?")
st.dataframe(other_genre, hide_index= True,
             column_config= {
                "rater": "Rated By",
                "clean_genre":"Genre",
                 "avg_rating":"Average Rating",
                 "rating_count":"Times Rated"
             })



