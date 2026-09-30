# Friend Group Music Taste Analyser

A program that analyses and displays a group music taste - including analysis of genre trends, favourite songs, "nicheness", and more...

---

## About Me

As a passionate music fan, choosing a music-related project was never in doubt. However, my interest in data engineering and analysis stems from my academic background and enjoyment of combining technical skills to solve problems. As a recent graduate with a BSc in chemistry and mathematics (international) from the University of Leeds, I particularly enjoyed applying mathematical and computational methods to real-world problems, whether that involved analysing experimental results in chemistry or using complex equations to solve and model quantum mechanical systems in my final-year project.

Throughout my degree, I have always enjoyed the process of learning new skills. This included teaching myself Python in order to numerically solve the Schrödinger equation, as well as studying unfamiliar subjects on my year abroad such as finance, economics, and accountancy. These experiences strengthened my interest in applying my quantitative skills to new fields.

The Information Lab offers a unique opportunity to develop new skills and apply them in the workplace soon afterwards. I have enjoyed developing my foundational SQL knowledge through the University of Michigan's Coursera course, alongside independent practice using platforms such as SQLBolt and Exercism. However, I am excited by the opportunity to take these skills further. The Information Lab's personal approach to learning and developing new skills, particularly with the support of a dedicated daily coach really interests me, and I believe this would be the ideal environment to develop my technical skills while gaining experience in a professional setting.

This project combines my passion for music, with my growing interest in working with data. Developing the project has allowed me to put my Python and SQL knowledge into practice, moving beyond tutorials and online exercises to build something practical. I have really enjoyed the process of turning raw data into useful analysis and insights.


---
## What I built and who for?
Often, me and my friends share a lot of music recommendations to one another. However, we kept having the same problem where we thought we understood one another's taste, and would recommend a song we thought they would love, only for them to hate it. I have always wanted to create a small personal project that could help us understand what each other's music taste really was. So, I built this project.

This program can easily be adapted to increase the number of friends involved, the number of songs involved or the names of people/songs just be changing the `raw_ratings.csv` file.

## How it works
Initially, I gave my 2 friends 10 songs I had recommended for them, asked them to rate them 1 to 10 and then asked them to suggest another 10 songs of their own. This gave me a small dataset of 30 songs to which I could use to write this program.

Using the Last.fm API, information about each individual song and artist is gathered and saved in the `/raw_jason` folder as JSON files, so that the program can function offline. Each file contains information on the song/artist, like total listeners/playcount and user created tags which are generally the genre of the song or artist. When the song did not have an attached artist (generally because the song was not popular enough for other users to tag it), the program would fallback and use the artist's tags.

After extracting the relevant information from the API for each song, the `transform_load.py` file uses the JSON files and cleans the data extracted, such as removing clutter and simplifying the tags/genres. Then all the information is loaded into a dataframe from which 3 tables (ratings, tracks, and artists) in duckdb are formed, each with primary keys and foreign keys.

Finally, a streamlit app is created that uses SQL statements to create tables, plots and charts to analyse and present visualisations that display the key information.

## The Results
I had 6 key questions I wanted the project to answer for me and my friends:
1. Who was the strictest/harshest critic?
2. What was everyones preference in genre?
3. Who has the nichest taste?
4. Who's suggestions were most liked?
5. Which songs were highest rated?
6. Which songs were the most divisive?

Due to a small dataset of only 30 songs, the results are quite limited as trends are much less obvious. However, with more time, I could easily add more songs to the list to be reviewed, or even more friends to review the songs which would greatly improve the visualisations and trends.

## The API

[Last.fm Documentation](https://www.last.fm/api)
I used the Last.fm API due to it having an advantage over other free music APIs as it had a listener and playcount. The user can get a free API key easily by signing up here : [Last.fm account creation](https://www.last.fm/api/account/create) . I placed a time.sleep(1) function on all my API calls as to not overload the system, however there are no specific rules on how often a user can call from the API. I used the `requests.get(url, params=params)` function to query the API, using the url `http://ws.audioscrobbler.com/2.0/` and changing the parameters depending on whether I wanted the artist or the track data (`artist.getInfo` or `track.getInfo`). The `extract.py` file loads a private `.env` file which includes the `LASTFM_API_KEY=` and the `LASTFM_SHARED_SECRET=` . The API returns either XML or JSON, I used JSON for this program.

## How To Run

### Prerequisites: 
Python 3.9+ and Git

### Clone the repository: 
```
git clone https://github.com/zwarner2003-hue/music-analysis.git
cd music-analysis
```

### Create a virtual environment
(On Windows):
```
python -m venv venv
venv\Scripts\activate
```
(On Mac/Linux):
```
python3 -m venv venv
source venv/bin/activate
```

### Install the dependencies: 
```
pip install -r requirements.txt
```

### To run the program online (skip if wanting to run offline):
Sign up to the Last.fm API and create a `.env` file containing `LASTFM_API_KEY=your_key_here` and run ```python extract.py```

### Build the duckdb database: 
```
python transform_load.py
```

### Launch the streamlit app:
```
streamlit run app.py
```

You do not need to call the API to run this program, all the JSON files are committed in the `/raw_jason` directory. 



## What I Would Improve

With more time, I would try to implement a more complex metric for analysis. 

I had the idea of improving my "nicheness" metric and how I decide how to measure how niche someone's music taste is. At first I had the idea of taking $ \frac{1}{\text{listeners}} \times \text{rating} $ as a formula for calculating a "nicheness" of someone's taste, however I realised that if a user was submitting songs with low listener count themselves, they would be penalised because they could not rate their own songs. To fix this I gave each submission a default 7/10 rating by the user that submitted the track. Then, I noticed a "rating inflation", when one user was a less harsh/strict critic than the others, so I tried to implement a Z-Score Normalisation to counter this, however I could not find a way to implement all this correctly and still achieve results I thought were accurate within the timeframe I had. Instead, I used a reliable baseline, and calculated "nicheness" by taking the average of all songs a user submitted, or rated 7 or higher. With more time, I will fully implement the Z-score normalization to dynamically account for reviewer bias.

Other improvements would be to improve the usage of the notes written by users, I believe the notes could be useful on the dashboard to give more context to songs. Also, I would implement a second API that contains more detailed data about each song and artist, such as tempo, more specific genres, or danceability to improve the bredth of the trends that could be analysed.



## AI Assistance
To begin with I had many ideas of directions to take my project, however, having never undertaken a similar project, I used AI to check the feasibility of such ideas within the time limit I had set myself. Throughout the process of writing the code, whenever the program was broken and I could not see where the issue was, I would use the built in Copilot agent in VS Code to troubleshoot and locate the root of the issue. Lastly, having never created a streamlit app before, after creating very basic tables myself, I used AI to improve the UI of the app itself, such as adding more colour and improving general display.