import tracemalloc


class MemoryUsage:
    def start(self) -> None:
        tracemalloc.start()

    def stop(self) -> tuple[float, float]:
        """Stop tracking and return (current, peak) in MB."""
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return self.to_mb(current), self.to_mb(peak)

    @staticmethod
    def to_mb(size: float) -> float:
        return size / 1024 / 1024