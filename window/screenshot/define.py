from typing import Callable
from pathlib import Path

screenshot_dir = Path('./resource/user/screenshot')
screenshot_dir.mkdir(parents=True, exist_ok=True)

LoadImage = Callable[[], None]
