from typing import Optional
import datetime

from dotenv import load_dotenv
import spotipy
from spotipy import CacheFileHandler
from spotipy.oauth2 import SpotifyOAuth


load_dotenv()


class PlaylistCreator:
    SCOPES = [
        "playlist-read-private",
        "playlist-read-collaborative",
        "playlist-modify-private",
        "playlist-modify-public",
    ]

    def __init__(self):
        self.sp = None

    def authenticate(self):
        cache_handler = CacheFileHandler()
        auth_manager = SpotifyOAuth(scope=self.SCOPES, cache_handler=cache_handler)
        self.sp = spotipy.Spotify(auth_manager=auth_manager)

    def search_tracks(self, query: str, limit: int = 1, offset: int = 0) -> Optional[dict]:
        results = self.sp.search(query, limit, offset, type="track")
        return results.get("tracks", {}).get("items", [])[0]

    def find_user_playlist(self, name: str) -> Optional[dict]:
        result = None
        limit = 50
        offset = 0
        while True:
            playlists = self.sp.current_user_playlists(limit, offset)

            items = playlists.get("items", [])
            for item in items:
                item_name = item.get("name", "")
                if item_name == name:
                    result = item
                    break

            offset += limit

            # break if there are no more results
            if playlists.get("next") is None:
                break

            # break if a playlist was found
            if result is not None:
                break
        
        return result

    def get_or_create_playlist(self, name: str = "Spotipy tracks"):
        playlist = self.find_user_playlist(name)

        if playlist is None:
            user = self.sp.me()["id"]
            playlist = self.sp.user_playlist_create(user, name, public = False)

        return playlist


if __name__ == "__main__":
    creator = PlaylistCreator()
    creator.authenticate()

    print(creator.get_or_create_playlist())
