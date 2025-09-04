import re
import logging
from ast import literal_eval

log = logging.getLogger(__name__)

def strip_ansi(text):
    """Remove ANSI escape sequences from text."""
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def extract_memory_rss(memory_info_list):
    log.debug("Extracting memory RSS values.")
    rss_values = []
    for mem in memory_info_list:
        try:
            if isinstance(mem, str):
                mem = literal_eval(mem)
            rss = getattr(mem, 'rss', None)
            if rss is not None:
                rss_values.append(rss)
        except Exception:
            log.debug("Failed to extract RSS from memory info entry.")
            continue
    return rss_values

def extract_num_threads(threads_list):
    log.debug("Extracting number of threads per sample.")
    return [len(t) if hasattr(t, '__len__') else 0 for t in threads_list]

def extract_num_children(children_list):
    log.debug("Extracting number of children per sample.")
    return [len(c) if hasattr(c, '__len__') else 0 for c in children_list]
