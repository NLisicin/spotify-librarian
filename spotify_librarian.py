from json import dump, load, JSONDecodeError
from os import getenv
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from playlist_config import PlaylistConfig

# Load environment variables.
load_dotenv()
CLIENT_ID = getenv("CLIENT_ID")
CLIENT_SECRET = getenv("CLIENT_SECRET")
REDIRECT = "http://localhost:8888"
SCOPE= "playlist-modify-public playlist-modify-private user-library-read"

# Connect to Spotify.
sp = Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT, scope=SCOPE))
user_tracks = sp.current_user_saved_tracks()

# Set playlist configurations.
POP_GENRES = ["pop", "funk", "synthpop", "indie", "disco", "r&b", "electronica", "soul", "girl group", "game", "multidisciplinary", "twitch"]
NOT_POP_GENRES = ["funk metal", "bow pop"]
ROCK_GENRES = ["rock", "metal", "slayer", "hurdy-gurdy"]

ENERGY_THRESHOLD = 0.7

PLAYLIST_CONFIGS = [
    PlaylistConfig(sp, "Instrumental", min_instrumentalness=0.7),
    PlaylistConfig(sp, "Sleep", max_energy=0.4, min_duration_ms=60000),
    PlaylistConfig(sp, "Dance", min_danceability=0.65, min_energy=ENERGY_THRESHOLD, min_duration_ms=60000,  genres=POP_GENRES, not_genres=NOT_POP_GENRES),
    PlaylistConfig(sp, "Morning", min_acousticness=0.3, max_energy=0.5,  min_duration_ms=60000, not_genres=["classic rock", "dutch metal"]),
    PlaylistConfig(sp, "Rock & Metal", min_duration_ms=60000, genres=ROCK_GENRES),
    PlaylistConfig(sp, "High Energy Pop", min_energy=ENERGY_THRESHOLD, min_duration_ms=60000, genres=POP_GENRES, not_genres=NOT_POP_GENRES),
    PlaylistConfig(sp, "Low Energy Pop", max_energy=ENERGY_THRESHOLD, min_duration_ms=60000, genres=POP_GENRES, not_genres=NOT_POP_GENRES),
    PlaylistConfig(sp, "Pop", genres=POP_GENRES, min_duration_ms=60000, not_genres=NOT_POP_GENRES),
    PlaylistConfig(sp, "High Energy", min_duration_ms=60000, min_energy=ENERGY_THRESHOLD),
    PlaylistConfig(sp, "Low Energy", min_duration_ms=60000, max_energy=ENERGY_THRESHOLD),
]

# Load saved data.
print("\nLoading data...\n")
try:
    with open("audio_features.json", "r") as features_file:
        saved_features = load(features_file)
except (FileNotFoundError, JSONDecodeError):
    saved_features = {}
try:
    with open("artists.json", "r") as artists_file:
        saved_artists = load(artists_file)
except (FileNotFoundError, JSONDecodeError):
    saved_artists = {}

# Process tracks incrementally.
processed_count = 0
tracks_without_audio_features = []
tracks_with_audio_features = []
tracks_not_added = []
new_tracks = []


def download_audio_features():
    new_audio_features = sp.audio_features([track["id"] for track in tracks_without_audio_features])
    for i in range(len(tracks_without_audio_features)):
        new_track = tracks_without_audio_features[i]
        new_track["audio_features"] = new_audio_features[i] if new_audio_features[i] else {}
        new_track["audio_features"]["name"] = new_track["name"]
        tracks_with_audio_features.append(new_track)
        saved_features[new_track["id"]] = new_track["audio_features"]
        new_tracks.append(new_track["name"])
    with open("audio_features.json", "w") as features_file:
        dump(saved_features, features_file)


def add_tracks_to_playlists():
    for track in tracks_with_audio_features:
        added_to_at_least_one = False
        for config in PLAYLIST_CONFIGS:
            was_added = config.check_and_add_track(track)
            if was_added:
                added_to_at_least_one = True
        if not added_to_at_least_one:
            tracks_not_added.append(track["name"])


while user_tracks:
    for item in user_tracks["items"]:
        processed_count += 1
        print(f"Processing track {processed_count}...", end="\r")

        track = item["track"]

        # Check if track needs audio features downloaded.
        try:
            track["audio_features"] = saved_features[track["id"]]
            tracks_with_audio_features.append(track)
        except KeyError:
            tracks_without_audio_features.append(track)
        except Exception as e:
            print(e)
        
        # Check if track needs artist downloaded.
        artist_id = track["artists"][0]["id"]
        try:
            track["artist"] = saved_artists[artist_id]
        except KeyError as e:
            artist = sp.artist(artist_id)
            track["artist"] = artist
            saved_artists[artist_id] = artist
            with open("artists.json", "w") as artists_file:
                dump(saved_artists, artists_file)
        except Exception as e:
            print(e)

        # Download new audio features every 100 tracks.
        if len(tracks_without_audio_features) == 100:
            download_audio_features()
            tracks_without_audio_features = []

        # Add tracks to playlists.
        add_tracks_to_playlists()
        tracks_with_audio_features = []

    if user_tracks["next"]:
        user_tracks = sp.next(user_tracks)
    else:
        # Process remaining tracks and finish.
        download_audio_features()
        add_tracks_to_playlists()
        user_tracks = None

for config in PLAYLIST_CONFIGS:
    config.finish()

print(f"\nDone 🎉\n\nProcessed {processed_count} tracks.")

# Show newly added tracks.
if new_tracks:
    print("\nNew tracks:", end="\n\n  ")
    print("\n  ".join(new_tracks))

# Show tracks that were not added to any playlist.
if tracks_not_added:
    print("\nNew tracks:", end="\n\n  ")
    print("\n  ".join(tracks_not_added))
