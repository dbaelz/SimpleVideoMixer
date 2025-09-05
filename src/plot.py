import os
from typing import List, Tuple

def plot_timeline(video: Tuple[str, float, int], audios: List[Tuple[str, float, float, int, int]]):
    """
    Timeline visualization for video and audio tracks.
    Args:
        video: (filename, volume, duration)
        audios: list of (filename, volume, offset, duration, repeat)
    """
    video_file, video_vol, video_dur = video


    # Header: Label, Volume, Delay, Repeat, Timeline
    col_label = 15
    col_vol = 8
    col_delay = 8
    col_repeat = 8

    # Table header
    header = f"{'Label':<{col_label}}{'Volume':<{col_vol}}{'Delay':<{col_delay}}{'Repeat':<{col_repeat}}"
    print(header)
    print('-' * len(header))

    def format_row(filename, volume, delay, repeat):
        fname = os.path.basename(filename)
        vol_str = f"{volume:<{col_vol}.2f}" if isinstance(volume, float) else f"{volume:<{col_vol}}"
        delay_str = f"{delay:<{col_delay}.2f}" if isinstance(delay, float) else f"{delay:<{col_delay}}"
        if repeat == -1:
            repeat_str = "infinite"
        elif repeat == '-':
            repeat_str = '-'
        else:
            repeat_str = f"{repeat}x".ljust(col_repeat)
        return f"{fname:<{col_label}}{vol_str}{delay_str}{repeat_str}"

    print(format_row(video_file, video_vol, '-', '-'))

    audios_sorted = sorted(audios, key=lambda x: x[2])
    for audio_file, audio_vol, offset, _, repeat in audios_sorted:
        print(format_row(audio_file, audio_vol, offset, repeat))
