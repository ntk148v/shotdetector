import os

DIRNAME = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(DIRNAME, '../static/images')
SHOTS_DIR = os.path.join(DIRNAME, '../static/shots')

OPENCV_METHODS = {
    'CV_COMP_CORREL': 1,
    'CV_COMP_CHISQR': 2,
    'CV_COMP_INTERSECT': 3,
    'CV_COMP_BHATTACHARYYA': 4,
}

THRESHOLD_CONST = 10