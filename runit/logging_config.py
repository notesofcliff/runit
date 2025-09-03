import logging
import sys

log = logging.getLogger(__name__)

def setup_logging(level):
    logging.basicConfig(
        level=getattr(logging, level),
        stream=sys.stderr,
        format='[%(levelname)s] %(name)s: %(message)s',
    )
    log.setLevel(getattr(logging, level))
