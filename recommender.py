import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import numpy as np
import re
import random
import spotify_helper_functions
import clustering_music
from difflib import get_close_matches


def import_top_songs(path="top_songs.csv"):
    top_df = pd.read_csv(path, index_col=0)
    top_df = top_df.applymap(lambda x: x.lower())
    
    return top_df

def import_spotify_df(path="spotify_songs.csv"):
    df = pd.read_csv(path, index_col=0)
    df["song_name"] = df["song_name"].apply(lambda x: x.lower())
    df["artist_name"] = df["artist_name"].apply(lambda x: x.lower())
    return df


def is_similar(user_input, name_series):
    """
    Finds if a name is similar to a pandas series that is given as input. It uses a built in algorithm that
    checks the similarity of sequences, through the Function get_close_matches.
    Input: the name (song or artist) we would like to search for, and the series.
    Output: a list with the name or names that is similar or equal, if it finds it; empty list if there are no close matches.
    """
    #We extract the list of names from the series which we get as an input, and make them lowecase. 
    #We also remove special characters using the translate string method
    name_list = name_series.to_list()


    # The function will return the closest matches in the list, or an empty list if there are none
    close_matches = get_close_matches(user_input, name_list, n=3, cutoff=0.90)

    return close_matches

def is_top_song(user_input, df):

    song_series = df["songs"]

    return is_similar(user_input, song_series)


def is_spotify_song(user_input, df):

    song_series = df["song_name"]

    matches = is_similar(user_input, song_series)

    if matches == []:
        return []
    else:
        list_ids = []
        match_series = df.loc[df["song_name"] == matches[0], "song_id"]
        for song_id in match_series:
            list_ids.append(song_id)
        return list_ids

def choice(options, df, sp, names_or_ids="ids"):
    print("Select one of the following choices:")
    
    if names_or_ids == "names":
        for index, item in enumerate(options):
            print(f"Option {index + 1} - {item}")
        while True:
            try:
                choice = int(input("Selection: "))
                if choice >= 1 and choice <= len(options):
                    return options[choice-1]
            except:
                continue
    else:
        #Second case, list with song_ids. We return the song_id

        for index, song_id in enumerate(options):
            song_name, artist_name = spotify_helper_functions.get_song_info(song_id, sp)
            print(f"Option {index + 1} - {song_name} by {artist_name}")
        while True:
                try:
                    choice = int(input("Selection:"))
                    if choice >= 1 and choice <= len(options):
                        return options[choice-1]
                except:
                    continue



def recommend_top_song(song_name, df):
    while True:  # Loop so we don't recommend the same song the user inputs.
        random_row = random.choice(range(len(df)))
        random_song = df.iloc[random_row, 0]
        random_artist = df.iloc[random_row, 1]

        if random_song != song_name:
            break

    print(f"TOP recommendation! A similar song to {song_name.capitalize()} that you might \
like is {random_song.capitalize()}, by {random_artist.capitalize()}.")

    return {"song_name":random_song, "artist_name":random_artist}


def recommend_spotify_song(song_id, df, model, sp_connection):

    modeling_df = df.drop(columns=["song_name", "artist_name", "artist_id", "song_id"])
    clusters = model.predict(modeling_df)

    data = {"song_name": df["song_name"], "song_id": df["song_id"], "artist_name": df["artist_name"],
     "artist_id": df["artist_id"], "cluster": clusters}

    names_ids_df = pd.DataFrame(data=data)

    if song_id in names_ids_df["song_id"]:
        recommendation_cluster = names_ids_df.loc[names_ids_df["song_id"] == song_id, "cluster"].unique()[0]
    else:
        attributes = spotify_helper_functions.get_songs_attributes(song_id, sp_connection)
        row = pd.DataFrame(data=attributes, index=modeling_df.columns)
        recommendation_cluster = model.predict(row)[0]

    mask = names_ids_df["cluster"] == recommendation_cluster
    recommendation_df = names_ids_df.loc[mask, ["song_name", "artist_name", "artist_id", "song_id", "cluster"]]

    random_row = random.choice(range(len(recommendation_df)))

    song_rec_name = names_ids_df.iloc[random_row, 0].capitalize()
    song_rec_artist = names_ids_df.iloc[random_row, 2].capitalize()
    song_rec_id = names_ids_df.iloc[random_row, 1]

    print(f"Spotify recommendation! A song you might like is {song_rec_name}, by {song_rec_artist}! ")
    
    return song_rec_id, song_rec_name, song_rec_artist

    
def song_recommender(n = 5):

    #We create the Spotify connection
    sp = spotify_helper_functions.spotify_connection()

    #We load the two datasets: top songs and spotify songs
    top_df = import_top_songs(path="top_songs.csv")
    spotify_df = import_spotify_df(path="spotify_songs.csv")

    #We load the model that we will use
    model = clustering_music.load_model(path="music_model.pkl")

    user_input = input("Please insert the name of the song that you like: ").lower()

    #1. First we check if it is in the top df, and we offer the choice to the user
    top_song = is_top_song(user_input, top_df)  #This value will be [] if there are no similar songs

    if top_song != []:
        if len(top_song) == 1:
            top_recommended = recommend_top_song(top_song[0], top_df)
            return 0
        else:
            song_choice = choice(top_song, spotify_df, sp, names_or_ids="names")
            top_recommended = recommend_top_song(song_choice, top_df)
            return 0

    #2. If the song is not in the top list, we search in the spotify_df
    spoti_song = is_spotify_song(user_input, spotify_df)

    if spoti_song == []:
        possible_tracks = spotify_helper_functions.find_possible_songs(user_input,sp)
        if possible_tracks:
            song_choice_id = choice(list(possible_tracks.values()), spotify_df, sp)
            for _ in range(n):
                spoti_recommended = recommend_spotify_song(song_choice_id, spotify_df, model, sp)
            return 0
        else:
            print("Sorry, we didn't find any matches in Spotify")

    elif len(spoti_song) == 1:
        for _ in range(n):
            spoti_recommended = recommend_spotify_song(spoti_song[0], spotify_df, model, sp)
        return 0
    
    else:
        song_choice_id = choice(spoti_song, spotify_df, sp)
        for _ in range(n):
            spoti_recommended = recommend_spotify_song(song_choice_id, spotify_df, model, sp)
        return 0


def main():

    song_recommender()
    


if __name__=="__main__":
    main()
