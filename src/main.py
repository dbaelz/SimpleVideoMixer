import os
import subprocess

from cli import parse_args

def main() -> None:
    video_file, video_volume, audio_tracks, output_file, verbose, dry_run = parse_args()

    video_duration = get_media_duration(video_file)
    if video_duration is None:
        print(f"[ERROR] Could not determine duration of video file: {video_file}")
        exit(1)

    # Prepare ffmpeg input arguments, using -stream_loop for repeats
    input_args = ['-i', video_file]
    filter_parts = []
    filter_parts.append(f"[0:a]volume={video_volume}[a0]")
    actual_audio_tracks = []
    for idx, track in enumerate(audio_tracks, 1):
        audio_duration = get_media_duration(track['file'])
        if audio_duration is None or audio_duration == 0:
            print(f"[WARN] Audio '{track['file']}' not added: could not determine duration or duration is zero.")
            continue

        offset = track['delay']
        available = video_duration - offset
        if available < audio_duration:
            print(f"[WARN] Audio '{track['file']}' not added: repeat window too short for any full repeat.")
            continue
        
        max_full_repeats = int(available // audio_duration)
        requested_repeat = track.get('repeat', 0)
        if requested_repeat == -1:  # inf
            repeat = max_full_repeats
        elif requested_repeat == 0:
            repeat = 1 if max_full_repeats >= 1 else 0
        else:
            repeat = min(requested_repeat, max_full_repeats)

        if repeat == 0:
            print(f"[WARN] Audio '{track['file']}' not added: repeat window too short for any full repeat.")
            continue

        if repeat > 1:
            input_args += ['-stream_loop', str(repeat-1)]
        input_args += ['-i', track['file']]
        delay_ms = int(track['delay'] * 1000)
        adelay = f"adelay={delay_ms}|{delay_ms}" if delay_ms > 0 else ""
        volume = f"volume={track['volume']}"
        filters = []
        if adelay:
            filters.append(adelay)
        filters.append(volume)
        filter_str = ','.join(filters)
        filter_parts.append(f"[{idx}:a]{filter_str}[a{idx}]")
        actual_audio_tracks.append(track)

    amix_inputs = len(actual_audio_tracks) + 1
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


def get_media_duration(filename):
    """Return duration in seconds as float, or None on error."""
    try:
        result = subprocess.run([
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            filename
        ], capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception:
        return None


if __name__ == "__main__":
    main()