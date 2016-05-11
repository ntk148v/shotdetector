"""Summary

Attributes:
    fourcc (TYPE): Description
    fps (TYPE): Description
    framesize (TYPE): Description
"""
import cv2
import copy
import math
import os

from queues import Queue, FrameQueue, DiffQueue
from shot_writter import ShotWritter
import constants
import hist_handler
import adaptive_threshold

from PIL import Image


fps = None
fourcc = None
framesize = None


class ShotBoundaryDetector(object):

    """Shot Boundary Detector

    Attributes:
        diff_queue (DiffQueue): queue contain diff between 2 frames
        frame_queue (FrameQueue): queue contain frame
        frames (list): Description
        swritter (TYPE): Description
        threshold: adaptive threshold
        video_path (string): path of source video
    """

    def __init__(self, video_path):
        """Initalize

        Args:
            video_path (string): path of source video
        """
        self.video_path = video_path
        self.frame_queue = FrameQueue()
        self.diff_queue = DiffQueue()
        self.frames = []
        self.swritter = ShotWritter()

    def capture_video(self):
        """Capture source video

        Returns:
            VideoCapture: capture
        """
        return cv2.VideoCapture(self.video_path)

    def shot_info(self, cap):
        """Summary

        Args:
            cap (TYPE): Description

        Returns:
            TYPE: Description
        """
        global fps, fourcc, framesize
        fps = cap.get(cv2.CAP_PROP_FPS)
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        # fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        framesize = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                     int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    def get_frame_info(self, _id, _pos, _hist):
        """Get information of frame

        Args:
            _id (float): index of frame in video
            _pos (second): position of frame in video
            _hist (matrix): histogram of frame

        Returns:
            dict: frame information
        """
        frame_info = {
            'id': _id,
            'position': _pos,
            'histogram': _hist,
        }

        return frame_info

    def get_frames(self):
        """Get all frames from source video

        Raises:
            IOError: Error when can't get video
        """
        cap = self.capture_video()
        if not cap.isOpened():
            raise IOError(" Something went wrong! Please check \
                           your video path again!")
        else:
            print("Everything is fine")

        self.shot_info(cap)

        while(cap.isOpened()):
            print("Read frame from video...")
            ret, frame = cap.read()

            if not ret:
                print("No more frame")
                break

            self.frames.append(frame)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            frame_info = self.get_frame_info(
                cap.get(cv2.CAP_PROP_POS_FRAMES),
                cap.get(cv2.CAP_PROP_POS_MSEC),
                hist_handler.calc_hist([gray], [0], None, [256], [0, 256])
            )

            # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            # frame_info = self.get_frame_info(
            #     cap.get(cv2.CAP_PROP_POS_FRAMES),
            #     cap.get(cv2.CAP_PROP_POS_MSEC),
            #     hist_handler.calc_hist([hsv], [0], None, [256], [0, 256])
            # )

            self.frame_queue.enqueue(frame_info)

        cap.release()
        cv2.destroyAllWindows()

    def put_diff_queue(self):
        """Put hist diff to queue
        """
        self.get_frames()
        print("{},{},{}" . format(fps, fourcc, framesize))
        queue = copy.deepcopy(self.frame_queue)

        while(1):
            if(queue.size() < 2):
                break

            temp = queue.get()[-2::]
            diff_value = hist_handler.comp_hist(
                temp[0]['histogram'],
                temp[1]['histogram'],
                constants.OPENCV_METHODS['CV_COMP_CORREL'])

            diff = {
                'prev_frame': temp[1]['id'],
                'next_frame': temp[0]['id'],
                'value': diff_value
            }

            self.diff_queue.enqueue(diff)

            queue.dequeue()
            del temp[:]

        del queue

    def calc_keyframe(self, sframe_id, eframe_id):
        """Summary

        Args:
            sframe_id (TYPE): Description
            eframe_id (TYPE): Description

        Returns:
            TYPE: Description
        """
        mframe_id = sframe_id + \
            math.floor(abs(eframe_id - sframe_id) / 2)
        return mframe_id

    def save_keyframe(self, sframe_id, eframe_id):
        """Summary

        Args:
            sframe_id (TYPE): Description
            eframe_id (TYPE): Description

        Returns:
            TYPE: Description
        """
        index = int(self.calc_keyframe(sframe_id, eframe_id))
        print("Key Frame : {}" . format(index))

        im = Image.fromarray(self.frames[int(index)])

        if not (os.path.exists(constants.IMAGES_DIR) or
                os.path.isdir(constants.IMAGES_DIR)):
            os.makedirs(constants.IMAGES_DIR)

        im.save(
            constants.IMAGES_DIR + "/keyframe_{}.jpg". format(int(index)))

    def save_shot(self, sframe_id, eframe_id):
        """Summary

        Args:
            sframe_id (TYPE): Description
            eframe_id (TYPE): Description

        Returns:
            TYPE: Description
        """
        for frame in self.frames[int(sframe_id):int(eframe_id)]:
            if not (os.path.exists(constants.SHOTS_DIR) or
                    os.path.isdir(constants.SHOTS_DIR)):
                os.makedirs(constants.SHOTS_DIR)

            path = constants.SHOTS_DIR + \
                "/{}_{}.avi" . format(int(sframe_id), int(eframe_id))

            self.swritter.set_out(path, fourcc, fps, framesize)
            self.swritter.write(frame)
        self.swritter.release()

    def save(self, boundary_queue):
        """Summary

        Args:
            boundary_queue (TYPE): Description

        Returns:
            TYPE: Description
        """
        i = 0

        while(True):
            if(i >= (boundary_queue.size() - 1)):
                break

            sframe_id = boundary_queue.get()[i]['next_frame']
            eframe_id = boundary_queue.get()[i + 1]['prev_frame']

            self.save_keyframe(sframe_id, eframe_id)
            self.save_shot(sframe_id, eframe_id)

            i += 1

    def detect(self):
        """Detect Boundary
        """
        self.put_diff_queue()
        self.threshold = adaptive_threshold.calc_threshold(
            self.diff_queue, constants.THRESHOLD_CONST)
        boundary_queue = Queue()

        for diff in self.diff_queue.get():
            if(diff['value'] >= self.threshold):
                print("Shot Boundary Detected : {} - {}"
                      . format(diff['prev_frame'], diff['next_frame']))
                boundary_queue.enqueue(diff)

        self.save(boundary_queue)
