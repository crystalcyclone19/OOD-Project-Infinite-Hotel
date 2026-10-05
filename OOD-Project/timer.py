import time


class Timer:
    def __init__(self):
        self._start_time = None
        self.elapsed = 0.0

    def start(self):
        if self._start_time is not None:
            raise RuntimeError("Timer is already running")
        self._start_time = time.perf_counter()

    def stop(self):
        if self._start_time is None:
            raise RuntimeError("Timer is not running")
        self.elapsed = time.perf_counter() - self._start_time
        self._start_time = None
        return self.elapsed
        
    def format_duration(seconds: float, decimals: int = 3) -> str:
        """Convert seconds to a readable SI unit: s, ms, us, ns."""
        if seconds >= 1:
            return f"{seconds:.{decimals}f} s"
        if seconds >= 1e-3:
            return f"{seconds * 1e3:.{decimals}f} ms"
        if seconds >= 1e-6:
            return f"{seconds * 1e6:.{decimals}f} us"
        return f"{seconds * 1e9:.{decimals}f} ns"