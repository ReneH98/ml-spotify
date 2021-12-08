import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time 

def getTrackIDsFromPlaylistID(playlist_id):
    ids = []
    playlist = sp.playlist_items(playlist_id)
    
    for track_item in playlist['items']:
        ids.append(track_item['track']['id'])
        
    return ids

if __name__ == '__main__':
    client_id = '342693a5bc7240649bb8cb8a17f81e0b'
    client_secret = '17d4bd23b0d24287af971ec919e65d19'

    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    track_ids = getTrackIDsFromPlaylistID('37i9dQZF1DX4jP4eebSWR9')

    features = sp.audio_features(tracks=track_ids)
    print(features)