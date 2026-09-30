import duckdb
import streamlit as st
import plotly.express as px


st.title("Whose Music Taste is Best?")
st.text('Quantifying group taste through track submission scores, rating distributions, and listener consensus.')

duckdb_conn = duckdb.connect( "music_data.duckdb", read_only=True)

st.divider()

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


fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
fig.update_layout(
    xaxis=dict(range=[0, 10]),
    yaxis_title="",
    xaxis_title="Average Rating",
    height=280,
    margin=dict(l=0, r=20, t=10, b=10),
    coloraxis_showscale= False
)
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, width="stretch")


with st.expander("How this calculation works"):
    st.write("""
    **Mean Rating** - The average rating given by other group members to a user's submitted tracks.
    """)

st.divider()


pop_songs = duckdb_conn.sql("""
SELECT
    tracks.song_title,
    artists.artist_name,
    AVG(rating) as average_rating,
    ratings.submitter as "Submitted By"
FROM ratings
JOIN tracks
    ON ratings.track_id = tracks.track_id
JOIN artists
    ON artists.artist_id = tracks.artist_id
GROUP BY 
        tracks.track_id, 
        tracks.song_title, 
        artists.artist_name, 
        "Submitted By"
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


with st.expander("How this calculation works"):
    st.write("""
    **High Score!** - The average rating of each submitted song given by other group members.
    """)


st.divider()


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


with st.expander("How this calculation works"):
    st.write("""
    **Mean Score Awarded** - The average rating each member gives to other people's song submissions. Lower average means harsher critic.
    """)

st.divider()



disparity = duckdb_conn.sql("""
SELECT
    tracks.song_title,
    artists.artist_name,
    MAX(ratings.rating) - MIN(ratings.rating) AS rating_disparity
FROM ratings
JOIN tracks
    ON tracks.track_id = ratings.track_id
JOIN artists
    ON artists.artist_id = tracks.artist_id
GROUP BY tracks.track_id, tracks.song_title, artists.artist_name
ORDER BY rating_disparity Desc, tracks.song_title
LIMIT 5;
""").df()

st.subheader("Most Divisive Songs")
st.dataframe(disparity, hide_index= True, width="stretch",
             column_config = {
                 "song_title": "Song Title",
                 "artist_name": "Artist",
                 "rating_disparity": "Difference Of Rating" 
             },)

with st.expander("How this calculation works"):
    st.write("""
    **Rating Disparity** - Calculated as $\\text{MAX}(rating) - \\text{MIN}(rating)$ for each song to highlight tracks with the widest split in reviewer opinions.
    """)



st.divider()


nicheness = duckdb_conn.sql("""
WITH user_tracks AS (
    SELECT submitter AS user_name, track_id FROM ratings WHERE submitter IS NOT NULL
    UNION
    SELECT rater AS user_name, track_id FROM ratings WHERE rating >= 7 AND rater IS NOT NULL
),
user_medians AS (
    SELECT
        user_name,
        MEDIAN(tracks.listeners) AS median_listeners
    FROM user_tracks
    JOIN tracks ON tracks.track_id = user_tracks.track_id
    GROUP BY user_name
)
SELECT
    ROW_NUMBER() OVER (ORDER BY median_listeners ASC) AS "Nicheness Rank",
    user_name AS "Name",
    ROUND(median_listeners, 0) AS "Median Listeners"
FROM user_medians
ORDER BY "Nicheness Rank" ASC;
""").df()

st.subheader("🏆 Most Niche Music Taste")

if len(nicheness) >= 3:
    col1, col2, col3 = st.columns(3)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🥇 1st Place**")
    st.subheader(nicheness.iloc[0]["Name"])
    st.caption(f"{int(nicheness.iloc[0]['Median Listeners']):,} median listeners")

with col2:
    st.markdown("**🥈 2nd Place**")
    st.subheader(nicheness.iloc[1]["Name"])
    st.caption(f"{int(nicheness.iloc[1]['Median Listeners']):,} median listeners")

with col3:
    st.markdown("**🥉 3rd Place**")
    st.subheader(nicheness.iloc[2]["Name"])
    st.caption(f"{int(nicheness.iloc[2]['Median Listeners']):,} median listeners")


with st.expander("How this calculation works"):
    st.write("""
    **Nicheness Score** - Calculated as the median Last.fm listener count across all tracks each member submitted or awarded a $7/10$ or higher. Lower medians represent a more underground taste profile.
    """)



st.divider()



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
st.subheader("What Is Your Favourite Genre?")

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



with st.expander("How this calculation works"):
    st.write("""
    **Personal Top Genres** - Displays each member's top 3 genres based on the average rating awarded across rated tracks, filtered for genres reviewed at least twice.
    """)

st.divider()



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


with st.expander("How this calculation works"):
    st.write("""
    **Group Top Genres** - Ranks genres by the average rating received across all group members.
    """)


ratings_df = duckdb_conn.sql("""
    SELECT 
        rater AS "Group Member", 
        rating AS "Rating"
    FROM ratings 
    WHERE rater IS NOT NULL
""").df()

st.subheader("Rating Distribution & Score Spreads")

fig = px.histogram(
    ratings_df,
    x="Rating",
    color="Group Member",
    barmode="group",  # Options: 'group' (side-by-side) or 'overlay' (stacked)
    nbins=10,
    labels={"Rating": "Score Awarded", "count": "Count"},
    color_discrete_sequence=px.colors.qualitative.Plotly
)

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#FFFFFF",
    xaxis=dict(dtick=1, range=[0.5, 10.5], title="Rating (1-10)"),
    yaxis=dict(title="Number of Scores Given"),
    legend_title_text="Member",
    bargap=0.15
)

st.plotly_chart(fig, use_container_width=True)

with st.expander("How this calculation works"):
    st.markdown(
        "**Score Spread:** Visualises how frequently each member awards specific ratings (1–10). "
    )
