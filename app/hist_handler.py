import cv2


def calc_hist(images, channels, mask, histSize, ranges):
    """Calculate histogram

    Args:
        images (TYPE): Description
        channels (TYPE): Description
        mask (TYPE): Description
        histSize (TYPE): Description
        ranges (TYPE): Description

    Returns:
        matrix: histogram value after normalized
    """
    _hist = cv2.calcHist(images, channels, mask, histSize, ranges)
    hist = cv2.normalize(_hist, _hist).flatten()
    return hist


def comp_hist(hist1, hist2, method):
    """Compare 2 histograms

    Args:
        hist1 (matrix): 1st histogram
        hist2 (matrix): 2nd histogram
        method (int): compare method

    Returns:
        float: diff value
    """
    diff = cv2.compareHist(hist1, hist2, method)
    return diff
