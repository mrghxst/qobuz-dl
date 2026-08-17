# qobuz-dl
Search, explore and download Lossless and Hi-Res music from [Qobuz](https://www.qobuz.com/). It *just works*™ (2025).
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=VZWSWVGZGJRMU&source=url)

## Features

* Download FLAC and MP3 files from Qobuz
* Explore and download music directly from your terminal with **interactive** or **lucky** mode
* Download albums, tracks, artists, playlists and labels with **download** mode
* Download music from last.fm playlists (Spotify, Apple Music and Youtube playlists are also supported through this method)
* Queue support on **interactive** mode
* Effective duplicate handling with own portable database
* Support for albums with multiple discs
* Support for M3U playlists
* Downloads URLs from text file
* Extended tags
* And more

## Getting started

> You'll need an **active subscription**

#### Install qobuz-dl with pip
##### Linux / MAC OS
```
pip3 install --upgrade qobuz-dl
```
##### Windows
```
pip3 install windows-curses
pip3 install --upgrade qobuz-dl
```

#### First run: configure and log in

Qobuz no longer supports email/password login. Run `qobuz-dl -r` to set up
your config file, then log in through your browser with:

```
qobuz-dl oauth
```

This opens a Qobuz login URL in your browser (you'll need an active
subscription). After you sign in, qobuz-dl captures the login locally,
stores your auth token in `config.ini` and is ready to use.

> The token is automatically refreshed and saved back to your config on
> every run. If it ever expires, just run `qobuz-dl oauth` again.

## Quality options

Choose the download quality with the `-q` flag (or set it in your config):

| Quality | Description |
|---------|-------------|
| `1` | FFmpeg 32kbps (transcoded from 320kbps MP3) |
| `2` | FFmpeg 64kbps (transcoded from 320kbps MP3) |
| `3` | FFmpeg 128kbps (transcoded from 320kbps MP3) |
| `4` | FFmpeg 192kbps (transcoded from 320kbps MP3) |
| `5` | MP3 320kbps |
| `6` | Lossless 16 bit, 44.1kHz |
| `7` | Hi-Res 24 bit, <96kHz |
| `27` | Hi-Res 24 bit, >96kHz |

Qualities `1`-`4` download the 320kbps MP3 and convert it locally to the
target bitrate, which requires [`ffmpeg`](https://ffmpeg.org/) to be
installed and available on your `PATH`. Example:

```
qobuz-dl dl https://play.qobuz.com/album/qxjbxh1dc3xyb -q 3
```

## Examples

### Download mode
Download URL in 24B<96khz quality
```
qobuz-dl dl https://play.qobuz.com/album/qxjbxh1dc3xyb -q 7
```
Download multiple URLs to custom directory
```
qobuz-dl dl https://play.qobuz.com/artist/2038380 https://play.qobuz.com/album/ip8qjy1m6dakc -d "Some pop from 2020"
```
Download multiple URLs from text file
```
qobuz-dl dl this_txt_file_has_urls.txt
```
Download albums from a label and also embed cover art images into the downloaded files
```
qobuz-dl dl https://play.qobuz.com/label/7526 --embed-art
```
Download a Qobuz playlist in maximum quality
```
qobuz-dl dl https://play.qobuz.com/playlist/5388296 -q 27
```
Download all the music from an artist except singles, EPs and VA releases
```
qobuz-dl dl https://play.qobuz.com/artist/2528676 --albums-only
```
Download all the music to only playlist folder, no database, no cover in mp3 format
```bash
qdl dl --no-db -q 5 --no-cover --no-m3u -ff "." -tf "{artist}-{tracktitle}"
```

#### Last.fm playlists
> Last.fm has a new feature for creating playlists: you can create your own based on the music you listen to or you can import one from popular streaming services like Spotify, Apple Music and Youtube. Visit: `https://www.last.fm/user/<your profile>/playlists` (e.g. https://www.last.fm/user/vitiko98/playlists) to get started.

Download a last.fm playlist in the maximum quality
```
qobuz-dl dl https://www.last.fm/user/vitiko98/playlists/11887574 -q 27
```

Run `qobuz-dl dl --help` for more info.

### Interactive mode
Run interactive mode with a limit of 10 results
```
qobuz-dl fun -l 10
```
Type your search query
```
Logging...
Logged: OK
Membership: Studio


Enter your search: [Ctrl + c to quit]
- fka twigs magdalene
```
`qobuz-dl` will bring up a nice list of releases. Now choose whatever releases you want to download (everything else is interactive).

Run `qobuz-dl fun --help` for more info.

### Lucky mode
Download the first album result
```
qobuz-dl lucky playboi carti die lit
```
Download the first 5 artist results
```
qobuz-dl lucky joy division -n 5 --type artist
```
Download the first 3 track results in 320 quality
```
qobuz-dl lucky eric dolphy remastered --type track -n 3 -q 5
```
Download the first track result without cover art
```
qobuz-dl lucky jay z story of oj --type track --no-cover
```

Run `qobuz-dl lucky --help` for more info.

### Other
Reset your config file
```
qobuz-dl -r
```

Log in / refresh your Qobuz auth token through the browser
```
qobuz-dl oauth
```

> `qobuz-dl oauth` is required after running `qobuz-dl -r`, or whenever
> your token expires. Email/password login is no longer supported by Qobuz.
> You can also paste a `user_auth_token` manually (grab it from your browser:
> DevTools → Network → look for `user_auth_token` in any Qobuz API response)
> as the `password` value in `~/.config/qobuz-dl/config.ini`.

By default, `qobuz-dl` will skip already downloaded items by ID with the message `This release ID ({item_id}) was already downloaded`. To avoid this check, add the flag `--no-db` at the end of a command. In extreme cases (e.g. lost collection), you can run `qobuz-dl -p` to completely reset the database.

## Usage
```
usage: qobuz-dl [-h] [-r] [-p] [-sc] {fun,dl,lucky,oauth} ...

The ultimate Qobuz music downloader.
See usage examples on https://github.com/vitiko98/qobuz-dl

options:
  -h, --help      show this help message and exit
  -r, --reset     create/reset config file
  -p, --purge     purge/delete downloaded-IDs database
  -sc, --show-config
                  show configuration

commands:
  run qobuz-dl <command> --help for more info
  (e.g. qobuz-dl fun --help)

  {fun,dl,lucky,oauth}
    fun           interactive mode
    dl            input mode
    lucky         lucky mode
    oauth         browser-based login
```

## Module usage 
Using `qobuz-dl` as a module is really easy. Basically, the only thing you need is `QobuzDL` from `core`.

```python
import logging
from qobuz_dl.core import QobuzDL

logging.basicConfig(level=logging.INFO)

# 'password' must be a valid user_auth_token. Get one with:
#   qobuz-dl oauth   (then it's stored in config.ini)
email = "your@email.com"
token = "user_auth_token_from_qobuz-dl_oauth"

qobuz = QobuzDL()
qobuz.get_tokens()  # get 'app_id' and 'secrets' attrs
qobuz.initialize_client(email, token, qobuz.app_id, qobuz.secrets)

qobuz.handle_url("https://play.qobuz.com/album/va4j3hdlwaubc")
```

Attributes, methods and parameters have been named as self-explanatory as possible.

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency and
virtual environment management (Python 3.12+).

Set up the environment and install the package (editable) plus the dev tools:

```
uv sync

# to install this version
 uv tool install .
```

Run the CLI in development mode:

```
uv run qobuz-dl --help
uv run qobuz-dl oauth
uv run qobuz-dl dl https://play.qobuz.com/album/0886443927087
```

Or invoke it as a module:

```
uv run python -c "from qobuz_dl.cli import main; main()" dl https://play.qobuz.com/track/8767428
```

Lint with flake8:

```
uv run flake8 qobuz_dl/
```

## A note about Qo-DL
`qobuz-dl` is inspired in the discontinued Qo-DL-Reborn. This tool uses two modules from Qo-DL: `qopy` and `spoofer`, both written by Sorrow446 and DashLt.
## Disclaimer
* This tool was written for educational purposes. I will not be responsible if you use this program in bad faith. By using it, you are accepting the [Qobuz API Terms of Use](https://static.qobuz.com/apps/api/QobuzAPI-TermsofUse.pdf).
* `qobuz-dl` is not affiliated with Qobuz
