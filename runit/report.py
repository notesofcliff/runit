from .utils import extract_memory_rss, extract_num_threads, extract_num_children
import logging

log = logging.getLogger(__name__)

def format_report(stats):
    log.info("Formatting report.")
    rss_values = extract_memory_rss(stats['memory_info'])
    num_threads = extract_num_threads(stats['threads'])
    num_children = extract_num_children(stats['children'])
    report = [
        f"Command: {stats['command']}",
        f"PID: {stats.get('pid')}",
        f"Start Time: {stats['start_time']}",
        f"End Time: {stats['end_time']}",
        f"Duration: {stats['duration']}",
        f"Max RSS (bytes): {max(rss_values) if rss_values else 'N/A'}",
        f"Max Threads: {max(num_threads) if num_threads else 'N/A'}",
        f"Max Children: {max(num_children) if num_children else 'N/A'}",
        f"Samples: {len(stats['check_times'])}",
        f"\nstdout: \n\n\t{'\n\t'.join(stats['stdout'].splitlines()) if stats['stdout'] else 'N/A'}",
        f"\nstderr: \n\n\t{'\n\t'.join(stats['stderr'].splitlines()) if stats['stderr'] else 'N/A'}",

    ]
    return "\n=== runit report ===\n" + "\n".join(report)
