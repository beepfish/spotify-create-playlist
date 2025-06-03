from typing import Optional

from dotenv import load_dotenv
from rapidfuzz import process, fuzz
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
        # search for existing playlist first
        playlist = self.find_user_playlist(name)

        # create if not found
        if playlist is None:
            user = self.sp.me()["id"]
            playlist = self.sp.user_playlist_create(user, name, public = False)

        return playlist


def dedupe_tracks(filename: str) -> list[str]:
    """Fuzzily dedupes entries in the given file."""
    with open(filename) as f:
        lines = f.readlines()

    data = [line.strip(' "\n') for line in lines]

    result = []
    for entry in data:
        if len(entry) == 0:
            continue

        # only append entry to results if no similar entry is present
        _, score, _ = process.extractOne(entry, result, scorer=fuzz.token_sort_ratio) or (None, 0, None)
        if score < 90:
            result.append(entry)

    return result


if __name__ == "__main__":
    import sys

    if not len(sys.argv) == 2:
        print(f"Usage: {sys.argv[0]} <tracklist>")
        sys.exit(1)

    # load file list
    filename = sys.argv[1]
    tracks = dedupe_tracks(filename)

    # init spotipy
    creator = PlaylistCreator()
    creator.authenticate()
    playlist = creator.get_or_create_playlist()
