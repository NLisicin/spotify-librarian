from dotenv import load_dotenv
from os import getenv
from playlist_config import PlaylistConfig
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables.
load_dotenv()
CLIENT_ID = getenv("CLIENT_ID")
CLIENT_SECRET = getenv("CLIENT_SECRET")
REDIRECT = "http://localhost:8888"
SCOPE= "playlist-modify-public playlist-modify-private user-library-read"

# Connect to Spotify.
sp = Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT, scope=SCOPE))

# Set playlist configurations.
PLAYLIST_CONFIGS = [
    PlaylistConfig(sp, "Low Energy Pop", max_energy=0.5, genres=["pop", "funk", "synth", "indie", "disco", "r&b", "electronica", "soul", "girl group", "game", "multidisciplinary", "twitch"]),
    PlaylistConfig(sp, "High Energy Pop", min_energy=0.5, genres=["pop", "funk", "synth", "indie", "disco", "r&b", "electronica", "soul", "girl group", "game", "multidisciplinary", "twitch"]),
    PlaylistConfig(sp, "Rock & Metal", genres=["rock", "metal", "slayer"]),
    PlaylistConfig(sp, "Acoustic", min_acousticness=0.8),
    PlaylistConfig(sp, "Dance", min_danceability=0.8),
    PlaylistConfig(sp, "Instrumental", min_instrumentalness=0.8),
    PlaylistConfig(sp, "Low Energy", max_energy=0.5),
    PlaylistConfig(sp, "High Energy", min_energy=0.5),
]

# Process tracks incrementally.
user_tracks = sp.current_user_saved_tracks()
i = 1
tracks_not_added = []
print("")
while user_tracks:
    for item in user_tracks["items"]:
        track = item["track"]
        print(f"Processing track {i}...", end="\r")
        i += 1
        added_to_at_least_one = False
        for config in PLAYLIST_CONFIGS:
            was_added = config.add_track(track)
            if was_added:
                added_to_at_least_one = True
        if not added_to_at_least_one:
            tracks_not_added.append(track)
    if user_tracks["next"]:
        user_tracks = sp.next(user_tracks)
    else:
        user_tracks = None
for config in PLAYLIST_CONFIGS:
    config.finish()
print(f"Processing track {i}...\n\nDone 🎉")

# Show tracks that were not added to any playlist.
print("\nNot added:\n")
for track in tracks_not_added:
    track_id = track["id"]
    artist_id = track["artists"][0]["id"]
    artist = sp.artist(artist_id)
    artist_genres = artist["genres"]
    audio_features = sp.audio_features(track_id)[0]
    print(f"{artist['name']} - {track['name']} ({artist_genres})")
