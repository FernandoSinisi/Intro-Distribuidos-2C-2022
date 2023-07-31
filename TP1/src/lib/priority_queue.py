import itertools
from queue import PriorityQueue

LOW_PRIO = 2
HIGH_PRIO = 1

class PQueue:

    def __init__(self):
        self.counter = itertools.count()
        self.queue = PriorityQueue()
    
    def put_low(self, e):
        self.queue.put((LOW_PRIO, next(self.counter), e))
    
    def put_high(self, e):
        self.queue.put((HIGH_PRIO, next(self.counter), e))
    
    def get(self, timeout=None):
        return self.queue.get(timeout=timeout)[2]