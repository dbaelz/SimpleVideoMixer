import argparse


PROGRAM_NAME = "Simple Video Mixer"
VERSION = "0.0.1"


def parse_args():
    parser = argparse.ArgumentParser(description="Mix video and audio sources", add_help=True)
    parser.add_argument("--version", action="version", version=f"{PROGRAM_NAME} - version {VERSION}")

    parser.add_argument(
        "--video",
        required=True,
        help="Input video file, optionally with volume as file:volume (e.g. video.mp4:0.8). Volume is optional, default 1.0."
    )

    parser.add_argument(
        "--audio",
        action="append",
        default=[],
        help="Audio file(s) to mix, format: file[:volume[:delay]]. Can be used multiple times. Volume and delay are optional, default 1.0 and 0."
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file (default: input video filename with '-mixed' before extension)"
    )

    args = parser.parse_args()

    # Parse video argument (file[:volume])
    video_parts = args.video.split(":")
    video_file = video_parts[0]
    video_volume = float(video_parts[1]) if len(video_parts) > 1 and video_parts[1] else 1.0

    # Parse audio arguments (file[:volume[:delay]])
    audio_tracks = []
    for audio_spec in args.audio:
        parts = audio_spec.split(":")
        file = parts[0]
        volume = float(parts[1]) if len(parts) > 1 and parts[1] else 1.0
        delay = float(parts[2]) if len(parts) > 2 and parts[2] else 0.0
        audio_tracks.append({
            "file": file,
            "volume": volume,
            "delay": delay
        })

    # Output file logic
    import os
    if args.output:
        output_file = args.output
    else:
        base, ext = os.path.splitext(video_file)
        output_file = f"{base}-mixed{ext}"

    return video_file, video_volume, audio_tracks, output_file


def main() -> None:
    video_file, video_volume, audio_tracks, output_file = parse_args()

    # For demonstration, print parsed arguments
    print(f"Video: {video_file}, volume: {video_volume}")
    for i, track in enumerate(audio_tracks, 1):
        print(f"Audio {i}: {track['file']}, volume: {track['volume']}, delay: {track['delay']}")
    print(f"Output: {output_file}")
    
if __name__ == "__main__":
    main()