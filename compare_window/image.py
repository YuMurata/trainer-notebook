from collections import UserDict
from typing import Dict, NamedTuple
from PIL import Image, ImageTk
from logger import init_logger

logger = init_logger(__name__)


class ScaleRatioRange(NamedTuple):
    max: float
    min: float


class RatioClipper:
    ratio_range = ScaleRatioRange(3.0, 0.5)

    @staticmethod
    def clip(ratio: float):
        return max(min(ratio, RatioClipper.ratio_range.max),
                   RatioClipper.ratio_range.min)


class ImageStruct:
    def __init__(self, image: Image.Image) -> None:
        self.image = image
        self.photoimage = ImageTk.PhotoImage(image)
        self.scale_ratio = 1.0

    def step_scale(self, step: float) -> ImageTk.PhotoImage:
        return self.scale(self.scale_ratio+step)

    def scale(self, scale_ratio: float) -> ImageTk.PhotoImage:
        self.scale_ratio = RatioClipper.clip(scale_ratio)
        logger.debug(f'scale: {self.scale_ratio}')
        x, y = self.image.size
        x, y = int(x*self.scale_ratio), int(y*self.scale_ratio)
        self.photoimage = ImageTk.PhotoImage(self.image.resize((x, y)))
        return self.photoimage

    def copy(self):
        return ImageStruct(self.image.copy())


class ImageStructDict(UserDict):
    def __init__(self) -> None:
        super().__init__()
        self.scale_ratio = 1.0

    def step_scale(self, step: float):
        self.scale(self.scale_ratio+step)

    def scale(self, scale_ratio: float):
        self.scale_ratio = RatioClipper.clip(scale_ratio)
        for item_id in self.data.keys():
            self.data[item_id].scale(self.scale_ratio)

    def get_last_key(self):
        return next(iter(reversed(self.data)))
