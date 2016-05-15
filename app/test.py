import cv2
import copy
import math
import os

from queues import Queue, FrameQueue, DiffQueue
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
        # fourcc = int(cv2.VideoWriter_fourcc(*'XVID'))
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

    def get_diff_queue(self):
        """
        read video and get difference between any couple keyframes
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

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame_info = self.get_frame_info(
                cap.get(cv2.CAP_PROP_POS_FRAMES),
                cap.get(cv2.CAP_PROP_POS_MSEC),
                hist_handler.calc_hist([gray], [0], None, [256], [0, 256])
            )

            self.frame_queue.enqueue(frame_info)
            self.put_diff_queue()

        cap.release()
        cv2.destroyAllWindows()

    def put_diff_queue(self):
        """
        calc difference histogram and put to diff_queue
        """
        if self.frame_queue.size() < 2:
            return False
        else:
            queue = self.frame_queue.get()[-2::]
            diff_value = hist_handler.comp_hist(
                queue[0]['histogram'],
                queue[1]['histogram'],
                constants.OPENCV_METHODS['CV_COMP_CORREL'])

            diff = {
                'prev_frame': queue[1]['id'],
                'next_frame': queue[0]['id'],
                'value': diff_value
            }
            self.diff_queue.enqueue(diff)
            self.frame_queue.dequeue()
            del queue[:]
            return True

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

    def get_list_keyframes_index(self, boundary_queue):
        """
        get list index: all of keyframes
        """
        list_index = []
        i = 0
        while(True):
            if(i >= (boundary_queue.size() - 1)):
                break

            sframe_id = boundary_queue.get()[i]['next_frame']
            eframe_id = boundary_queue.get()[i + 1]['prev_frame']

            index = int(self.calc_keyframe(sframe_id, eframe_id))
            list_index.append(index)
            i += 1
            print("Key Frame : {}" . format(index))

        return list_index

    def save_keyframes(self, list_index):
        """Summary

        Args:
            list_index (TYPE): Description
        """
        if not (os.path.exists(constants.IMAGES_DIR) or
                os.path.isdir(constants.IMAGES_DIR)):
            os.makedirs(constants.IMAGES_DIR)

        #### new code ###
        cap = self.capture_video()
        if not cap.isOpened():
            raise IOError(" Something went wrong! Please check \
                           your video path again!")
        else:
            print("Everything is fine to save keyframes")

        self.shot_info(cap)
        i = 1
        while(cap.isOpened()):
            ret, frame = cap.read()

            if not ret:
                break

            if i in list_index:
                im = Image.fromarray(frame)
                im.save(
                    constants.IMAGES_DIR + "/keyframe_{}.jpg". format(i))

            i = i + 1

        cap.release()
        cv2.destroyAllWindows()

    def detect(self):
        """Detect Boundary
        """
        self.get_diff_queue()
        self.threshold = adaptive_threshold.calc_threshold(
            self.diff_queue, constants.THRESHOLD_CONST)
        boundary_queue = Queue()

        for diff in self.diff_queue.get():
            if(diff['value'] >= self.threshold):
                print("Shot Boundary Detected : {} - {}"
                      . format(diff['prev_frame'], diff['next_frame']))
                boundary_queue.enqueue(diff)

        list_index = self.get_list_keyframes_index(boundary_queue)
        self.save_keyframes(list_index)
        return list_index

if __name__ == '__main__':
    detector = ShotBoundaryDetector('/home/daidv/GITHUB/shotdetector/test_video/james.mp4')
    detector.detect()
