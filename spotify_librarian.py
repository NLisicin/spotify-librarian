from dotenv import load_dotenv
from os import getenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from numpy import percentile


def get_all_items(callback: list, mode: str):
    items = {}
    print(f"Getting {mode}..", end="")
    while callback:
        print(".", end="")
        for item in callback["items"]:
            if mode == "tracks":
                item = item["track"]
                artist = sp.artist(item["artists"][0]["id"])
                items[item["id"]] = {
                    "name": item["name"], 
                    "artist_name": item["artists"][0]["name"],
                    "genres": artist["genres"],
                    }
            elif mode == "playlists":
                items[item["id"]] = {"name": item["name"]}
        if callback["next"]:
            callback = sp.next(callback)
        else:
            callback = None
    print("\n")
    return items


# Load environment variables.
load_dotenv()
CLIENT_ID = getenv("CLIENT_ID")
CLIENT_SECRET = getenv("CLIENT_SECRET")
REDIRECT = getenv("REDIRECT")
SCOPE = getenv("SCOPE")

# Connect to Spotify.
sp = Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT, scope=SCOPE))

# Get saved tracks and playlists.
user_tracks_callback = sp.current_user_saved_tracks()
user_tracks = get_all_items(user_tracks_callback, "tracks")

user_playlists_callback = sp.current_user_playlists()
user_playlists = get_all_items(user_playlists_callback, "playlists")

# Get audio features of saved tracks.
FEATURES_TO_GET = ["danceability", "energy", "acousticness", "instrumentalness", "tempo"]
user_track_ids = list(user_tracks.keys())
print("Getting audio features..", end="")
for i in range(0, len(user_track_ids), 100):
    print(".", end="")
    audio_features = sp.audio_features(user_track_ids[i:i+100])
    for feature in audio_features:
        user_tracks[feature["id"]]["audio_features"] = {k: v for k, v in feature.items() if k in FEATURES_TO_GET}
print("\n")
