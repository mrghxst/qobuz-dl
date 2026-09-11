<div align="center">

# qobuz-dl

**Search, explore and download lossless and hi-res music from [Qobuz](https://www.qobuz.com/), right from your terminal.**

[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-3776AB.svg?logo=python&logoColor=white)](pyproject.toml)
[![Managed with uv](https://img.shields.io/badge/managed%20with-uv-DE5FE9.svg)](https://docs.astral.sh/uv/)
[![Fork of vitiko98/qobuz-dl](https://img.shields.io/badge/fork%20of-vitiko98%2Fqobuz--dl-lightgrey.svg?logo=github)](https://github.com/vitiko98/qobuz-dl)

</div>

> [!NOTE]
> This is a fork of [vitiko98/qobuz-dl](https://github.com/vitiko98/qobuz-dl), the original project by Vitiko,
> building on the [darocaecobr/qobuz-dl](https://github.com/darocaecobr/qobuz-dl) fork. Everything the original
> does still works; this fork adds browser login, local transcoding and verified, upload-ready files.
> See [Credits](#credits).

> [!IMPORTANT]
> You need an **active Qobuz subscription**. qobuz-dl downloads what your account has access to.

---

## ✨ What this fork adds

| | Feature | What it does |
|---|---|---|
| 🔐 | **Browser login** | `qobuz-dl oauth` signs you in through your browser, since Qobuz dropped email/password login. |
| 🎚️ | **Low-bitrate MP3** | Qualities `1`–`4` convert the 320 kbps MP3 locally with ffmpeg (32–192 kbps). |
| 🏷️ | **Release identity tags** | Every FLAC gets the Qobuz album `URL`, its `UPC` and each track's `ISRC`, so tagging and upload tools (e.g. [smoked-salmon](https://github.com/smokin-salmon/smoked-salmon)) open the exact release instead of guessing by name. |
| ✅ | **Verified downloads** | Each FLAC is fully decoded with `flac`. The MD5 checksum Qobuz leaves empty is filled in; only the checksum is written, the audio stays byte-for-byte as downloaded. A broken download is never given its final name. |
| 🧩 | **Completeness check** | An album with a missing, preview-only or failed track is reported as **INCOMPLETE** and kept out of the database, so running the same download again fetches what is missing. |
| 📐 | **Honest folder labels** | Albums that mix resolutions are named after all of them, e.g. `[24B-44.1+48kHz]`, not after their first track. |

## 🎧 Features

- Download **FLAC** (up to 24 bit / 192 kHz) and **MP3** from Qobuz
- **Download** mode for albums, tracks, artists, playlists and labels, by URL or from a text file of URLs
- **Interactive** mode to search and queue releases, and **lucky** mode to grab the first results
- **Last.fm playlists**, which also covers Spotify, Apple Music and YouTube playlists imported into Last.fm
- Multi-disc albums, M3U playlists, cover art and booklets
- Duplicate handling with its own portable database
- Extended tags, customizable folder and file names

## 📦 Installation

With [uv](https://docs.astral.sh/uv/) (recommended):

```sh
uv tool install git+https://github.com/mrghxst/qobuz-dl
```

To update later, run the same command with `--reinstall`. With [pipx](https://pipx.pypa.io/): `pipx install git+https://github.com/mrghxst/qobuz-dl`.

> [!TIP]
> `pip install qobuz-dl` installs the original upstream release from PyPI, **not** this fork.

### Optional tools

| Tool | Needed for | Windows | macOS | Debian / Ubuntu |
|---|---|---|---|---|
| [`flac`](https://xiph.org/flac/) | download verification and MD5 checksums | `winget install Xiph.FLAC` | `brew install flac` | `sudo apt install flac` |
| [`ffmpeg`](https://ffmpeg.org/) | qualities `1`–`4` | `winget install Gyan.FFmpeg` | `brew install ffmpeg` | `sudo apt install ffmpeg` |

Without `flac`, downloads still work, but files are not verified and qobuz-dl warns that no MD5 was stored.

## 🚀 First run

```sh
qobuz-dl -r       # create the config file
qobuz-dl oauth    # log in through your browser
```

`qobuz-dl oauth` opens a Qobuz login page. After you sign in, qobuz-dl captures the login locally and stores your
auth token in `config.ini`:

- **Windows:** `%APPDATA%\qobuz-dl\config.ini`
- **Linux / macOS:** `~/.config/qobuz-dl/config.ini`

The token is refreshed and saved back on every run. If it ever expires, run `qobuz-dl oauth` again.

<details>
<summary>Log in with a token instead</summary>

You can paste a `user_auth_token` manually as the `password` value in `config.ini`. Grab it from your browser:
DevTools → Network → look for `user_auth_token` in any Qobuz API response.

</details>

## 🎚️ Quality

Pick the quality with `-q` (or set `default_quality` in your config):

| `-q` | Format |
|---|---|
| `1` | MP3 32 kbps (converted locally from 320 kbps, needs ffmpeg) |
| `2` | MP3 64 kbps (converted locally from 320 kbps, needs ffmpeg) |
| `3` | MP3 128 kbps (converted locally from 320 kbps, needs ffmpeg) |
| `4` | MP3 192 kbps (converted locally from 320 kbps, needs ffmpeg) |
| `5` | MP3 320 kbps |
| `6` | FLAC 16 bit / 44.1 kHz (CD quality) |
| `7` | FLAC 24 bit, up to 96 kHz |
| `27` | FLAC 24 bit, up to 192 kHz (best available) |

When a release is not available in the chosen quality, qobuz-dl falls back to the best one it has.
Use `--no-fallback` to skip such releases instead.

## 📖 Usage

### Download mode

```sh
# an album in 24 bit / up to 96 kHz
qobuz-dl dl https://play.qobuz.com/album/qxjbxh1dc3xyb -q 7

# several URLs into a custom directory
qobuz-dl dl https://play.qobuz.com/artist/2038380 https://play.qobuz.com/album/ip8qjy1m6dakc -d "Some pop from 2020"

# every URL listed in a text file
qobuz-dl dl this_txt_file_has_urls.txt

# a label's albums, with cover art embedded in the files
qobuz-dl dl https://play.qobuz.com/label/7526 --embed-art

# a Qobuz playlist in the best quality
qobuz-dl dl https://play.qobuz.com/playlist/5388296 -q 27

# an artist's albums, without singles, EPs and VA releases
qobuz-dl dl https://play.qobuz.com/artist/2528676 --albums-only

# MP3s into the current folder: no database, no cover, no .m3u
qdl dl --no-db -q 5 --no-cover --no-m3u -ff "." -tf "{artist}-{tracktitle}"

# 128 kbps MP3, converted locally with ffmpeg
qobuz-dl dl https://play.qobuz.com/album/qxjbxh1dc3xyb -q 3
```

**Last.fm playlists.** Last.fm can build playlists from what you listen to, or import them from Spotify, Apple Music
and YouTube. Find yours at `https://www.last.fm/user/<your profile>/playlists`, then:

```sh
qobuz-dl dl https://www.last.fm/user/vitiko98/playlists/11887574 -q 27
```

Run `qobuz-dl dl --help` for every option.

### Interactive mode

```sh
qobuz-dl fun -l 10    # search with a limit of 10 results
```

```
Logging...
Logged: OK
Membership: Studio

Enter your search: [Ctrl + c to quit]
- fka twigs magdalene
```

qobuz-dl lists the matching releases; pick the ones you want and it takes care of the rest.
Run `qobuz-dl fun --help` for more.

### Lucky mode

```sh
qobuz-dl lucky playboi carti die lit                           # first album result
qobuz-dl lucky joy division -n 5 --type artist                 # first 5 artist results
qobuz-dl lucky eric dolphy remastered --type track -n 3 -q 5   # first 3 tracks as MP3 320
qobuz-dl lucky jay z story of oj --type track --no-cover       # first track, no cover art
```

Run `qobuz-dl lucky --help` for more.

## 🗂️ Files, tags and checks

### Folder and file names

Set them with `-ff` / `-tf` or `folder_format` / `track_format` in your config. Available keys: `artist`,
`albumartist`, `album`, `year`, `bit_depth`, `sampling_rate`, `tracktitle`, `version`, `tracknumber`.

The default folder format `{artist} - {album} ({year}) [{bit_depth}B-{sampling_rate}kHz]` gives:

```
Khalil Chahine - Le Dé (2024) [24B-48kHz]
Some Artist - Some Album (2021) [24B-44.1+48kHz]    ← tracks at two sampling rates
```

### Tags

| Tag | Value |
|---|---|
| `TITLE` | track title, with its version (e.g. `Title (Live)`) |
| `ARTIST` / `ALBUMARTIST` | track performer / album artist |
| `ALBUM`, `DATE` | album title, original release date |
| `TRACKNUMBER`, `TRACKTOTAL`, `DISCNUMBER` | position (disc number on multi-disc albums) |
| `COMPOSER`, `GENRE` | as listed on Qobuz |
| `LABEL`, `COPYRIGHT` | as listed on Qobuz (`n/a` when missing) |
| `URL`, `UPC`, `ISRC` | Qobuz album page, album barcode, track ISRC (FLAC only) |

### Download checks (FLAC)

Every track is decoded with `flac` while it is tagged. At the end of each album qobuz-dl says whether the folder is
complete:

```
Completed: all 7 tracks downloaded and verified
INCOMPLETE, do not upload: only 6 of 7 tracks. Run the same download again to fetch what is missing.
```

A track that fails verification keeps its temporary `.NN.tmp` name, so it is never mistaken for a finished file.

### Database

qobuz-dl skips release IDs it has already downloaded, with the message
`This release ID ({item_id}) was already downloaded`. Add `--no-db` to bypass the check, or run `qobuz-dl -p` to
reset the database (e.g. after losing your collection). Incomplete albums are not recorded, so they can be retried.

## 🧰 Command reference

<details>
<summary><code>qobuz-dl --help</code></summary>

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

</details>

## 🐍 Module usage

Everything you need is `QobuzDL` from `core`:

```python
import logging
from qobuz_dl.core import QobuzDL

logging.basicConfig(level=logging.INFO)

# 'token' must be a valid user_auth_token. Get one with `qobuz-dl oauth`
# (it is then stored in config.ini).
email = "your@email.com"
token = "user_auth_token_from_qobuz-dl_oauth"

qobuz = QobuzDL()
qobuz.get_tokens()  # get 'app_id' and 'secrets' attrs
qobuz.initialize_client(email, token, qobuz.app_id, qobuz.secrets)

qobuz.handle_url("https://play.qobuz.com/album/va4j3hdlwaubc")
```

## 🛠️ Development

The project uses [uv](https://docs.astral.sh/uv/) for dependencies and virtual environments.

```sh
uv sync                      # set up the environment with the dev tools
uv run qobuz-dl --help       # run the CLI from the checkout
uv run qobuz-dl dl https://play.qobuz.com/album/0886443927087
uv run flake8 qobuz_dl/      # lint
uv tool install .            # install this checkout as your qobuz-dl
```

Or call it as a module:

```sh
uv run python -c "from qobuz_dl.cli import main; main()" dl https://play.qobuz.com/track/8767428
```

## 🙏 Credits

- **[Vitiko (vitiko98)](https://github.com/vitiko98)** created qobuz-dl in 2020 and maintains the original,
  [vitiko98/qobuz-dl](https://github.com/vitiko98/qobuz-dl). Everything here builds on that work. If qobuz-dl is
  useful to you, consider [supporting the original author](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=VZWSWVGZGJRMU&source=url).
- **Upstream contributors**, including nathannathant, François Charette, Georg Perhofer, TheDen and
  [everyone else](https://github.com/vitiko98/qobuz-dl/graphs/contributors) who sent patches to the original.
- **Sorrow446 and DashLt**: the `qopy` and `spoofer` modules come from their Qo-DL-Reborn, the discontinued project
  that inspired qobuz-dl.
- **[darocaecobr/qobuz-dl](https://github.com/darocaecobr/qobuz-dl)**: browser (OAuth) login, the uv development
  setup and ffmpeg transcoding for low bitrates.
- **[mrghxst/qobuz-dl](https://github.com/mrghxst/qobuz-dl)** (this fork): the OAuth callback fix, release identity
  tags, verified downloads with MD5 checksums, the completeness check and mixed-resolution folder labels.

Licensed under the [GNU General Public License v3.0](LICENSE), like the original.

## ⚠️ Disclaimer

- This tool was written for educational purposes. Its authors are not responsible for bad-faith use. By using it,
  you accept the [Qobuz API Terms of Use](https://static.qobuz.com/apps/api/QobuzAPI-TermsofUse.pdf).
- qobuz-dl is not affiliated with Qobuz.
