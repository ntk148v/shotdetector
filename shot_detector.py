import cv2
import copy
import math
import os
import logging

from queues import Queue, FrameQueue, DiffQueue
import constants
import hist_handler
import adaptive_threshold

from PIL import Image


fps = None
fourcc = None
framesize = None
logger = logging.getLogger(__name__)


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

    def capture_video(self):
        """Capture source video

        Returns:
            VideoCapture: capture
        """
        return cv2.VideoCapture(self.video_path)

    def shot_info(self, cap):
        """Set shot information

        Args:
            cap (cv2.VideoCapture): 
        """
        global fps, fourcc, framesize
        fps = cap.get(cv2.CAP_PROP_FPS)
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
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
            logger.exception(" Something went wrong! Please check \
                           your video path again!")
            raise IOError
        else:
            logger.info("Everything is fine")

        self.shot_info(cap)

        while(cap.isOpened()):
            logger.info("Read frame from video...")
            ret, frame = cap.read()

            if not ret:
                logger.info("No more frame")
                break

            self.frames.append(frame)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame_info = self.get_frame_info(
                cap.get(cv2.CAP_PROP_POS_FRAMES),
                cap.get(cv2.CAP_PROP_POS_MSEC),
                hist_handler.calc_hist([gray], [0], None, [256], [0, 256])
            )
            logger.info("Put frame info to queue...")
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
        """Calculate keyframe

        Args:
            sframe_id (float): start frame of shot id
            eframe_id (float): end frame of shot id

        Returns:
            float: key frame - middle frame of shot id.
        """
        mframe_id = sframe_id + \
            math.floor(abs(eframe_id - sframe_id) / 2)
        return mframe_id

    def save_keyframe(self, sframe_id, eframe_id):
        """Save keyframe

        Args:
            sframe_id (float): start frame of shot id
            eframe_id (float): end frame of shot id
        """
        index = int(self.calc_keyframe(sframe_id, eframe_id))
        print("Key Frame : {}" . format(index))

        im = Image.fromarray(self.frames[int(index)])

        if not (os.path.exists(constants.IMAGES_DIR) or
                os.path.isdir(constants.IMAGES_DIR)):
            logger.info("Create keyframe folder")
            os.makedirs(constants.IMAGES_DIR)

        im.save(
            constants.IMAGES_DIR + "/keyframe_{}.jpg". format(int(index)))
        logger.info(
            "Save keyframe of shot {} - {}" . format(sframe_id, eframe_id))

    def save_shot(self, sframe_id, eframe_id):
        """Save shot

        Args:
            sframe_id (float): start frame of shot id
            eframe_id (float): end frame of shot id
        """
        if not (os.path.exists(constants.SHOTS_DIR) or
                os.path.isdir(constants.SHOTS_DIR)):
            logger.info("Create shot folder")
            os.makedirs(constants.SHOTS_DIR)
        path = constants.SHOTS_DIR + \
            "/{}_{}.avi" . format(int(sframe_id), int(eframe_id))
        out = cv2.VideoWriter(path, fourcc, fps, framesize)
        for frame in self.frames[int(sframe_id):int(eframe_id)]:
            out.write(frame)
        logger.info(
            "Save keyframe of shot {} - {}" . format(sframe_id, eframe_id))
        out.release()

    def save(self, boundary_queue):
        """Save both keyframe and shot 

        Args:
            boundary_queue (list): boundary queue
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
        logger.info("Set threshold")
        self.threshold = adaptive_threshold.calc_threshold(
            self.diff_queue, constants.THRESHOLD_CONST)
        boundary_queue = Queue()

        for diff in self.diff_queue.get():
            if(diff['value'] >= self.threshold):
                logger.info("Shot boundary detected : {} - {}"
                            . format(diff['prev_frame'], diff['next_frame']))
                boundary_queue.enqueue(diff)
            else:
                logger.info("No shot boundary detected")

        self.save(boundary_queue)
