import cv2
import copy
import math

from queues import Queue, FrameQueue, DiffQueue
import constants
import hist_handler
import adaptive_threshold

from PIL import Image

class ShotBoundaryDetector(object):

    """Shot Boundary Detector

    Attributes:
        diff_queue (DiffQueue): queue contain diff between 2 frames
        frame_queue (FrameQueue): queue contain frame
        threshold (): adaptive threshold
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
        self.list_frame = []

    def capture_video(self):
        """Capture source video

        Returns:
            VideoCapture: capture
        """
        return cv2.VideoCapture(self.video_path)

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

        while(cap.isOpened()):
            print("Read frame from video...")
            ret, frame = cap.read()

            if not ret:
                print("No more frame")
                break

            self.list_frame.append(frame)

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
        mframe_id = sframe_id + \
            math.floor(abs(eframe_id - sframe_id) / 2)
        return mframe_id

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

        i = 0

        while(True):
            if(i >= (boundary_queue.size() - 1)):
                break

            sframe_id = boundary_queue.get()[i]['next_frame']
            eframe_id = boundary_queue.get()[i + 1]['prev_frame']
            index = int(self.calc_keyframe(sframe_id, eframe_id))
            print("Key Frame : {}" . format(index)))
            im = Image.fromarray(self.list_frame[int(index)])
            im.save("images/keyframe_{}.jpg". format(int(index)))
            i += 1
