import pandas as pd
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm
import requests
import json
import numpy as np
import re

def import_top_songs():
    """
    Function that loads the top_songs.csv in a pandas dataframe.
    No input.
    Output: the dataframe with songs and authors.
    If there is no csv file with the songs stored, the function will alert the user.
    """

    try:
        df = pd.read_csv("top_songs.csv", index_col=0)
        return df
    except:
        print("No dataframe with top songs found. Run create_songs_dataframe() to create it.")
        return 0

def create_songs_dataframe():
    """
    Function that secrapes songs and stores them in a csv. The sources for the songs are:
    1) The hot 100 at billboard.com
    2) The top 100 at popvortex.com
    No input.
    Returns the df
    """

    #Songs from hot 100 billboard

    #download the webpage
    url = "https://www.billboard.com/charts/hot-100"
    page = requests.get(url)

    if page.status_code != 200:
        print(f"Error downloading the first page. Error {page.status_code}")
        exit(0)

    # parse the html
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get a list with information about each of the 100 songs.
    info = soup.find_all("span", {"class":"chart-element__information"})

    #Select the relevant parts: track and artist
    songs = []
    artists = []
    for value in info:
        song = value.find_all("span", {"class": "chart-element__information__song text--truncate color--primary"})[0].get_text()
        artist = value.find_all("span", {"class": "chart-element__information__artist text--truncate color--secondary"})[0].get_text()
        songs.append(song)
        artists.append(artist)

    #Create the dataframe
    df = pd.DataFrame(data={"songs":songs, "artists": artists})

    #Download the second webpage
    #download the webpage
    url = "http://www.popvortex.com/music/charts/top-100-songs.php"
    page = requests.get(url)

    if page.status_code != 200:
        print(f"Error downloading the second page. Error {page.status_code}")
        exit(0)

    # parse the html
    soup = BeautifulSoup(page.content, 'html.parser')

    #Get the information
    title_artists = soup.find_all("p", {"class":"title-artist"})

    #We include them in the dataframe
    for elem in title_artists:
        track = elem.cite.string
        artist = elem.em.string
        df = df.append({"songs":track, "artists": artist}, ignore_index=True)

    #Dropping dupllicated songs and resetting the index.
    df = df.drop_duplicates(subset="songs").reset_index(drop=True)

    #Saving the datframe in a csv
    df.to_csv("top_songs.csv")

    print("Dataframe with top songs created: top_songs.csv")

    return df

def main():
    df = create_songs_dataframe()
    return 0

if __name__=="__main__":
    main()
