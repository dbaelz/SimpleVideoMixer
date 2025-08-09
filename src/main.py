import argparse
import os
import subprocess


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

    return video_file, video_volume, audio_tracks, output_file, args.verbose

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


def main() -> None:
    video_file, video_volume, audio_tracks, output_file, verbose = parse_args()

    # Prepare ffmpeg input arguments
    input_args = ['-i', video_file]
    for track in audio_tracks:
        input_args += ['-i', track['file']]

    filter_parts = []
    # Video audio (index 0)
    filter_parts.append(f"[0:a]volume={video_volume}[a0]")
    # Audio tracks (index 1...N)
    for idx, track in enumerate(audio_tracks, 1):
        delay_ms = int(track['delay'])
        # adelay needs value for each channel, assume stereo (|)
        adelay = f"adelay={delay_ms}|{delay_ms}" if delay_ms > 0 else ""
        volume = f"volume={track['volume']}"
        filters = []
        if adelay:
            filters.append(adelay)
        filters.append(volume)
        filter_str = ','.join(filters)
        filter_parts.append(f"[{idx}:a]{filter_str}[a{idx}]")
    # amix
    amix_inputs = len(audio_tracks) + 1
    amix_inputs_str = ''.join([f"[a{i}]" for i in range(amix_inputs)])
    filter_parts.append(f"{amix_inputs_str}amix=inputs={amix_inputs}:normalize=0[aout]")
    filter_complex = ';'.join(filter_parts)

    # Build full ffmpeg command
    cmd = [
        'ffmpeg',
        *input_args,
        '-filter_complex', filter_complex,
        '-map', '0:v',
        '-map', '[aout]',
        '-c:v', 'copy',
        '-c:a', 'aac',
        output_file
    ]

    if verbose:
        print('FFmpeg command:')
        print(' '.join(cmd))

    # Run ffmpeg
    try:
        result = subprocess.run(cmd, check=True, capture_output=not verbose, text=True)
        print(f"Mixing completed: {output_file}")
    except subprocess.CalledProcessError as e:
        print("FFmpeg failed:")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        print(f"Command: {' '.join(cmd)}")
        exit(1)

if __name__ == "__main__":
    main()