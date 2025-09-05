import os
import shutil
import tempfile
import subprocess
from typing import List, Dict, Tuple, Optional

from audioTrack import AudioTrack
from cli import parse_args
from plot import plot_timeline
from utils import get_media_duration, has_audio_stream

def main() -> None:
    video_file, video_volume, audio_tracks_raw, output_file, verbose, dry_run = parse_args()

    # Copy each audio file to a unique temp file
    temp_files = []
    audio_tracks: List[AudioTrack] = []
    for idx, track in enumerate(audio_tracks_raw):
        orig_file = track['file']
        base, ext = os.path.splitext(os.path.basename(orig_file))
        tmp_name = os.path.join(tempfile.gettempdir(), f"{base}_{idx}{ext}")
        shutil.copy(orig_file, tmp_name)
        temp_files.append(tmp_name)
        audio_tracks.append({
            'file': tmp_name,
            'volume': track.get('volume', 1.0),
            'delay': track.get('delay', 0.0),
            'repeat': track.get('repeat', 0)
        })
    def cleanup_temp_files():
        for f in temp_files:
            try:
                os.remove(f)
            except Exception:
                pass
    import atexit
    atexit.register(cleanup_temp_files)
    video_duration = get_media_duration(video_file)

    if video_duration is None:
        print(f"[ERROR] Could not determine duration of video file: {video_file}")
        exit(1)

    # Plot
    video_plot = (video_file, video_volume, int(video_duration))
    audios_plot = []
    for idx, track in enumerate(audio_tracks):
        # Use the original filename for display in the plot
        orig_file = audio_tracks_raw[idx]['file'] if idx < len(audio_tracks_raw) else track['file']
        volume = track['volume']
        delay = track['delay']
        repeat = track['repeat']
        audio_dur = get_media_duration(track['file'])
        audios_plot.append((orig_file, volume, delay, int(audio_dur) if audio_dur else 0, repeat if repeat != 0 else 1))
    plot_timeline(video_plot, audios_plot)

    video_has_audio = has_audio_stream(video_file)
    audio_sources = collect_audio_sources(video_volume, video_has_audio, audio_tracks, video_duration)
    input_args = build_input_args(video_file, audio_sources)
    filter_complex, map_audio = build_filter_and_map(audio_sources)

    loglevel = 'verbose' if verbose else 'warning'
    cmd = ['ffmpeg', '-loglevel', loglevel, *input_args]
    if filter_complex:
        cmd += ['-filter_complex', filter_complex]
    cmd += ['-map', '0:v']
    if map_audio:
        cmd += ['-map', map_audio, '-c:a', 'aac']
    cmd += ['-c:v', 'copy', output_file]

    if verbose or dry_run:
        print('FFmpeg command:')
        print(' '.join(cmd))
    if dry_run:
        print("Dry run: ffmpeg command not executed.")
        return

    try:
        subprocess.run(cmd, check=True)
        print(f"Mixing completed: {output_file}")
    except subprocess.CalledProcessError:
        print("FFmpeg failed.")
        print(f"Command: {' '.join(cmd)}")
        exit(1)

def collect_audio_sources(
    video_volume: float,
    video_has_audio: bool,
    audio_tracks: List[AudioTrack],
    video_duration: float
) -> List[Dict]:
    sources = []
    if video_has_audio:
        sources.append({
            'input_idx': 0,
            'filter': f"[0:a]volume={video_volume}[a0]",
            'label': 'a0',
            'type': 'video'
        })
    # Audio tracks start at input 1 (video is always input 0)
    audio_input_start = 1
    for i, track in enumerate(audio_tracks):
        audio_input_idx = audio_input_start + i
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
        if requested_repeat == -1:
            repeat = max_full_repeats
        elif requested_repeat == 0:
            repeat = 1 if max_full_repeats >= 1 else 0
        else:
            repeat = min(requested_repeat, max_full_repeats)
        if repeat == 0:
            print(f"[WARN] Audio '{track['file']}' not added: repeat window too short for any full repeat.")
            continue
        delay_ms = int(track['delay'] * 1000)
        adelay = f"adelay={delay_ms}|{delay_ms}" if delay_ms > 0 else ""
        volume = f"volume={track['volume']}"
        filters = ','.join(filter for filter in [adelay, volume] if filter)
        sources.append({
            'input_idx': audio_input_idx,
            'filter': f"[{audio_input_idx}:a]{filters}[a{audio_input_idx}]",
            'label': f"a{audio_input_idx}",
            'type': 'audio',
            'repeat': repeat,
            'file': track['file']
        })
    return sources

def build_input_args(video_file: str, audio_sources: List[Dict]) -> List[str]:
    args = ['-i', video_file]
    for src in audio_sources:
        if src.get('type') == 'audio':
            repeat = src.get('repeat', 1)
            if repeat > 1:
                args += ['-stream_loop', str(repeat-1)]
            args += ['-i', src['file']]
    return args

def build_filter_and_map(audio_sources: List[Dict]) -> Tuple[Optional[str], Optional[str]]:
    if not audio_sources:
        return None, None
    filter_parts = [src['filter'] for src in audio_sources]
    labels = [src['label'] for src in audio_sources]
    if len(labels) == 1:
        return ';'.join(filter_parts), f"[{labels[0]}]"
    amix_inputs_str = ''.join([f"[{label}]" for label in labels])
    filter_parts.append(f"{amix_inputs_str}amix=inputs={len(labels)}:normalize=0[aout]")
    return ';'.join(filter_parts), '[aout]'

if __name__ == "__main__":
    main()