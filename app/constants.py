import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARRENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

IMAGES_DIR = os.path.join(PARRENT_DIR, 'static/images')
SHOTS_DIR = os.path.join(PARRENT_DIR, 'static/shots')

OPENCV_METHODS = {
    'CV_COMP_CORREL': 1,
    'CV_COMP_CHISQR': 2,
    'CV_COMP_INTERSECT': 3,
    'CV_COMP_BHATTACHARYYA': 4,
}

THRESHOLD_CONST = 1