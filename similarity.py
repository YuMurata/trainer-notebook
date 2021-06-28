from typing import Tuple
import numpy as np
from enum import Enum, auto


class SIMILARITY(Enum):
    SQDIFF = auto()
    SQDIFF_NORMED = auto()
    CCORR = auto()
    CCORR_NORMED = auto()
    CCOEFF = auto()
    CCOEFF_NORMED = auto()


def _flatten(src_1: np.ndarray, src_2: np.ndarray) -> Tuple[np.ndarray,
                                                            np.ndarray]:
    return np.ravel(src_1), np.ravel(src_2)


_denom_eps = 1e-5


def _denom(src_1: np.ndarray, src_2: np.ndarray) -> float:
    flat_1, flat_2 = _flatten(src_1, src_2)
    return ((np.linalg.norm(flat_1, ord=2) * np.linalg.norm(flat_2, ord=2))
            + _denom_eps)


def sqdiff(src_1: np.ndarray, src_2: np.ndarray) -> float:
    flat_1, flat_2 = _flatten(src_1, src_2)
    return np.linalg.norm(flat_1-flat_2, ord=2) ** 2


def sqdiff_normed(src_1: np.ndarray, src_2: np.ndarray) -> float:
    return sqdiff(src_1, src_2)/_denom(src_1, src_2)


def ccorr(src_1: np.ndarray, src_2: np.ndarray) -> float:
    flat_1, flat_2 = _flatten(src_1, src_2)
    return np.dot(flat_1, flat_2)


def ccorr_normed(src_1: np.ndarray, src_2: np.ndarray) -> float:
    return ccorr(src_1, src_2)/_denom(src_1, src_2)


def _coeff_denom(src_1: np.ndarray, src_2: np.ndarray) -> float:
    flat_1, flat_2 = _flatten(src_1, src_2)

    mean_1 = flat_1.mean()
    mean_2 = flat_2.mean()
    return (np.linalg.norm(flat_1-mean_1, ord=2)
            * np.linalg.norm(flat_2-mean_2, ord=2))+_denom_eps


def ccoeff(src_1: np.ndarray, src_2: np.ndarray) -> float:
    flat_1, flat_2 = _flatten(src_1, src_2)

    mean_1 = flat_1.mean()
    mean_2 = flat_2.mean()

    return np.dot(flat_1-mean_1, flat_2-mean_2)


def ccoeff_normed(src_1: np.ndarray, src_2: np.ndarray) -> float:
    return ccoeff(src_1, src_2)/_coeff_denom(src_1, src_2)


def similarity_dict(src_1: np.ndarray, src_2: np.ndarray) -> dict:
    return {'sqdiff': sqdiff(src_1, src_2),
            'sqdiff_normed': sqdiff_normed(src_1, src_2),
            'ccorr': ccorr(src_1, src_2),
            'ccorr_normed': ccorr_normed(src_1, src_2),
            'ccoeff': ccoeff(src_1, src_2),
            'ccoeff_normed': ccoeff_normed(src_1, src_2)}
