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
        tracks = results.get("tracks", {}).get("items", [])

        if len(tracks) > 0:
            return tracks[0]

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

    def find_playlist_tracks(self, playlist_id: str) -> dict[str, bool]:
        track_uris = {}
        limit = 100
        offset = 0
        while True:
            playlist_tracks = self.sp.playlist_tracks(playlist_id, limit=limit, offset=offset)

            tracks = playlist_tracks.get("items", [])
            for track in tracks:
                uri = track.get("track", {}).get("uri")
                if uri is not None:
                    track_uris[uri] = True

            offset += limit

            # break if there are no more results
            if playlist_tracks.get("next") is None:
                break

        return track_uris

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

    # load track list
    filename = sys.argv[1]
    tracks = dedupe_tracks(filename)
    num_tracks = len(tracks)

    # init spotipy
    creator = PlaylistCreator()
    creator.authenticate()
    playlist = creator.get_or_create_playlist()
    playlist_id = playlist["id"]
    playlist_tracks = creator.find_playlist_tracks(playlist_id)

    # search tracks and add to playlist
    track_uris = []
    for i, track in enumerate(tracks):
        print(f"[{i + 1} of {num_tracks}] {track} -- ", end="")

        result = creator.search_tracks(track)
        if result is None:
            print("TRACK NOT FOUND")
            continue

        uri = result.get("uri")
        if uri is None:
            print("TRACK HAS NO URI")
            continue

        exists = playlist_tracks.get(uri)
        if exists:
            print("ALREADY ON PLAYLIST")
        else:
            print("ADDED")
            track_uris.append(uri)

    if len(track_uris) > 0:
        print(f"Adding {len(track_uris)} track(s) to playlist")
        creator.sp.playlist_add_items(playlist_id, track_uris)
