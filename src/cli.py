import argparse
import os

PROGRAM_NAME = "Simple Video Mixer"
VERSION = "0.0.1"


def parse_args():
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
        nargs='+',
        default=[],
        help="Audio file(s) to mix, format: file[:volume[:delay]]. You can specify multiple files after -a. Volume and delay are optional, default 1.0 and 0."
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
        print(f"Error: Video file not found: {video_file}")
        exit(1)

    # Parse audio arguments (file[:volume[:delay]])
    audio_tracks = []
    for audio_spec in args.audio:
        parts = audio_spec.split(":")
        file = parts[0]
        volume, delay = parse_volume_delay(parts[1] if len(parts) > 1 else None, parts[2] if len(parts) > 2 else None, file)
        if not os.path.isfile(file):
            print(f"Error: Audio file not found: {file}")
            exit(1)
        audio_tracks.append({
            "file": file,
            "volume": volume,
            "delay": delay
        })

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
        print(f"Error: Invalid volume{f' for {file_label}' if file_label else ''}: {volume_str}")
        exit(1)
    if volume <= 0:
        print(f"Error: Volume{f' for {file_label}' if file_label else ''} must be greater than 0 (got {volume})")
        exit(1)
    
    try:
        delay = float(delay_str) if delay_str else 0.0
    except ValueError:
        print(f"Error: Invalid delay{f' for {file_label}' if file_label else ''}: {delay_str}")
        exit(1)
    if delay < 0:
        print(f"Error: Delay{f' for {file_label}' if file_label else ''} must be >= 0 (got {delay})")
        exit(1)
    return volume, delay
