# spotify-create-playlist
Automatically create a Spotify playlist for a list of tracks

Could use some error handling and/or tests.

## Install
Use `poetry` for installation:
```console
poetry install
```

## Setup
You need to register a Spotify developer project to get a `CLIENT_ID` and `CLIENT_SECRET`. Then copy the example ENV file and fill it out:
```console
cp example.env .env
```

## Track list
The track list is a text file with one line per track. For best results, the track metadata should be formatted like this:
```text
<track_title> <artist_name>
```

## Running
Run the script with `poetry`:
```console
poetry run playlist_creator <tracklist>
```

You can also specify the name of the target playlist with the `--playlist_name` option. The default name is `Spotipy Playlist`. If a playlist with the given name already exists, it will be used; otherwise a new playlist will be created.
