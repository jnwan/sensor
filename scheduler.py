import sched
import threading
import time


class Scheduler:
    def __init__(
        self,
    ) -> None:
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.stop_flag = threading.Event()
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def get_scheduler(self) -> sched.scheduler:
        return self.scheduler

    def stop(self):
        self.stop_flag.set()
        if self.thread.is_alive():
            self.thread.join()

    def run(self):
        while not self.stop_flag.is_set():
            self.scheduler.run()
