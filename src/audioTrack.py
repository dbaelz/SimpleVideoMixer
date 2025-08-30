from typing import TypedDict

class AudioTrack(TypedDict):
    file: str
    volume: float
    delay: float
    repeat: int