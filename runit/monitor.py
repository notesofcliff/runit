import subprocess
import psutil
from datetime import datetime
import time
import logging

log = logging.getLogger(__name__)

def _start_proc(command: list):
    log.info(f"Starting process: {command}")
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc

def monitor_process(command):
    log.info(f"Monitoring process: {command}")
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
    log.debug(f"Subprocess started with PID {ps_proc.pid}")

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
                log.debug(f"Sampled stats at {stats['check_times'][-1]}, CPU: {cpu_percent}%, Memory: {memory_info.rss} bytes, Children: {len(children)}, Threads: {len(threads)}")
            except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
                log.warning("Process ended or became inaccessible during monitoring.")
                break
            time.sleep(0.1)
        stats['stdout'] = proc.stdout.read().decode()
        stats['stderr'] = proc.stderr.read().decode()

    except Exception as e:
        log.warning(f"Exception during stat collection: {e}")
    stats['end_time'] = datetime.now()
    stats['duration'] = stats['end_time'] - stats['start_time']
    log.info(f"Process monitoring complete. Duration: {stats['duration']}")
    return stats
