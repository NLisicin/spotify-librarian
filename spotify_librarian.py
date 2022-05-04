from dotenv import load_dotenv
from os import getenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables.
load_dotenv()
CLIENT_ID = getenv("CLIENT_ID")
CLIENT_SECRET = getenv("CLIENT_SECRET")
REDIRECT = getenv("REDIRECT")
SCOPE = getenv("SCOPE")

# Connect to Spotify.
sp = Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT, scope=SCOPE))


class PlaylistConfig():
    def __init__(self, 
        name: str, 
        min_tempo: int=None, 
        max_tempo: int=None, 
        min_acousticness: float=None, 
        max_acousticness: float=None, 
        min_danceability: float=None, 
        max_danceability: float=None, 
        min_energy: float=None, 
        max_energy: float=None, 
        min_instrumentalness: float=None, 
        max_instrumentalness: float=None, 
        genres: list=None
    ) -> None:
        name = f"[SL] {name}"
        print(f"Initializing playlist {name}")
        self.min_tempo = min_tempo
        self.max_tempo = max_tempo
        self.genres = genres
        self.min_acousticness = min_acousticness
        self.max_acousticness = max_acousticness
        self.min_danceability = min_danceability
        self.max_danceability = max_danceability
        self.min_energy = min_energy
        self.max_energy = max_energy
        self.min_instrumentalness = min_instrumentalness
        self.max_instrumentalness = max_instrumentalness
        self.playlist_id = self.create_playlist(name)
    

    def create_playlist(self, name: str) -> str:
        # Unfollow (delete) an existing playlist.
        user_playlists = sp.current_user_playlists()
        while user_playlists:
            for playlist in user_playlists["items"]:
                if playlist["name"] == name:
                    sp.current_user_unfollow_playlist(playlist["id"])
            if user_playlists["next"]:
                user_playlists = sp.next(user_playlists)
            else:
                user_playlists = None

        # Create a new playlist.
        current_user_id = sp.current_user()["id"]
        playlist_id = sp.user_playlist_create(current_user_id, name)["id"]
        return playlist_id


    def check_track(self, track: dict) -> bool:
        track_id = track["id"]
        artist_id = track["artists"][0]["id"]
        artist = sp.artist(artist_id)
        artist_genres = artist["genres"]
        audio_features = sp.audio_features(track_id)[0]
        
        if self.min_tempo:
            if audio_features["tempo"] < self.min_tempo:
                return False
        if self.max_tempo:
            if audio_features["tempo"] > self.max_tempo:
                return False  

        if self.min_acousticness:
            if audio_features["acousticness"] < self.min_acousticness:
                return False  
        if self.max_acousticness:
            if audio_features["acousticness"] > self.max_acousticness:
                return False

        if self.min_danceability:
            if audio_features["danceability"] < self.min_danceability:
                return False  
        if self.max_danceability:
            if audio_features["danceability"] > self.max_danceability:
                return False

        if self.min_energy:
            if audio_features["energy"] < self.min_energy:
                return False  
        if self.max_energy:
            if audio_features["energy"] > self.max_energy:
                return False

        if self.min_instrumentalness:
            if audio_features["instrumentalness"] < self.min_instrumentalness:
                return False  
        if self.max_instrumentalness:
            if audio_features["instrumentalness"] > self.max_instrumentalness:
                return False  

        if self.genres:
            for artist_genre in artist_genres:
                for genre in self.genres:
                    if genre in artist_genre:
                        return True
            return False
        
        return True

    def add_track(self, track: dict) -> bool:
        if self.check_track(track):
            sp.playlist_add_items(self.playlist_id, [track["id"]])
            return True
        else:
            return False


PLAYLIST_CONFIGS = [
    PlaylistConfig("Chill Pop", max_tempo=90, genres=["pop", "funk", "synth", "indie", "disco", "r&b", "electronica", "soul", "girl group", "game", "multidisciplinary", "twitch"]),
    PlaylistConfig("High Energy Pop", min_tempo=90, genres=["pop", "funk", "synth", "indie", "disco", "r&b", "electronica", "soul", "girl group", "game", "multidisciplinary", "twitch"]),
    PlaylistConfig("Rock & Metal", genres=["rock", "metal", "slayer"]),
    PlaylistConfig("Acoustic", min_acousticness=0.5),
    PlaylistConfig("Instrumental", min_instrumentalness=0.5),
    PlaylistConfig("Dance", min_danceability=0.5),
    PlaylistConfig("Low Energy", max_energy=0.5),
    PlaylistConfig("High Energy", min_energy=0.5),
]

# Process tracks incrementally.
user_tracks = sp.current_user_saved_tracks(offset=3000)
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
print(f"Processing track {i}...\n\nDone 🎉")

print("\nNot added:\n")
for track in tracks_not_added:
    track_id = track["id"]
    artist_id = track["artists"][0]["id"]
    artist = sp.artist(artist_id)
    artist_genres = artist["genres"]
    audio_features = sp.audio_features(track_id)[0]
    print(f"{artist['name']} - {track['name']} ({artist_genres})")
