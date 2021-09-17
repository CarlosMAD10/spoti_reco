import pandas as pd
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm
import requests
import json
import numpy as np
import re
import spotify_helper_functions
import scraper
import time

def import_full_df():
    """
    Function that loads the top_songs.csv in a pandas dataframe.
    No input.
    Output: the dataframe with songs and authors.
    If there is no csv file with the songs stored, the function will alert the user.
    """

    try:
        df = pd.read_csv("top_songs_complete.csv", index_col=0)
        return df
    except:
        print("No dataframe with top songs found. Run create_songs_dataframe() to create it.")
        return 0


def spotify_df(df):
    """
    Function that takes the dataframe with scraped songs-artists. 
    Through spotify it adds the top songs by the artists to the dataframe.
    Then it stores the dataframe and returns it.
    """
    #Initial list of artists that we obtain from the scraped dataset
    artist_list = df["artists"].unique().tolist()

    #Connection to spotify
    sp = spotify_helper_functions.spotify_connection()

    #We create a dictionary with artists and their ids
    full_artists_dict = {}
    for artist in artists_list:
        artists_dict = spotify_helper_functions.find_artists(artist, sp)
        if artists_dict:
            full_artists_dict.update(artists_dict)

    #For each artist, we append the songs and their attributes to a dataframe
    columns = ['song_name', 'song_id', 'artist_name', 
    'artist_id', 'danceability', 'energy', 'key', 'loudness', 
    'mode', 'speechiness', 'acousticness', 'instrumentalness', 
    'liveness', 'valence', 'tempo']

    full_df = pd.DataFrame(columns=columns)

    #There will be nested for loops: for each artist we find the top songs.
    #And for each song we get the attributes.
    for artist_name, artist_id in full_artists_dict.items():
        songs_dict = spotify_helper_functions.get_top_songs(artist_id, sp)

        if songs_dict:
            for song_name, song_id in songs_dict.items():
                if song_id:
                    attributes = spotify_helper_functions.get_songs_attributes(song_id, sp)
                    if attributes:
                        #We expand the attributes dictionary for each song with the artist and song info
                        attributes.update({"artist_name":artist_name, "artist_id":artist_id,
                            "song_name": song_name, "song_id":song_id})
                        #And then we store all the data in the dataframe
                        full_df = full_df.append(attributes, ignore_index=True)

    full_df = full_df.drop_duplicates(subset="song_id")
    full_df.to_csv("spotify_df.csv")
    print(f"Created dataset with the songs and features from Spotify. Total of {len(full_df)} songs.")
    return full_df

def extend_df(df, save_path="final_df.csv"):
    """
    Function that takes the stored dataframe with spotify songs and their features, and
    extends it with more songs from recommended artists
    """

    sp = spotify_helper_functions.spotify_connection()

    #We extract the ids of the artists in the initial dataframe
    artist_id_list = df["artist_id"].unique()

    #We preload them in the extended dictionary in order to avoid repeating them
    extended_artist_dict = {df.loc[df["artist_id"]==artist_id, \
    "artist_name"].unique()[0]:artist_id for artist_id in artist_id_list}

    #We introduce a count variable to sleep for 15 seconds every 15 artists. This way we avoid running over the 
    #30 seconds rolling limit of the Spotify API
    count = 0

    #Now we iterate through the id list and use the function to find related artists, adding them
    #to the dictionary
    for artist_id in artist_id_list:
        more_artists = spotify_helper_functions.find_related_artists(artist_id, sp)
        if more_artists != None:
            extended_artist_dict.update(more_artists)

    #With the extended artist dictionary, we find the most popular songs and include them in the df
    for artist_name, artist_id in extended_artist_dict.items():
        songs_dict = spotify_helper_functions.get_top_songs(artist_id, sp)

        if songs_dict:
            print(f"Appending {len(songs_dict)} songs by {artist_name}")

            for song_name, song_id in songs_dict.items():
                if song_id:
                    attributes = spotify_helper_functions.get_songs_attributes(song_id, sp)
                    if attributes:
                        #We expand the attributes dictionary for each song with the artist and song info
                        attributes.update({"artist_name":artist_name, "artist_id":artist_id,
                            "song_name": song_name, "song_id":song_id})
                        #And then we store all the data in the dataframe
                        df = df.append(attributes, ignore_index=True)
        #We store it after each new artist is added, in case there is a connection timeout
        df.to_csv(save_path)
        
        #Sleeping
        count += 1
        if count % 15 == 0:
            print("Sleeping 10 seconds.")
            time.sleep(10)

    df = df.drop_duplicates(subset="song_id")
    df.to_csv(save_path)
    print(f"Created the final dataset with the songs and features from Spotify. Total of {len(df)} songs.")
    return df


def main():
    initial_df = scraper.import_top_songs()

    try:
        middle_df = pd.read_csv("spotify_df.csv", index_col=0)
    except:
        print("Creating spotify dataset")
        middle_df = spotify_df(initial_df)

    print("Extending dataset...")
    final_df = extend_df(middle_df)

    return 0

if __name__=="__main__":
    main()
