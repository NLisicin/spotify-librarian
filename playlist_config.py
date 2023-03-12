from spotipy import Spotify

class PlaylistConfig():
    def __init__(
        self,
        spotipy_client: Spotify,
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
        min_loudness: float=None,
        max_loudness: float=None,
        min_valence: float=None,
        max_valence: float=None,
        min_mode: int=None,
        max_mode: int=None,
        min_duration_ms: int=None,
        max_duration_ms: int=None,
        genres: list=[],
        not_genres: list=[]
    ):
        self.sp = spotipy_client
        self.name = f"[SL] {name}"
        print(f"Initializing playlist {self.name}")
        self.config = {
            "features": {
                "tempo": {
                    "min": min_tempo,
                    "max": max_tempo
                },
                "acousticness": {
                    "min": min_acousticness,
                    "max": max_acousticness
                },
                "danceability": {
                    "min": min_danceability,
                    "max": max_danceability
                },
                "energy": {
                    "min": min_energy,
                    "max": max_energy
                },
                "instrumentalness": {
                    "min": min_instrumentalness,
                    "max": max_instrumentalness
                },
                "loudness": {
                    "min": min_loudness,
                    "max": max_loudness
                },
                "valence": {
                    "min": min_valence,
                    "max": max_valence
                },
                "mode": {
                    "min": min_mode,
                    "max": max_mode
                },
                "duration_ms": {
                    "min": min_duration_ms,
                    "max": max_duration_ms
                },
            },
            "genres": genres,
            "not_genres": not_genres
        }
        self.playlist_id = self.create_playlist(self.name)
        self.tracks_to_add = []
    

    def create_playlist(self, name: str) -> str:
        # Unfollow (delete) an existing playlist.
        user_playlists = self.sp.current_user_playlists()
        while user_playlists:
            for playlist in user_playlists["items"]:
                if playlist["name"] == name:
                    self.sp.current_user_unfollow_playlist(playlist["id"])
            if user_playlists["next"]:
                user_playlists = self.sp.next(user_playlists)
            else:
                user_playlists = None

        # Create a new playlist.
        current_user_id = self.sp.current_user()["id"]
        playlist_id = self.sp.user_playlist_create(current_user_id, name)["id"]
        return playlist_id


    def check_track(self, track: dict) -> bool:
        audio_features = track["audio_features"]
        
        # Check feature config.
        for feature_name, thresholds in self.config["features"].items():
            if feature_name in audio_features:
                if thresholds["min"] is not None:
                    if audio_features[feature_name] < thresholds["min"]:
                        return False
                if thresholds["max"] is not None:
                    if audio_features[feature_name] > thresholds["max"]:
                        return False
        
        # Check genre config.
        for not_genre in self.config["not_genres"]:
            for artist_genre in track["artist"]["genres"]:
                if not_genre in artist_genre:
                    return False
        if self.config["genres"]:
            for genre in self.config["genres"]:
                for artist_genre in track["artist"]["genres"]:
                    if genre in artist_genre:
                        return True
            return False
        
        return True


    def check_and_add_track(self, track: dict) -> bool:
        if self.check_track(track):
            self.tracks_to_add.append(track["id"])
            if len(self.tracks_to_add) == 100:
                self.sp.playlist_add_items(self.playlist_id, self.tracks_to_add)
                self.tracks_to_add = []
            return True
        else:
            return False
    
    
    def finish(self):
        print(f"Finishing {self.name}")
        self.sp.playlist_add_items(self.playlist_id, self.tracks_to_add)
