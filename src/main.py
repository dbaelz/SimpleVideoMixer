import os
import subprocess

from cli import parse_args

def main() -> None:
    video_file, video_volume, audio_tracks, output_file, verbose, dry_run = parse_args()

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

    loglevel = 'verbose' if verbose else 'warning'
    # Build full ffmpeg command
    cmd = [
        'ffmpeg',
        '-loglevel', loglevel,
        *input_args,
        '-filter_complex', filter_complex,
        '-map', '0:v',
        '-map', '[aout]',
        '-c:v', 'copy',
        '-c:a', 'aac',
        output_file
    ]

    if verbose or dry_run:
        print('FFmpeg command:')
        print(' '.join(cmd))

    if dry_run:
        print("Dry run: ffmpeg command not executed.")
        return

    # Run ffmpeg
    try:
        result = subprocess.run(cmd, check=True)
        print(f"Mixing completed: {output_file}")
    except subprocess.CalledProcessError as e:
        print("FFmpeg failed.")
        print(f"Command: {' '.join(cmd)}")
        exit(1)

if __name__ == "__main__":
    main()