from spotipy import Spotify

class PlaylistConfig():
    def __init__(self, 
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
                }
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
        artist_id = track["artists"][0]["id"]
        artist = self.sp.artist(artist_id)
        artist_genres = artist["genres"]
        
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

    def check_and_add_track(self, track: dict) -> bool:
        try:
            if self.check_track(track):
                self.tracks_to_add.append(track["id"])
                if len(self.tracks_to_add) == 100:
                    print(f"Adding 100 tracks to {self.name}")
                    self.sp.playlist_add_items(self.playlist_id, self.tracks_to_add)
                    self.tracks_to_add = []
                return True
            else:
                return False
        except Exception as e:
            print(e)
            print("Track:")
            print(track)
            return False
    
    def finish(self):
        print(f"Adding {len(self.tracks_to_add)} tracks to {self.name}")
        self.sp.playlist_add_items(self.playlist_id, self.tracks_to_add)