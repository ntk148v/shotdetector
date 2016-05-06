"""Summary
"""
import numpy as np
import cv2


class ShotWritter(object):
    """Summary
    
    Attributes:
        out (TYPE): Description
    """
    # def __init__(self):
    #     ShotWritter.__init__(self)

    def set_out(self, path, fourcc, fps, frame_size):
        """Summary
        
        Args:
            path (TYPE): Description
            fourcc (TYPE): Description
            fps (TYPE): Description
            frame_size (TYPE): Description
        
        Returns:
            TYPE: Description
        """
        self.out = cv2.VideoWriter(path, fourcc, fps, frame_size)

    def write(self, frame):
        """Summary
        
        Args:
            frame (TYPE): Description
        
        Returns:
            TYPE: Description
        """
        self.out.write(frame)

    def release(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        self.out.release()
