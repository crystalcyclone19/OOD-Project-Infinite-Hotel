import time


class Timer:
    def __init__(self):
        self._start_time = None
        self.elapsed = 0.0

    def start(self):
        if self._start_time is not None:
            raise RuntimeError("Timer is already running")
        self._start_time = time.perf_counter()

    def stop(self,prefix :str) -> float:
        """
        reutrn in s(second)
        """
        if self._start_time is None:
            raise RuntimeError("Timer is not running")
        self.elapsed = time.perf_counter() - self._start_time
        self._start_time = None
        return self.format_duration(self.elapsed,prefix)
        
  
    def format_duration(self,seconds: float, prefix :str) -> float:
        if prefix == "s":
            return seconds 
        if prefix == "ms":
            return seconds * 1e3
        if prefix == "us":
            return seconds * 1e6
        return seconds * 1e9