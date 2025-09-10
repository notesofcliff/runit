# runit

A Python CLI tool to execute, monitor, and profile and visualize commands.

## Project Purpose

This project was created to prove that advanced functionality is absolutely possible in the terminal. `runit` showcases real-time monitoring of child processes, delivers detailed resource reports, and is built with a strong emphasis on robust, well-tested code. The goal: bring a modern, delightful CLI experience to profiling command execution with charts and everything.

## License

GPL v3. Please see the LICENSE file in the root of the repo for details.

## Features

- Utilizes [psutil](https://pypi.org/project/psutil/) for advanced resource tracking
- Reports execution time, system resource usage, threads, and child processes (including monitoring of all children)
- Terminal charts displaying CPU and memory usage
- Well tested

## Demo

See `runit` in action:

![runit demo](assets/runit-demo.gif)

## Requirements
* Python 3.9+
* psutil
* plotext

## Installation

Clone this repository and install with pip:

```sh
git clone https://github.com/notesofcliff/runit.git
cd runit
python -m venv .venv
source .venv/bin/activate  # Or (for Windows) .venv/Scripts/activate
pip install -e .
# Optionally run the tests
python test.py

```

Or, install directly from GitHub:

```sh
pip install git+https://github.com/notesofcliff/runit.git
```

After installation, use `runit` to run and analyze any command:

```sh
runit [args...] <command>
```

For example:

```sh
runit echo hello world
```

* If you run `runit` with no arguments, it will print help.

You'll receive a detailed resource usage report.

If [plotext](https://pypi.org/project/plotext/) is installed and `--plot` is specified, terminal charts for CPU and memory usage over time will be displayed.

* Charts appear only if the child process runs long enough to gather data.

## Example Output

```shell
=== runit report ===
Command: ['python', '-c', 'print(123)']
PID: 12345
Start Time: 2025-07-31 12:00:00.000000
End Time: 2025-07-31 12:00:01.000000
Duration: 0:00:01
Max RSS (bytes): 12345678
Max Threads: 4
Max Children: 0
Samples: 10
```

If plotext is installed, you'll also see beautiful terminal charts for CPU and memory usage.

## Run the Benchmarks

To run the benchmarks:

```sh
runit python benchmark.py
```

## CLI Options

- `--log-level LEVEL`: Set the logging level (default: INFO)
- `--out-file FILE`: Write the report and charts to a file (output is also shown in the terminal)
- `--strip-ansi`: Remove ANSI escape codes from output file (for plain text files)
- `--plot`: If specified, attempt to plot CPU and memory usage
- `command`: The command to run and monitor

When using `--out-file`, the output is both displayed in the terminal and written to the file. For plain text (no colors or terminal formatting), simply add `--strip-ansi`.

```sh
runit --out-file out.txt --strip-ansi python benchmark.py
```

You'll see the report and charts in your terminal, and a plain text version in `out.txt`.

## Development & Extending

### Project Structure

The codebase is organized for clarity and extensibility:

```
runit/
├── __init__.py
├── cli.py             # CLI handling: argparse setup and entrypoint
├── monitor.py         # Process launching + stat collection logic
├── report.py          # Summary formatter (text output)
├── plotting.py        # CPU/memory plots via plotext
├── utils.py           # Reusable helpers (ANSI stripping, extractors)
└── logging_config.py  # Centralized logging setup
```

### How to Add Features or Extend

- **Add new measurements:**
  - Extend `monitor.py` to collect additional stats.
  - Add new extractors to `utils.py`.
- **Change reporting:**
  - Update or add new formatters in `report.py`.
- **Add new CLI options:**
  - Edit `cli.py` and its `create_parser()` function.
- **Add/modify plotting:**
  - Update `plotting.py` (plotting is optional and gracefully degrades if `plotext` is missing).
- **Logging:**
  - All modules use a named logger for granular control. Adjust logging config in `logging_config.py`.
runit --out-file out.txt --strip-ansi python benchmark.py

### Tips for Contributors

- Each module should do one thing (separation of concerns).
- Avoid global state; keep functions pure where possible.
- Add tests for new features in `test.py`.
- Use dependency injection for flexibility (e.g., pass formatters or flags).
- Optional features should degrade gracefully (never crash if a dependency is missing).
