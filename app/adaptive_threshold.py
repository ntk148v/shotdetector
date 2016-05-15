import math


def calc_mean_dev(diff_queue):
    """Calculate mean deviation

    Args:
        diff_queue (DiffQueue): DiffQueue object

    Returns:
        float: mean deviation value
    """
    sum_diff = 0
    for diff in diff_queue.get():
        sum_diff += diff['value']

    print("Calculate Mean Deviation...")
    mean_dev = sum_diff / (diff_queue.size())
    return mean_dev


def calc_std_dev(diff_queue):
    """Calculate standard deviation

    Args:
        diff_queue (DiffQueue): DiffQueue object

    Returns:
        float: standard deviation value
    """
    tmp = 0
    mean_dev = calc_mean_dev(diff_queue)
    for diff in diff_queue.get():
        tmp += math.pow(diff['value'] - mean_dev, 2)

    print("Calculate Standard Deviation...")
    std_dev = math.sqrt(tmp / diff_queue.size())
    return std_dev


def calc_threshold(diff_queue, threshold_const):
    """Calculate adaptive threshold

    Args:
        diff_queue (DiffQueue): DiffQueue object
        threshold_const (int): Threshold constant

    Returns:
        float: adaptive threshold value
    """
    print("Calculate Adaptive Threshold...")
    threshold = calc_mean_dev(diff_queue) + \
        threshold_const * calc_std_dev(diff_queue)
    return threshold
