import os
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class VideoPlot:
    file: str
    volume: float
    duration: int

@dataclass
class AudioPlot:
    file: str
    volume: float
    delay: float
    duration: int
    repeat: int

def plot_timeline(video: VideoPlot, audios: List[AudioPlot]):
    """
    Timeline visualization for video and audio tracks.
    Args:
        video: VideoPlot instance
        audios: list of AudioPlot instances
    """
    # Header: Label, Volume, Delay, Repeat, Timeline
    column_label = 15
    column_info = 8

    # Table header
    header = f"{'Label':<{column_label}}{'Volume':<{column_info}}{'Delay':<{column_info}}{'Repeat':<{column_info}}"
    print(header)
    print('-' * len(header))

    def format_row(filename, volume, delay, repeat):
        fname = os.path.basename(filename)
        vol_str = f"{volume:<{column_info}.2f}" if isinstance(volume, float) else f"{volume:<{column_info}}"
        delay_str = f"{delay:<{column_info}.2f}" if isinstance(delay, float) else f"{delay:<{column_info}}"
        if repeat == -1:
            repeat_str = "infinite"
        elif repeat == '-':
            repeat_str = '-'
        else:
            repeat_str = f"{repeat}x".ljust(column_info)
        return f"{fname:<{column_label}}{vol_str}{delay_str}{repeat_str}"

    print(format_row(video.file, video.volume, '-', '-'))

    audios_sorted = sorted(audios, key=lambda x: x.delay)
    for audio in audios_sorted:
        print(format_row(audio.file, audio.volume, audio.delay, audio.repeat))
