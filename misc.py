from logging import Logger
from typing import List
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
from snip import ImageSnipper
import time
import os
import pyocr
from exception import FileNotFoundException


def pil2cv(image: Image.Image) -> np.ndarray:
    ''' PIL型 -> OpenCV型 '''
    new_image = np.array(image, dtype=np.uint8)
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    return new_image


def cv2pil(image: np.ndarray) -> Image.Image:
    ''' OpenCV型 -> PIL型 '''
    new_image = image.copy()
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image,
                                 cv2.COLOR_BGRA2RGBA)
    new_image = Image.fromarray(new_image)
    return new_image


class MouseXYGetter:
    winname = 'mouse_xy'

    def __init__(self, logger: Logger) -> None:
        self.is_draw = False
        self.start_xy: tuple = None
        self.org_image: np.ndarray = None
        self.rect_image: np.ndarray = None
        self.logger = logger

    def _callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.is_draw = True
            self.start_xy = x, y

            self.rect_image = self.org_image.copy()
            cv2.circle(self.rect_image, self.start_xy, 5, (0, 255, 0), -1)

        if self.is_draw and event == cv2.EVENT_MOUSEMOVE:
            self.rect_image = self.org_image.copy()
            cv2.rectangle(self.rect_image, self.start_xy,
                          (x, y), (255, 150, 150), 3)
            cv2.circle(self.rect_image, self.start_xy, 5, (0, 255, 0), -1)

        if self.is_draw and event == cv2.EVENT_LBUTTONUP:
            self.rect_image = self.org_image.copy()
            cv2.rectangle(self.rect_image, self.start_xy,
                          (x, y), (255, 150, 155), 3)
            cv2.circle(self.rect_image, self.start_xy, 5, (0, 255, 0), -1)
            cv2.circle(self.rect_image, (x, y), 5, (0, 0, 255), -1)

            self.is_draw = False

            left_top = self.start_xy
            right_bottom = (x, y)
            width = abs(x-self.start_xy[0])
            height = abs(y-self.start_xy[1])

            self.logger.info(
                f'left-top, right-bottom: {left_top}, {right_bottom}')
            self.logger.info(f'width, height: {width}, {height}')

        if event == cv2.EVENT_RBUTTONDOWN:
            self.rect_image = self.org_image.copy()

    def get(self, image: np.ndarray):
        self.org_image = image.copy()
        self.rect_image = image.copy()

        self.is_draw = False

        cv2.namedWindow(self.winname)
        cv2.setMouseCallback(self.winname, self._callback)
        cv2.imshow(self.winname, self.rect_image)

        while cv2.waitKey(1) != 27:
            cv2.imshow(self.winname, self.rect_image)

        cv2.destroyWindow(self.winname)


def screenshot():
    snipper = ImageSnipper()

    input_str = 'r'
    while input_str not in ['s', 'c']:
        snip_image = snipper.Snip()

        cv_image = pil2cv(snip_image)

        cv2.imshow('screenshot', cv_image)
        cv2.waitKey(0)

        input_str = input('save:retake:cancel (s/r/c) -> ')

        if input_str == 's':
            now = datetime.now().strftime('%Y%m%d-%H%M%S')
            cv2.imwrite(f'./resource/screenshot/{now}.png', cv_image)
            return

        if input_str == 'c':
            return


def concat_imshow(winname: str, image_list: List[np.ndarray]):
    max_height = max([image.shape[0] for image in image_list])

    def add_border(image: np.ndarray):
        height_diff = max_height-image.shape[0]
        return cv2.copyMakeBorder(image, 0, height_diff, 1, 1,
                                  cv2.BORDER_CONSTANT, (0, 0, 0))

    concat_image = cv2.hconcat([add_border(image) for image in image_list])

    cv2.imshow(winname, concat_image)


class StopWatch:
    def __init__(self, title: str, logger: Logger):
        self.title = title
        self.logger = logger

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.info(f'{self.title}: {time.time()-self.start}')


def get_OCR(logger: Logger):
    # インストールしたTesseract-OCRのパスを環境変数「PATH」へ追記する。

    ocr_path = r"C:\Program Files\Tesseract-OCR"
    path_list = os.environ['PATH'].split(';')
    if ocr_path not in path_list:
        path_list.append(ocr_path)
    os.environ['PATH'] = ';'.join(path_list)
    logger.debug(os.environ['PATH'])

    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        raise FileNotFoundException("No OCR tool found")

    return tools[0]
