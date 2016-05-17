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

    #-------------------------------------------------------------------------------------------------#

    def __init__(self, video_path):
        """Initalize

        Args:
            video_path (string): path of source video
        """
        self.video_path = video_path
        self.frame_queue = FrameQueue()
        self.diff_queue = DiffQueue()

    #-------------------------------------------------------------------------------------------------#

    def capture_video(self):
        """Capture source video

        Returns:
            VideoCapture: capture
        """
        return cv2.VideoCapture(self.video_path)

    #-------------------------------------------------------------------------------------------------#

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

    #-------------------------------------------------------------------------------------------------#

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

    #-------------------------------------------------------------------------------------------------#

    def get_diff_queue(self):
        """
        read video and get difference between any couple keyframes
        """
        cap = self.capture_video()
        if not cap.isOpened():
            raise IOError(
                " Something went wrong! Please check your video path again!")
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
            #print("Read frame from video...id = {}idtogram = {}".format(frame_info['id'], frame_info['histogram']))
            self.frame_queue.enqueue(frame_info)
            self.put_diff_queue()

        cap.release()
        cv2.destroyAllWindows()

    #-------------------------------------------------------------------------------------------------#

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
            # constants.OPENCV_METHODS['CV_COMP_CORREL', CV_COMP_CHISQR ,
            # CV_COMP_INTERSECT , CV_COMP_BHATTACHARYYA ])

            diff = {
                'prev_frame': queue[1]['id'],
                'next_frame': queue[0]['id'],
                'value': diff_value
            }
            print("value = {} prev_frame = {} next_frame={}".format(
                diff['value'], diff['prev_frame'], diff['next_frame']))
            self.diff_queue.enqueue(diff)
            self.frame_queue.dequeue()
            del queue[:]
            return True

    #-------------------------------------------------------------------------------------------------#

    def calc_keyframe_avg(self, sframe_id, eframe_id):
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

    #-------------------------------------------------------------------------------------------------#

    def calc_keyframe_diff_min(self, sframe_id, eframe_id):
        list_num_min = []
        list_index_min = []
        arr = self.diff_queue.get()
        arr.reverse()
        min_diff = arr[int(sframe_id)]['value']

        print(
            "-------------------------begin = {} end = {} -------------------------".format(sframe_id, eframe_id))

        for num in range(int(sframe_id), int(eframe_id+1)):
            if arr[num]['value'] < min_diff:
                min_diff = arr[num]['value']
        print("min_diff = {}".format(min_diff))
        length_list = 0
        index_min = sframe_id
        number_min = 0

        for num in range(int(sframe_id), int(eframe_id+1)):
            if arr[num]['value'] == min_diff:
                index_min = num
                number_min += 1
            else:
                if number_min > 0:
                    list_num_min.append(number_min)
                    list_index_min.append(index_min)
                    length_list += 1
                    number_min = 0

        if(arr[int(eframe_id)]['value'] == min_diff):
            list_num_min.append(number_min)
            list_index_min.append(index_min)
            length_list += 1

        max = list_num_min[0]
        index_min = list_index_min[0]
        for i in range(int(0), int(length_list)):
            print("index = {} number = {}".format(
                list_index_min[i], list_num_min[i]))
            if list_num_min[i] > max:
                max = list_num_min[i]
                index_min = list_index_min[i]
        print("max = {} index_min = {}".format(max, index_min))
        return int(index_min - max/2)

    #-------------------------------------------------------------------------------------------------#

    def calc_keyframe_diff_min_mark(self, sframe_id, eframe_id):
        length_mark = int(math.sqrt(eframe_id-sframe_id))
        if(length_mark >= (eframe_id-sframe_id+1)):
            return int((sframe_id+eframe_id)/2)
        else:
            min_mark = 0
            index_mark = sframe_id
            arr = self.diff_queue.get()
            arr.reverse()
            for i in range(int(sframe_id), int(sframe_id+length_mark)):
                min_mark += arr[i]['value']

            #print("min_mark = {}".format(min_mark))

            for i in range(int(sframe_id+1), int(eframe_id-length_mark+1)):
                sum_mark = 0
                for j in range(int(i), int(i+length_mark)):
                    sum_mark += arr[j]['value']
                    #print("j = {} sum = {}".format(j, sum_mark))
                #print("-------------------------- i = {} sum = {} -------------------------".format(i, sum_mark))
                if sum_mark < min_mark:
                    index_mark = i

        return int(index_mark+length_mark/2)

    #-------------------------------------------------------------------------------------------------#

    def calc_keyframe_diff_med(self, sframe_id, eframe_id):
        arr = self.diff_queue.get()
        arr.reverse()
        total = 0
        temp = 0
        index_diff = sframe_id
        print("start = {} end = {}".format(sframe_id, eframe_id))
        for num in range(int(sframe_id), int(eframe_id+1)):
            total += arr[num]['value']

        avg = total/(eframe_id-sframe_id+1)
        print("total = {} avg = {}".format(total, avg))

        list_diff_avg = []

        for i in range(int(sframe_id), int(eframe_id+1)):
            list_diff_avg.append(abs(avg-arr[i]['value']))

        min_diff_avg = list_diff_avg[0]
        for i in range(int(0), int(eframe_id-sframe_id)):
            if list_diff_avg[i] < min_diff_avg:
                min_diff_avg = list_diff_avg[i]
                index_diff = i

        print("min-diff-avg = {}".format(min_diff_avg))

        list_index_min_diff_avg = []
        length_list_index_min_diff_avg = 0

        for i in range(int(0), int(eframe_id-sframe_id)):
            if list_diff_avg[i] == min_diff_avg:
                list_index_min_diff_avg.append(i)
                length_list_index_min_diff_avg += 1

        return int(list_index_min_diff_avg[int(length_list_index_min_diff_avg/2)]+sframe_id)

#-------------------------------------------------------------------------------------------------#

    def get_list_keyframes_index(self, boundary_queue, algorithm=2):
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

            if algorithm == 1:
                index = int(self.calc_keyframe_avg(sframe_id, eframe_id))
            elif algorithm == 2:
                index = int(self.calc_keyframe_diff_min(sframe_id, eframe_id))
            elif algorithm == 3:
                index = int(self.calc_keyframe_diff_min_mark(sframe_id, eframe_id))
            else:
                index = int(self.calc_keyframe_diff_med(sframe_id, eframe_id))
            list_index.append(index)
            i += 1
            print("Key Frame : {}" . format(index))

        return list_index

    #-------------------------------------------------------------------------------------------------#

    def delete_dir_content(self, path):
        if not (os.path.exists(path) or os.path.isdir(path)):
            pass
        else:
            for the_file in os.listdir(path):
                file_path = os.path.join(path, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    # elif os.path.isdir(file_path): shutil.rmtree(file_path)
                except Exception as e:
                    logger.error(e)

    #-------------------------------------------------------------------------------------------------#

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
            raise IOError(
                " Something went wrong! Please check your video path again!")
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

    #-------------------------------------------------------------------------------------------------#
    def get_list_shots(self, boundary_queue):
        """ get dict (start, end) index keyframes of shots
        """
        list_shots = []
        i = 0
        while(True):
            if(i >= (boundary_queue.size() - 1)):
                break

            sframe_id = int(boundary_queue.get()[i]['next_frame'])
            eframe_id = int(boundary_queue.get()[i + 1]['prev_frame'])

            # save video here
            list_shots.append([sframe_id, eframe_id])
            i += 1

        return list_shots

    def save_shots(self, list_shots):

        if not (os.path.exists(constants.SHOTS_DIR) or
                os.path.isdir(constants.SHOTS_DIR)):
            os.makedirs(constants.SHOTS_DIR)

        #### new code ###
        cap = self.capture_video()
        if not cap.isOpened():
            raise IOError(
                " Something went wrong! Please check your video path again!")
        else:
            print("Everything is fine to save keyframes")

        self.shot_info(cap)
        i = 1  # index frame
        j = 0  # index shots
        number_shots = len(list_shots) - 1
        path = constants.SHOTS_DIR + \
            "/{}_{}.avi" . format(list_shots[j][0], list_shots[j][1])
        out = cv2.VideoWriter(path, fourcc, fps, framesize)

        while(cap.isOpened()):
            ret, frame = cap.read()

            if not ret:
                break

            if (i >= list_shots[j][0] and i <= list_shots[j][1]) or j == number_shots:
                out.write(frame)
            else:
                out.release()
                j = j + 1
                path = constants.SHOTS_DIR + \
                    "/{}_{}.avi" . format(list_shots[j][0], list_shots[j][1])
                out = cv2.VideoWriter(path, fourcc, fps, framesize)

            i = i + 1

        out.release()
        cap.release()
        cv2.destroyAllWindows()

    #-------------------------------------------------------------------------------------------------#
    def detect(self, algorithm=2, threshold=1):
        """Detect Boundary
        """
        self.get_diff_queue()
        self.threshold = adaptive_threshold.calc_threshold(
            self.diff_queue, threshold)
        boundary_queue = Queue()

        end = {
            'prev_frame': self.diff_queue.size()-1,
            'next_frame': self.diff_queue.size()-1,
            'value': 0
        }
        boundary_queue.enqueue(end)

        for diff in self.diff_queue.get():
            # print("{}".format(diff['value']))
            if(diff['value'] >= self.threshold):
                print("Shot Boundary Detected : {} - {}"
                      . format(diff['prev_frame'], diff['next_frame']))
                boundary_queue.enqueue(diff)

        start = {
            'prev_frame': 0,
            'next_frame': 0,
            'value': 0
        }
        boundary_queue.enqueue(start)

        list_index = self.get_list_keyframes_index(boundary_queue, algorithm)
        list_shots = self.get_list_shots(boundary_queue)

        self.delete_dir_content(constants.IMAGES_DIR)
        self.delete_dir_content(constants.SHOTS_DIR)

        self.save_keyframes(list_index)
        self.save_shots(list_shots)
        return list_index

    #-------------------------------------------------------------------------------------------------#

if __name__ == '__main__':
    detector = ShotBoundaryDetector(
        'C:\\Users\\tuanl\\OneDrive\\python\\shotdetector-gui\\test_video\\keyframe.avi')
    detector.detect()
