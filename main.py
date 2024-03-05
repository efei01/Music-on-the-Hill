import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

CLIENT_ID = "<client_id>"
CLIENT_SECRET = "<client_secret>"
client_credentials_manager = SpotifyClientCredentials(client_id = CLIENT_ID, client_secret = CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def search_artist(name):
    results = sp.search(q='artist:' + name, type='artist', limit=1)
    items = results['artists']['items']
    if len(items) > 0:
        return items[0]  # Returns the first matching artist
    else:
        return None

st.title('Music on the Hill '
         '\n'
         'Spotify Artist Dashboard')

artist_name = st.text_input('Enter Artist Name')

def search_album(name):
    results = sp.search(q='album:' + name, type='album', limit=1)
    items = results['albums']['items']
    if len(items) > 0:
        return items[0]
    else:
        return None

def get_all_albums_df(artist_id):
    all_albums = []
    offset = 0
    limit = 50  # Maximum limit per request
    while True:
        albums = sp.artist_albums(artist_id, album_type='album', limit=limit, offset=offset)
        if not albums['items']:
            break
        for album in albums['items']:
            all_albums.append({
                'Album Name': album['name'],
                'Release Date': album['release_date']
            })
        offset += limit
    df = pd.DataFrame(all_albums)
    return df

def get_all_album_titles(artist_id):
    all_albums = []
    offset = 0
    limit = 50

    while True:
        albums = sp.artist_albums(artist_id, album_type='album', limit=limit, offset=offset)
        if not albums['items']:
            break
        for album in albums['items']:
            all_albums.append(album['name'])
        offset += limit
    return all_albums

def get_album_tracks_df(album_id):
    tracks = []
    # Retrieve tracks from the album
    album_tracks = sp.album_tracks(album_id)
    for track in album_tracks['items']:
        # Retrieve popularity for the track
        track_id = track['id']
        track_popularity = sp.track(track_id)['popularity']

        tracks.append({
            'Track Name': track['name'],
            'Track Number': track['track_number'],
            'Duration': track['duration_ms'],
            'Popularity': track_popularity
        })
    df = pd.DataFrame(tracks)
    return df

def get_all_tracks(artist_id, country='US'):
    all_songs = []
    album_titles = get_all_album_titles(artist_id)
    for album_title in album_titles:
        album = search_album(album_title)
        album_id = album['id']
        album_tracks_df = get_album_tracks_df(album_id)

        album_tracks_df['Album'] = album_title
        all_songs.append(album_tracks_df)
    all_songs_df = pd.concat(all_songs, ignore_index=True)
    return all_songs_df


def artist_info(artist):
    st.write(f"Name: {artist['name']}")
    st.write(f"Genres: {', '.join(artist['genres'])}")
    st.write(f"Popularity: {artist['popularity']}")
    st.image(artist['images'][0]['url'], width=200)
    top_tracks = sp.artist_top_tracks(artist['id'])
    tracks_df = pd.DataFrame(top_tracks['tracks'],
                             columns=['name',
                                      'popularity',
                                      'external_urls'])
    st.write(tracks_df)

    tracks = get_all_tracks(artist['id'])

    album_popularity = plt.figure()
    albums = tracks["Album"].unique()
    #albums = np.sort(albums)
    popularity = []
    for album in albums:
        popularity.append(tracks["Popularity"][tracks["Album"] == album].mean())
    plt.bar(albums, popularity, figure=album_popularity)
    plt.xlabel('Album')
    plt.xticks(range(len(albums)), albums, rotation='vertical')
    plt.ylabel('Average Popularity')
    plt.title('Average Popularity Score by Album')
    plt.savefig('album_popularity.png')
    st.image('album_popularity.png', width=500)

if st.button('Search'):
    artist = search_artist(artist_name)
    if artist:
        artist_info(artist)
    else:
        st.write("Artist not found.")

artist_name = "Lorde"  # Example artist
artist = search_artist(artist_name)
if artist:
    print(f"Name: {artist['name']}")
    print(f"Genres: {', '.join(artist['genres'])}")
    print(f"Popularity: {artist['popularity']}")
    print(f"Followers: {artist['followers']['total']}")
    print(get_all_tracks(artist['id']))
