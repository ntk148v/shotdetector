class Queue(object):

    """Basic Queue

    Attributes:
        queue (list): Description
        queue (list)
    """

    def __init__(self):
        """Initalize
        """
        self.queue = []

    def get(self):
        """Get queue

        Returns:
            list: queue
        """
        return self.queue

    def is_empty(self):
        """Check Empty

        Returns:
            boolean: check queue is empty or not
        """
        return self.queue == []

    def enqueue(self, item):
        """Put item to queue

        Args:
            item (TYPE): queue's new item
        """
        self.queue.insert(0, item)

    def dequeue(self):
        """Pop item from queue

        Returns:
            item: last item in queue
        """
        return self.queue.pop()

    def size(self):
        """Get size of queue

        Returns:
            int: queue length
        """
        return len(self.queue)


class FrameQueue(Queue):

    """Frame Queue
    item in queue
    {
        'id': id,
        'histogram' : histogram,
        'position' : position
    }
    """

    def __init__(self):
        """Initalize
        """
        Queue.__init__(self)

    def get_id(self, index):
        """Get item's id

        Args:
            index (int): Index of item in queue

        Returns:
            id: id of item
        """
        try:
            id = self.queue[index]['id']
        except IndexError(" error"):
            id = None
        return id

    def get_histogram(self, index):
        """Get item's histogram

        Args:
            index (int): Index of item in queue

        Returns:
            matrix: Item's histogram
        """
        try:
            hist = self.queue[index]['histogram']
        except IndexError(" error"):
            hist = None
        return hist

    def get_position(self, index):
        """Get item's position
           Position of frame in video

        Args:
            index (int): Index of item in queue

        Returns:
            second: Item's position
        """
        try:
            pos = self.queue[index]['position']
        except IndexError(" error"):
            pos = None
        return pos


class DiffQueue(Queue):

    """Difference Queue
    item in queue
    {
        'prev_frame' : prev_frame_id,
        'next_frame' : next_frame_id,
        'value' : comprasion value between 2 frames
    }
    """

    def __init__(self):
        """Initalize
        """
        Queue.__init__(self)
