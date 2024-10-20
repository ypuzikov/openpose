"""
Visualizing Openpose outputs; based on Openpose documentation and this NB:
https://github.com/cchamber/visualize_keypoints/blob/master/scripts/extract_kp_plot.ipynb

"""
import logging
from argparse import Namespace, ArgumentParser

from contrib.src.serialization import load_img
from contrib.src.visualization.body_25 import read_openpose_json, plot_openpose_overlay_img

logger = logging.getLogger(__name__)


def parse_args():
    parser = ArgumentParser('Visualizing Openpose predictions')
    parser.add_argument("--image", type=str, help="Path to the image.")
    parser.add_argument("--openpose", type=str, help="Path to the Openpose keypoint JSON file.")
    parser.add_argument("--out", type=str, help="Path to save the output.")
    parser.add_argument("--overlay", action='store_true', help="Show keypoints as overlay with the src image.")
    return parser.parse_args()


def main(args: Namespace):
    img_fn = args.image
    img = load_img(img_fn)

    openpose_fn = args.openpose
    keypoints = read_openpose_json(openpose_fn)

    # plot
    plot_openpose_overlay_img(img, keypoints, overlay=args.overlay, out_fn=args.out)
    return


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    main(args)
    logger.info('Done')
