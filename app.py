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
st.dataframe(disparity, hide_index= True, width="stretch",
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
st.plotly_chart(fig, width="stretch")

pop_songs = duckdb_conn.sql("""
SELECT
    tracks.song_title,
    artists.artist_name,
    AVG(rating) as average_rating,
    ratings.submitter
FROM ratings
JOIN tracks
    ON ratings.track_id = tracks.track_id
JOIN artists
    ON artists.artist_id = tracks.artist_id
GROUP BY song_title, artists.artist_name, ratings.submitter
ORDER BY
    average_rating Desc,
    song_title
LIMIT 10
""").df()

st.subheader("Highest Rated Songs")
st.dataframe(pop_songs , hide_index= True, width="stretch",
            column_config = {
                "song_title": "Song TItle",
                "artist_name":"Artist",
                "average_rating": st.column_config.NumberColumn("Average Rating", format="%.2f ★")
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
best_genre['clean_genre'] = best_genre['clean_genre'].str.title()
st.subheader("What's Everyone's Favourite Genre")

raters = best_genre['rater'].unique()

cols = st.columns(len(raters))

for col, rater in zip(cols, raters):
    with col:
        st.markdown(f"### {rater}")
        person_df = best_genre[best_genre['rater'] == rater][['clean_genre', 'avg_rating', 'rating_count']]
        st.dataframe(
            person_df,
            hide_index=True,
            width="stretch",
            column_config={
                "clean_genre": "Genre",
                "avg_rating": st.column_config.NumberColumn("Avg. Rat.", format="%.2f ★"),
                "rating_count": "Freq."
            }
        )




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
other_genre['clean_genre'] = other_genre['clean_genre'].str.title()
st.subheader("Which Genre Is Highest Rated?")
st.dataframe(other_genre, hide_index= True, width="stretch",
             column_config= {
                "rater": "Rated By",
                "clean_genre":"Genre",
                 "avg_rating": st.column_config.NumberColumn("Average Rating", format="%.2f ★"),
                 "rating_count":"Times Rated"
             })


strictness = duckdb_conn.sql("""
SELECT
    rater AS "Critic",
    ROUND(AVG(rating),2) as "Average Rating"
FROM ratings 
GROUP BY "Critic"
ORDER BY "Average Rating" Asc
""").df()

st.subheader("Who Is The Hardest To Impress?")
cols = st.columns(len(strictness))

for col, (_, row) in zip(cols, strictness.iterrows()):
    col.metric(
        label=row["Critic"],
        value=f"{row['Average Rating']:.2f} ★"
    )