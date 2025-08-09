# Simple Video Mixer
A very simple command line tool to mix a video source with one or more audio sources. It uses ffmpeg for high-quality audio/video processing and mixing.


## Features
- Mix a video file (mp4) with one or more audio files (mp3 or other ffmpeg-supported formats).
- Set the volume for the video audio track and for each audio file individually.
- Set a delay (in milliseconds) for each audio file, specifying when it should start in the video.
- Supports flexible and compact command line syntax:
  - `-v video.mp4[:volume]` — specify video file and optional volume (e.g. `video.mp4:0.8` for 80% volume)
  - `-a audio1.mp3[:volume[:delay]] audio2.mp3[:volume[:delay]] ...` — specify one or more audio files, each with optional volume and delay (e.g. `audio1.mp3:0.5:2000`)
  - `-o output.mp4` — specify output file (default: input video filename with `-mixed` before the extension)
  - `--verbose` — print the ffmpeg command before running it
  - `--dry-run` — print the ffmpeg command and exit without executing it
  - See `--help` for more information


## Installation
1. Install Python (3.8 or higher)
2. Install [ffmpeg](https://ffmpeg.org/download.html) (must be available in your system PATH)
3. Clone this repository
6. Run `python src/main.py` with the arguments

## Requirements
- Python 3.8 or higher
- ffmpeg installed and available in your system PATH

## Contribution
Feel free to contribute via pull requests.

## License
The project is licensed by the [Apache 2 license](LICENSE).