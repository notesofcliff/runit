import time
import gc
import threading
import multiprocessing
import math

def cpu_burst(duration=1.0):
    """Consume CPU for a given duration."""
    end = time.time() + duration
    x = 0.0
    while time.time() < end:
        x += math.sqrt(x + 1)

def allocate_memory(size_mb=100):
    """Allocate and free memory."""
    arr = [0.0] * (size_mb * 250_000)  # ~100MB
    time.sleep(1)
    del arr
    gc.collect()

def thread_task():
    cpu_burst(0.5)
    time.sleep(0.5)

def process_task():
    allocate_memory(50)
    cpu_burst(0.5)

def main():
    print("[Benchmark] Starting CPU burst...")
    cpu_burst(1)

    print("[Benchmark] Allocating memory...")
    allocate_memory(200)

    print("[Benchmark] Spawning threads...")
    threads = [threading.Thread(target=thread_task) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print("[Benchmark] Spawning child processes...")
    procs = [multiprocessing.Process(target=process_task) for _ in range(2)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()

    print("[Benchmark] Final CPU burst...")
    cpu_burst(1)

    print("[Benchmark] Benchmark complete.")

if __name__ == "__main__":
    main()
