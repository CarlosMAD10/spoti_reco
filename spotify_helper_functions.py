import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json

def spotify_connection(path=r"C:\Users\carlo\OneDrive\Programming\spotify.txt"):
        """
        Function that returns the Spotify client object. 
        """
        try:
                with open(path) as file:
                        client_id = file.readline().strip()
                        client_secret = file.readline().strip()
        except:
                client_id = input("Enter your client_id for the Spotify client: ")
                client_secret = input("Enter your client_secret for the Spotify client: ")

        #Connect to spotify
        try:
                auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        except:
                print("Could not connect to Spotify. Try another client id and secret.")
                exit()

        sp = spotipy.Spotify(client_credentials_manager=auth_manager)

        return sp

def find_artists(name, sp):
        """
        Function that returns names and ids of artists, through a Spotify query.
        Input: the name of an artist (string) and the Spotify object.
        Output: a dictionary with the artist/s name/s and id/s that it finds. 
        """
        info = sp.search(q="artist: " + name, type="artist")
        dict_artists = {}

        if info["artists"]["items"] == []:
                return None

        for item in info["artists"]["items"]:
                dict_artists[item["name"]] = item["id"]
        
        return dict_artists

def get_top_songs(artist_id, sp):
        """
        Function that takes the id of an artist and a spotify connection, and returns
        a dictionary with names and ids of songs by the artist.
        Input: the id of the artist and the spotify connection.
        Output: a dictionary with songs names and ids.
        """
        info = sp.artist_top_tracks(artist_id)
        songs_dict = {}

        if info["tracks"] == []:
                return None

        for song in info["tracks"]:
                songs_dict[song["name"]] = song["id"]

        return songs_dict

def get_songs_attributes(song_id, sp):
        """
        Function that takes the id of a track and returns a dictionary with its 
        features or attributes, as received from Spotify.
        Input: the track if and the spotify connection´.
        Output: a dictionary that stores selected songs features.
        """
        info = sp.audio_features(song_id)

        if len(info) == 0:
                return None

        features = info[0]

        if features == {} or type(features) != dict:
                return None

        selected_features = ['danceability', 'energy', 
        'key', 'loudness', 'mode', 'speechiness', 'acousticness',
         'instrumentalness', 'liveness', 'valence', 'tempo']

        final_dict = {}

        for key, value in features.items():
                if key in selected_features:
                        final_dict[key] = value
        
        return final_dict

def find_related_artists(artist_id,sp):

        related = sp.artist_related_artists(artist_id)

        if len(related) == 0:
                return None
        dict_related = {}

        for artist in related["artists"]:
                dict_related[artist["name"]] = artist["id"]

        return dict_related

def find_possible_songs(song_name, sp):

        possible_tracks = sp.search(q="track: " + song_name, type="track")["tracks"]["items"]

        if len(possible_tracks) == 0:
                return None
        
        dict_tracks = {}

        for track in possible_tracks:
                dict_tracks[track["name"]] = track["id"]

        return dict_tracks

def get_song_info(song_id, sp):

        song_info = sp.track(song_id)
        song_name = song_info["name"]
        artist_name = song_info["album"]["artists"][0]["name"]
        return song_name, artist_name