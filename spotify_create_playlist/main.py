from dotenv import load_dotenv
import spotipy
from spotipy import CacheFileHandler
from spotipy.oauth2 import SpotifyOAuth


load_dotenv()


def authenticate() -> spotipy.Spotipy:
    scope = "user-library-read"

    cache_handler = CacheFileHandler()
    auth_manager = SpotifyOAuth(scope=scope, cache_handler=cache_handler)
    return spotipy.Spotify(auth_manager=auth_manager)


