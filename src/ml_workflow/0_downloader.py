import spotipy, json, os
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from operator import is_not
from functools import partial

client_id = '342693a5bc7240649bb8cb8a17f81e0b'
client_secret = '17d4bd23b0d24287af971ec919e65d19'
client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def __read_file(filename: str) -> dict:
    try:
        with open(filename) as f:
            data = json.load(f)
        return data
    except:
        print("No such file!")
        return None

def __write_file(filename: str, data: dict) -> None:
    current_path = os.path.dirname(os.path.realpath(__file__)) 
    file = os.path.join(current_path, "data", filename)
    try:
        with open(file, "w") as f:
            json.dump(data, f)
        print(f"Saved data to: {file}")
    except:
        print(f"Could not write to file: {file}")

def get_track_IDs_from_playlist_ID(playlist_ID: str) -> list:
    ids = []

    playlist = sp.playlist_items(playlist_ID)
    total_tracks = playlist["total"]
    offset = 0

    while total_tracks > 0:
        playlist = sp.playlist_items(playlist_ID, offset=offset)
        total_tracks -= 100
        offset += 100
        ids += [i["track"]["id"] for i in playlist["items"]]
        
    # return a list of all track ids without None values
    return list(filter(partial(is_not, None), ids))

def get_features_from_track_IDs(track_IDs: list) -> list:
    features = []

    for i in range(0, len(track_IDs), 100):
        last = i + 99
        if i + 99 > len(track_IDs): last = len(track_IDs) - 1
        print(f'Request features in range: {i} - {last}')
        try:
            # try to get 100 track features at a time which is the limit
            features += sp.audio_features(tracks=track_IDs[i:last])
        except:
            # but if some exception happens, it might be a single wrong track id ->  we don't want to miss out on 100 track features, lets iterate over each trackID and throw away the bad trackID where the exception happened, this is perfectly fine since the code should never go in here, but if it does it's probably only once in a lot of requests (only happened with None values during testing, but we already removed None values earlier)
            tracks = track_IDs[i:last]
            for track in tracks:
                try:
                    feature = sp.audio_features(tracks=[track])
                    features.append(feature)
                except: continue

    return features

def extract_features_from_playlist(playlist_ID: str, genre: str, filename: str = None) -> None:
    track_IDs = get_track_IDs_from_playlist_ID(playlist_ID)
    features = get_features_from_track_IDs(track_IDs)

    # list comprehension to add the key genre to each dict in a list of dicts
    features = [dict(f, **{"genre": genre}) for f in features]
    if filename is None: filename = playlist_ID + ".json"
    __write_file(filename, features)

if __name__ == '__main__':

    # https://open.spotify.com/playlist/37i9dQZF1DWZJhOVGWqUKF?si=18913d45450d4410
    rock_playlist = "37i9dQZF1DWZJhOVGWqUKF"
    extract_features_from_playlist(rock_playlist, "rock")

    # https://open.spotify.com/playlist/37i9dQZF1DXcfWvNFKxjDo?si=6f5b1958827149ff
    edm_playlist = "37i9dQZF1DXcfWvNFKxjDo"
    extract_features_from_playlist(edm_playlist, "edm")
