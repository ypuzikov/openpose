"""
Visualizing Openpose BODY_25 outputs; based on Openpose documentation and this NB:
https://github.com/cchamber/visualize_keypoints/blob/master/scripts/extract_kp_plot.ipynb

"""
import logging
from itertools import islice, cycle
from typing import List, Tuple, Dict, Optional

import matplotlib.pyplot as plt
from PIL import Image

from contrib.src.serialization import load_json

logger = logging.getLogger(__name__)

body_parts = ["Nose", "Neck", "RShoulder", "RElbow", "RWrist", "LShoulder", "LElbow", "LWrist", "RHip", "RKnee",
              "RAnkle",
              "LHip", "LKnee",
              "LAnkle", "REye", "LEye", "REar", "LEar"]

joints = [['RShoulder', 'Neck', 'RElbow'],
          ['RElbow', 'RShoulder', 'RWrist'],
          ['RHip', 'LHip', 'RKnee'],
          ['RKnee', 'RHip', 'RAnkle'],
          ['LShoulder', 'Neck', 'LElbow'],
          ['LElbow', 'LShoulder', 'LWrist'],
          ['LHip', 'RHip', 'LKnee'],
          ['LKnee', 'LHip', 'LAnkle']]

limbSeq = [
    [0, 15], [15, 17],
    [0, 16], [16, 18],
    [0, 1],
    [1, 2], [2, 3], [3, 4],
    [1, 5], [5, 6], [6, 7],
    [1, 8],
    [8, 9], [9, 10], [10, 11], [11, 22], [22, 23], [11, 24],
    [8, 12], [12, 13], [13, 14], [14, 21], [14, 19], [19, 20],

]

colors = cycle([[255, 0, 0], [255, 85, 0], [255, 170, 0], [255, 255, 0], [170, 255, 0], [85, 255, 0],
                [0, 255, 0],
                [0, 255, 85], [0, 255, 170], [0, 255, 255], [0, 170, 255], [0, 85, 255], [0, 0, 255],
                [85, 0, 255],
                [170, 0, 255], [255, 0, 255], [255, 0, 170], [255, 0, 85], [255, 0, 0]])

KEYPOINT_AREAS = ['pose_keypoints_2d',
                  'face_keypoints_2d',
                  'hand_left_keypoints_2d',
                  'hand_right_keypoints_2d']


def plot_openpose_overlay_img(img: Image,
                              keypoints: Dict[str, Tuple[List[float], List[float], List[float]]],
                              overlay: bool = True,
                              out_fn: Optional[str] = None) -> None:
    logger.debug(f'Plotting Openpose results')
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))
    if overlay:
        ax.imshow(img)

    plot_skeleton(ax, keypoints, conf_thresh=0.1)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xticks([])
    ax.set_yticks([])

    if not overlay:
        plt.gca().invert_yaxis()

    if out_fn is not None:
        plt.savefig(out_fn)

    plt.show()
    return


def plot_skeleton(ax, keypoints, conf_thresh: float = 0.1):
    for area in KEYPOINT_AREAS:

        if area not in keypoints:
            logger.warning(f'Area `{area}` not in default KEYPOINT_AREAS -> skipping')
            continue

        logger.info(f'- {area}')
        xs, ys, confs = keypoints[area]

        # plot keypoint markers
        plot_kpt_markers(ax, xs, ys, confs, conf_thresh)

        # also plot limbs and other segments for the pose area,
        # (other areas are not supported yet)
        if area == 'pose_keypoints_2d':
            plot_limbs(ax, xs, ys, confs, limbSeq, conf_thresh)

    return


def plot_kpt_markers(ax, xs, ys, confs, conf_thresh: float):
    for i in range(len(xs)):
        if confs[i] >= conf_thresh:
            next_color = next(colors)
            ax.plot(xs[i], ys[i], 'o', markersize=10, alpha=0.3, color=[j / 255 for j in next_color])
    return


def plot_limbs(ax, xs, ys, confs, limbSeq, conf_thresh: float):
    for start_i, end_i in limbSeq:
        if confs[start_i] >= conf_thresh and confs[end_i] >= conf_thresh:
            next_color = next(colors)
            plot_data1 = [xs[start_i], xs[end_i]]
            plot_data2 = [ys[start_i], ys[end_i]]
            ax.plot(plot_data1, plot_data2, linewidth=5, color=[j / 255 for j in next_color], alpha=0.3)
    return


def chunk(arr, arr_size):
    arr = iter(arr)
    return iter(lambda: tuple(islice(arr, arr_size)), ())


def read_openpose_json(openpose_fn) -> Dict[str, Tuple[List[float], List[float], List[float]]]:
    openpose_data = load_json(openpose_fn)
    kpts = {}
    for k in KEYPOINT_AREAS:
        _kpts = openpose_data['people'][0][k]
        xs = []
        ys = []
        confs = []
        for (x, y, c) in chunk(_kpts, 3):
            xs.append(x)
            ys.append(y)
            confs.append(c)
        kpts[k] = (xs, ys, confs)

    return kpts
