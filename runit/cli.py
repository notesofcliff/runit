import sys
from .monitor import monitor_process
from .report import format_report
from .plotting import plot_charts
from .utils import strip_ansi
from .logging_config import setup_logging
import argparse
import logging
from io import StringIO


def run_cli():
    parser = create_parser()
    args = parser.parse_args()
    setup_logging(args.log_level)
    log = logging.getLogger(__name__)
    log.info("Starting runit CLI")
    if not args.command:
        parser.print_help()
        log.info("No command provided. Exiting.")
        return
    orig_stdout = sys.stdout
    buf = None
    if args.out_file:
        buf = StringIO()
        sys.stdout = buf
        log.info("Capturing output to buffer for file: %s", args.out_file)
    stats = monitor_process(args.command)
    report = format_report(stats)
    if args.plot:
        plot_charts(stats)
    print(report)
    if args.out_file:
        sys.stdout = orig_stdout
        output = buf.getvalue()
        print(output, end='')
        file_output = output
        if getattr(args, 'strip_ansi', False):
            log.info("Stripping ANSI codes for output file.")
            file_output = strip_ansi(output)
        with open(args.out_file, 'w', encoding='utf-8') as f:
            f.write(file_output)
        log.info("Wrote output to file: %s", args.out_file)
    log.info("runit CLI finished.")

def create_parser():
    parser = argparse.ArgumentParser(
        description="Run a command and report on its execution (time, resources, etc)."
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set the logging level (default: INFO)'
    )
    parser.add_argument(
        '--out-file',
        type=str,
        default=None,
        help='Write the text report to this file instead of stdout.'
    )
    parser.add_argument(
        '--strip-ansi',
        action='store_true',
        help='Remove ANSI escape codes from output (for plain text files).'
    )
    parser.add_argument(
        '--plot',
        action='store_true',
        help='Show resource usage charts (requires plotext).'
    )
    parser.add_argument(
        'command',
        nargs=argparse.REMAINDER,
        help='The command and arguments to run.'
    )
    return parser
