import time


class StopWatch:
    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        print("Stopwatch started")
        if self.start_time == None:
            self.start_time = time.time()

    def elapsed(self):
        if self.start_time == None:
            return 0   
        
        current = time.time()
        timing = current - self.start_time
        print(f"Elapsed time: {timing}")
        return timing

    def end(self):
        if self.end_time != None:
            self.end_time = time.time() - self.start_time

    def reset(self):
        self.__init__()

    def restart(self):
        self.__init__()
        self.start()
