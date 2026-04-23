import subprocess
import psutil
from datetime import datetime
import time
import logging
import threading
import sys

log = logging.getLogger(__name__)

def _start_proc(command: list):
    log.info("Starting process: %s", command)
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc

def monitor_process(command):
    log.info("Monitoring process: %s", command)
    stats = {
        'start_time': datetime.now(),
        'command': command,
        'check_times': [],
        'cpu_percent': [],
        'memory_info': [],
        'children': [],
        'threads': [],
    }
    proc = _start_proc(command)
    ps_proc = psutil.Process(proc.pid)
    log.debug("Subprocess started with PID %s", ps_proc.pid)

    stdout_chunks = []
    stderr_chunks = []

    def _forward_and_capture(stream, target, chunks):
        for chunk in iter(lambda: stream.read1(4096), b''):
            chunks.append(chunk)
            target.buffer.write(chunk)
            target.flush()
        stream.close()

    stdout_thread = threading.Thread(
        target=_forward_and_capture,
        args=(proc.stdout, sys.stdout, stdout_chunks),
        daemon=True,
    )
    stderr_thread = threading.Thread(
        target=_forward_and_capture,
        args=(proc.stderr, sys.stderr, stderr_chunks),
        daemon=True,
    )
    stdout_thread.start()
    stderr_thread.start()

    stats['pid'] = ps_proc.pid
    try:
        while ps_proc.is_running() and not ps_proc.status() == psutil.STATUS_ZOMBIE:
            try:
                cpu_percent = ps_proc.cpu_percent(interval=0.1)
                memory_info = ps_proc.memory_info()
                children = ps_proc.children(recursive=True)
                threads = ps_proc.threads()
                stats['cpu_percent'].append(cpu_percent)
                stats['memory_info'].append(memory_info)
                stats['children'].append(children)
                stats['threads'].append(threads)
                stats['check_times'].append(datetime.now())
                log.debug("Sampled stats at %s, CPU: %s%%, Memory: %s bytes, Children: %s, Threads: %s", stats['check_times'][-1], cpu_percent, memory_info.rss, len(children), len(threads))
            except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
                log.warning("Process ended or became inaccessible during monitoring.")
                break
            time.sleep(0.1)
        proc.wait()
        stdout_thread.join()
        stderr_thread.join()
        stats['stdout'] = b''.join(stdout_chunks).decode(errors='backslashreplace')
        stats['stderr'] = b''.join(stderr_chunks).decode(errors='backslashreplace')

    except Exception as e:
        log.warning("Exception during stat collection: %s", e)
    stats['end_time'] = datetime.now()
    stats['duration'] = stats['end_time'] - stats['start_time']
    log.info("Process monitoring complete. Duration: %s", stats['duration'])
    return stats
