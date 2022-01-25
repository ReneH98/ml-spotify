from matplotlib.pyplot import new_figure_manager
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
        playlist["items"] = list(filter(partial(is_not, None), playlist["items"]))

        id_list = []
        for item in playlist["items"]:
            try:
                id_list.append(item["track"]["id"])
            except: pass

        #id_list = [i["track"]["id"] for i in playlist["items"]]

        ids += list(set(id_list))
        
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

def extract_features_from_multiple_playlists(playlist_dict: dict) -> None:
    for genre, playlist_list in playlist_dict.items():
        track_ID_list = []
        features = list()
        for playlist_ID in playlist_list:
            track_IDs = get_track_IDs_from_playlist_ID(playlist_ID)
            track_ID_list += track_IDs

        features = get_features_from_track_IDs(track_ID_list)
        features = list(filter(partial(is_not, None), features))
        features = [dict(f, **{"genre": genre}) for f in features]

        __write_file(genre + ".json", features)

if __name__ == '__main__':

    playlist = {
        "rock": [
            "37i9dQZF1DWZJhOVGWqUKF", # https://open.spotify.com/playlist/37i9dQZF1DWZJhOVGWqUKF?si=d7e98ab126fc4775 100
            "37i9dQZF1DX4vth7idTQch", # https://open.spotify.com/playlist/37i9dQZF1DX4vth7idTQch?si=b6615e9fe24247e0 100
            "37i9dQZF1DX3oM43CtKnRV", # https://open.spotify.com/playlist/37i9dQZF1DX3oM43CtKnRV?si=22531f45d2ab4fa3 100
            "37i9dQZF1DX1spT6G94GFC", # https://open.spotify.com/playlist/37i9dQZF1DX1spT6G94GFC?si=da016a8b75ca4184 80
            "37i9dQZF1DXcF6B6QPhFDv", # https://open.spotify.com/playlist/37i9dQZF1DXcF6B6QPhFDv?si=8625e0be663f4817 50
            "37i9dQZF1DWWzBc3TOlaAV"  # https://open.spotify.com/playlist/37i9dQZF1DWWzBc3TOlaAV?si=96185faf547f4064 90
                                                                                                                   # 520
        ],
        "edm": [
            "37i9dQZF1DX0pH2SQMRXnC", # https://open.spotify.com/playlist/37i9dQZF1DX0pH2SQMRXnC?si=19a3ef5d30d54f06 200
            "37i9dQZF1DX6J5NfMJS675", # https://open.spotify.com/playlist/37i9dQZF1DX6J5NfMJS675?si=51bc4eb90bfb45c4 60
            "37i9dQZF1DX7ZUug1ANKRP", # https://open.spotify.com/playlist/37i9dQZF1DX7ZUug1ANKRP?si=ad499640a06c4936 50
            "6FjUyONoZCmdvKPfeWEohP", # https://open.spotify.com/playlist/6FjUyONoZCmdvKPfeWEohP?si=60e85e51ee6c4dc1 130
            "5oJkaanfqM8upo86pAu96I" # https://open.spotify.com/playlist/5oJkaanfqM8upo86pAu96I?si=c4c9a13fbc5e4943 70
                                                                                                                   # 510
        ],
        "classic": [
            "37i9dQZF1DXaHEllsiT8lf", # https://open.spotify.com/playlist/37i9dQZF1DXaHEllsiT8lf?si=268afb23cad843dd 95
            "37i9dQZF1DWZf52HmhYw49", # https://open.spotify.com/playlist/37i9dQZF1DWZf52HmhYw49?si=3615d6f7e736421b 50
            "37i9dQZF1DWWEJlAGA9gs0", # https://open.spotify.com/playlist/37i9dQZF1DWWEJlAGA9gs0?si=e72bea12b8a74858 148
            "1h0CEZCm6IbFTbxThn6Xcs", # https://open.spotify.com/playlist/1h0CEZCm6IbFTbxThn6Xcs?si=eb84a180b61940bd 128
            "37i9dQZF1DXaHEllsiT8lf"  # https://open.spotify.com/playlist/37i9dQZF1DXaHEllsiT8lf?si=4d2de6bac7574da8 95
                                                                                                                   # 516
        ],
        "jazz": [
            "37i9dQZF1DWTR4ZOXTfd9K", # https://open.spotify.com/playlist/37i9dQZF1DWTR4ZOXTfd9K?si=48a1869291e54948 100
            "37i9dQZF1DX1C8KR4UJlnr", # https://open.spotify.com/playlist/37i9dQZF1DX1C8KR4UJlnr?si=e2334a238c0f4557 100
            "37i9dQZF1DX9n1kQRulpEn", # https://open.spotify.com/playlist/37i9dQZF1DX9n1kQRulpEn?si=c3ff641894514280 100
            "37i9dQZF1DWYxwmBaMqxsl", # https://open.spotify.com/playlist/37i9dQZF1DWYxwmBaMqxsl?si=c8716c64f78f45bd 78
            "37i9dQZF1DX2iVTU1bf67i"  # https://open.spotify.com/playlist/37i9dQZF1DX2iVTU1bf67i?si=8ba59c02886449fc 150
                                                                                                                   # 528
          
        ],
        "hiphop": [
            "37i9dQZF1DX7Mq3mO5SSDc", # https://open.spotify.com/playlist/37i9dQZF1DX7Mq3mO5SSDc?si=3ea682942a2a4734 50
            "37i9dQZF1DX186v583rmzp", # https://open.spotify.com/playlist/37i9dQZF1DX186v583rmzp?si=f87582055c5245cf 100
            "5TZkls9cEOzWDR6qCxwDot", # https://open.spotify.com/playlist/5TZkls9cEOzWDR6qCxwDot?si=d3cf9c440f9244fe 168
            "3A46xM92rYMDL7Ohezea0H"  # https://open.spotify.com/playlist/3A46xM92rYMDL7Ohezea0H?si=b543916164544a71 216
                                                                                                                   # 534
        ]
    }

    extract_features_from_multiple_playlists(playlist_dict=playlist)
