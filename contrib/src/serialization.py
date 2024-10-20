import json
import logging
import pickle
import shutil
from pathlib import Path
from typing import Union, Any

import numpy as np
import pandas as pd
from PIL import Image
from matplotlib import pyplot as plt

logger = logging.getLogger(__name__)


def path_with_suffix(path: Union[Path, str], suffix):
    path = Path(path)
    return path.parent / (path.stem + f'.{suffix}')


def save_to_pdf(path, format="pdf"):
    logger.info(f'Saving figure to: {path}')
    path = path_with_suffix(path, suffix=format)
    plt.savefig(path, format=format, bbox_inches="tight")
    return


def save_to_txt(data, path):
    logger.info(f'Saving {len(data)} rows to txt file: {path}')
    with open(path, 'w') as f:
        for d in data:
            f.write(f'{d}\n')


def save_img(img, path):
    logger.debug(f'Saving an image to: {str(path)}')
    img.save(path)
    return


def save_numpy(obj, path, allow_pickle=True):
    logger.debug(f'Saving Numpy array to: {path}')
    np.save(path, obj, allow_pickle=allow_pickle)
    return


def save_to_pkl(obj, path):
    logger.debug(f'Saving object via Pickle to: {path}')
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def save_to_parquet(df: pd.DataFrame, path):
    logger.info(f'Saving {len(df)} data rows to parquet: {path}')
    df.to_parquet(path)
    return


def load_parquet(path):
    logger.info(f'Reading data from a parquet file: {path}')
    data = pd.read_parquet(path)
    logger.info(f'  loaded {len(data)} rows')
    return data


def load_csv(path):
    logger.info(f'Reading data from a CSV file: {path}')
    data = pd.read_csv(path)
    logger.info(f'  loaded {len(data)} rows')
    return data


def load_numpy(path, allow_pickle: bool = False):
    logger.debug(f'Loading Numpy data from: {path}')
    try:
        data = np.load(str(path), allow_pickle=allow_pickle)
    except ValueError as ve:
        logger.warning(f'{ve}')
        logger.warning('Try setting `allow_pickle=True` to load this file')
        data = None
    except pickle.PickleError as pe:
        logger.warning(f'{pe}')
        data = None
    return data


def load_json(path):
    logger.debug(f'Loading JSON data from: {path}')
    with open(path) as f:
        return json.load(f)


def load_img(path) -> Image:
    logger.debug(f'Loading image from: {path}')
    return Image.open(path)


def load_pkl(path):
    logger.debug(f'Loading Pickle data from: {path}')
    with open(path, 'rb') as f:
        return pickle.load(f)


def load_adaptively(path):
    path = Path(path)
    extension = str(path.suffix)[1:]  # strip the '.'
    if extension in {'npz', 'npy'}:
        func = load_numpy
    elif extension == 'json':
        func = load_json
    elif extension in {'jpeg', 'jpg', "png"}:
        func = load_img
    elif extension in {'pickle', 'pkl'}:
        func = load_pkl
    else:
        raise NotImplementedError

    return func(path)


def save_adaptively(path: str, obj: Any):
    """
    Generic save function for images, pickles and numpy objects.

    Args:
        path (str): Filename where the object is to be stored. Must contain file extension.
        obj (Any): Python object to save.

    Raises:
        RuntimeError: Raised when filename does not contain a file extension.
    """
    file_components = path.split(".")
    if len(file_components) == 1:
        raise RuntimeError("You need to specify a file extension.")

    file_ext = file_components[1]
    if file_ext == "npy":
        save_numpy(obj, path)
    elif file_ext in ["png", "jpg", "jpeg"]:
        save_img(obj, path)
    elif file_ext == "pkl":
        save_to_pkl(obj, path)


def copy_file(src_fname: str, tgt_fname: str):
    logger.debug(f'Copying from {src_fname} to {tgt_fname}')
    shutil.copy(src_fname, tgt_fname)
