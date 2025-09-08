from dataclasses import dataclass
from typing import Optional, TypedDict
from enum import Enum

class AudioTrack(TypedDict):
    file: str
    volume: float
    delay: float
    repeat: int

class SourceType(Enum):
    AUDIO = "audio"
    VIDEO = "video"
    
@dataclass
class AudioSource:
    input_idx: int
    filter: str
    label: str
    type: SourceType
    repeat: Optional[int] = None
    file: Optional[str] = None