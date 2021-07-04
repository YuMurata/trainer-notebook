from collections import UserDict
from exception import InvalidTypeException
from typing import NamedTuple, Tuple
from PIL import Image, ImageTk, ImageDraw
from logger import CustomLogger

logger = CustomLogger(__name__)


class ScaleRatioRange(NamedTuple):
    max: float
    min: float


class RatioClipper:
    ratio_range = ScaleRatioRange(3.0, 0.5)

    @staticmethod
    def clip(ratio: float):
        return max(min(ratio, RatioClipper.ratio_range.max),
                   RatioClipper.ratio_range.min)


class Emphasis(NamedTuple):
    width: int
    outline: Tuple[int, int, int]


class ImageStruct:
    def __init__(self, image: Image.Image) -> None:
        self.image = image
        self.photoimage = ImageTk.PhotoImage(image)
        self.scale_ratio = 1.0
        self.emphasis: Emphasis = None

    def step_scale(self, step: float) -> ImageTk.PhotoImage:
        return self.scale(self.scale_ratio+step)

    def scale(self, scale_ratio: float) -> ImageTk.PhotoImage:
        self.scale_ratio = RatioClipper.clip(scale_ratio)
        x, y = self.image.size
        x, y = int(x*self.scale_ratio), int(y*self.scale_ratio)

        image = self.image.resize((x, y))

        if self.emphasis:
            w, h = image.size
            draw = ImageDraw.Draw(image)

            draw.rectangle((0, 0, w-1, h-1), width=self.emphasis.width,
                           outline=self.emphasis.outline)

        self.photoimage = ImageTk.PhotoImage(image)
        return self.photoimage

    def set_emphasis(self, emphasis: Emphasis):
        self.emphasis = emphasis
        self.scale(self.scale_ratio)

    def copy(self):
        return ImageStruct(self.image.copy())


class ImageStructDict(UserDict):
    def __init__(self) -> None:
        super().__init__()
        self.scale_ratio = 1.0

    def __setitem__(self, key: str, item: ImageStruct) -> None:
        if type(item) != ImageStruct:
            raise InvalidTypeException(
                f'set allow only ImageStruct, got {type(item)}')
        return super().__setitem__(key, item)

    def __getitem__(self, key: str) -> ImageStruct:
        return super().__getitem__(key)

    def step_scale(self, step: float):
        self.scale(self.scale_ratio+step)

    def scale(self, scale_ratio: float):
        self.scale_ratio = RatioClipper.clip(scale_ratio)
        for item_id in self.data.keys():
            self.data[item_id].scale(self.scale_ratio)

    def get_last_key(self):
        return next(iter(reversed(self.data)))
