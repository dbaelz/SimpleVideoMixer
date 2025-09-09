import argparse
import os
import logging
import sys
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)

from audio_models import AudioTrack

PROGRAM_NAME = "Simple Video Mixer"
VERSION = "0.0.1"

_REPEAT_MODE_INF = "inf"

def parse_args() -> tuple[str, float, list[AudioTrack], str, bool, bool]:
    parser = argparse.ArgumentParser(description="Mix video and audio sources", add_help=True)
    parser.add_argument("--version", action="version", version=f"{PROGRAM_NAME} - version {VERSION}")

    parser.add_argument(
        "-v",
        "--video",
        required=True,
        help="Input video file, optionally with volume as file:volume (e.g. video.mp4:0.8). Volume is optional, default 1.0."
    )

    parser.add_argument(
        "-a",
        "--audio",
        action='append',
        default=[],
        help="Audio file(s) to mix, format: file[:volume[:delay]]. You can specify multiple --audio flags. Volume and delay are optional, default 1.0 and 0."
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file (default: input video filename with '-mixed' before extension)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print the ffmpeg command before running it."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the ffmpeg command and exit without executing it."
    )

    args = parser.parse_args()

    # Parse video argument (file[:volume])
    video_parts = args.video.split(":")
    video_file = video_parts[0]
    video_volume, _ = parse_volume_delay(video_parts[1] if len(video_parts) > 1 else None, None, "video")
    if not os.path.isfile(video_file):
            logging.error(f"Video file not found: {video_file}")
            sys.exit(1)

    # Flatten audio args in case multiple --audio flags are used
    audio_specs = []
    for entry in args.audio:
        if isinstance(entry, list):
            audio_specs.extend(entry)
        else:
            audio_specs.append(entry)

    # Parse audio arguments (file[:volume[:delay[:repeat]]])
    audio_tracks: list[AudioTrack] = []
    for audio_spec in audio_specs:
        parts = audio_spec.split(":")
        file = parts[0]
        volume, delay = parse_volume_delay(parts[1] if len(parts) > 1 else None, parts[2] if len(parts) > 2 else None, file)
        repeat_str = parts[3] if len(parts) > 3 else None
        repeat = 0
        if repeat_str:
            if repeat_str == _REPEAT_MODE_INF:
                repeat = -1
            else:
                try:
                    repeat = int(repeat_str)
                except ValueError:
                        logging.error(f"Invalid repeat for {file}: {repeat_str}")
                        sys.exit(1)
                if repeat < 0:
                        logging.error(f"Repeat for {file} must be >= 0 or '{_REPEAT_MODE_INF}' (got {repeat})")
                        sys.exit(1)
        if not os.path.isfile(file):
                logging.error(f"Audio file not found: {file}")
                sys.exit(1)
        audio_tracks.append(AudioTrack(
            file=file,
            volume=volume,
            delay=delay,
            repeat=repeat
        ))

    # Output file logic
    if args.output:
        output_file = args.output
    else:
        base, ext = os.path.splitext(video_file)
        output_file = f"{base}-mixed{ext}"

    return video_file, video_volume, audio_tracks, output_file, args.verbose, args.dry_run


def parse_volume_delay(volume_str, delay_str, file_label=""):
    try:
        volume = float(volume_str) if volume_str else 1.0
    except ValueError:
            logging.error(f"Invalid volume{f' for {file_label}' if file_label else ''}: {volume_str}")
            sys.exit(1)
    if volume <= 0:
            logging.error(f"Volume{f' for {file_label}' if file_label else ''} must be greater than 0 (got {volume})")
            sys.exit(1)
    
    try:
        delay = float(delay_str) if delay_str else 0.0
    except ValueError:
            logging.error(f"Invalid delay{f' for {file_label}' if file_label else ''}: {delay_str}")
            sys.exit(1)
    if delay < 0:
            logging.error(f"Delay{f' for {file_label}' if file_label else ''} must be >= 0 (got {delay})")
            sys.exit(1)
    return volume, delay
