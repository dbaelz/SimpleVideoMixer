import subprocess
from typing import Optional

def get_media_duration(filename: str) -> Optional[float]:
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

def has_audio_stream(file: str) -> bool:
    try:
        result = subprocess.run([
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'a',
            '-show_entries', 'stream=index',
            '-of', 'csv=p=0',
            file
        ], capture_output=True, text=True, check=True)
        return bool(result.stdout.strip())
    except Exception:
        return False