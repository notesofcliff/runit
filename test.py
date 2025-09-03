import subprocess
import unittest
import tempfile
import os
import re

class TestRunitCLI(unittest.TestCase):
    """Integration tests for the runit CLI command."""

    def test_nonexistent_command(self):
        """Fails gracefully when a nonexistent command is run."""
        result = subprocess.run(['runit', 'nonexistent_command_12345'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue('error' in result.stderr.lower() or 'not found' in result.stderr.lower() or result.returncode != 0)

    def test_quick_exit_command(self):
        """Handles a process that exits almost instantly."""
        result = subprocess.run(['runit', 'python', '-c', 'pass'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('Command:', result.stdout)

    def test_output_file_overwrite(self):
        """Ensures output file is overwritten on repeated runs."""
        out_file = 'test_runit_out_overwrite.txt'
        try:
            for i in range(2):
                result = subprocess.run([
                    'runit', '--out-file', out_file, 'python', '-c', f'print({i})'
                ], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0)
            with open(out_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
            self.assertIn('Command:', file_content)
            self.assertIn('print(1)', file_content)
        finally:
            if os.path.exists(out_file):
                os.remove(out_file)

    def test_argument_parsing(self):
        """Checks that CLI options like log level and plot are parsed."""
        result = subprocess.run(['runit', '--log-level', 'DEBUG', '--plot', 'python', '-c', 'print(123)'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('Command:', result.stdout)

    def test_plotting_graceful_degradation(self):
        """Verifies plotting does not crash if plotext is missing."""
        result = subprocess.run(['runit', '--plot', 'python', '-c', 'print(123)'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('Command:', result.stdout)

    def test_no_arguments_prints_help(self):
        """Shows help when no arguments are provided."""
        result = subprocess.run(['runit'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertTrue('usage:' in result.stdout.lower() or 'usage:' in result.stderr.lower())

    def test_command_runs_and_reports(self):
        """Runs a command and checks for key report fields."""
        result = subprocess.run(['runit', 'python', '-c', 'print(123)'], capture_output=True, text=True)
        out = result.stdout
        self.assertEqual(result.returncode, 0)
        self.assertIn('Command:', out)
        self.assertIn('Start Time:', out)
        self.assertIn('End Time:', out)
        self.assertIn('Max RSS (bytes):', out)
        self.assertIn('Max Threads:', out)
        self.assertIn('Max Children:', out)
        self.assertIn('Samples:', out)

    def test_out_file_and_strip_ansi(self):
        """Checks --out-file and --strip-ansi produce plain text output."""
        out_file = 'test_runit_out.txt'
        try:
            result = subprocess.run([
                'runit', '--out-file', out_file, '--strip-ansi', 'python', '-c', 'print(123)'
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            # Output should be in terminal (stdout)
            self.assertIn('Command:', result.stdout)
            # File should exist and contain plain text
            with open(out_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
            self.assertIn('Command:', file_content)
            # Should not contain ANSI escape codes
            ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
            self.assertIsNone(ansi_escape.search(file_content))
        finally:
            if os.path.exists(out_file):
                os.remove(out_file)

class TestStatExtractors(unittest.TestCase):
    """Unit tests for stat extraction utility functions."""

    def test_strip_ansi(self):
        """Removes ANSI codes from a string as expected."""
        from runit.utils import strip_ansi
        ansi_text = '\x1b[31mRed\x1b[0m Normal \x1b[1;32mGreenBold\x1b[0m'
        plain = strip_ansi(ansi_text)
        self.assertIn('Red', plain)
        self.assertIn('Normal', plain)
        self.assertIn('GreenBold', plain)
        self.assertNotIn('\x1b', plain)

    def test_extract_memory_rss(self):
        """Extracts RSS values from memory info objects."""
        from runit.utils import extract_memory_rss
        class DummyMem:
            def __init__(self, rss): self.rss = rss
        mem_list = [DummyMem(100), DummyMem(200), DummyMem(150)]
        self.assertEqual(extract_memory_rss(mem_list), [100, 200, 150])

    def test_extract_num_threads(self):
        """Counts threads in each sample correctly."""
        from runit.utils import extract_num_threads
        threads_list = [[1,2,3], [1,2], []]
        self.assertEqual(extract_num_threads(threads_list), [3,2,0])

    def test_extract_num_children(self):
        """Counts child processes in each sample correctly."""
        from runit.utils import extract_num_children
        children_list = [[1], [], [1,2,3]]
        self.assertEqual(extract_num_children(children_list), [1,0,3])

class TestRunitAccuracy(unittest.TestCase):
    def test_child_process_monitoring(self):
        """Runs a command that spawns child processes and checks Max Children > 0."""
        code = "import subprocess; subprocess.run(['sleep', '5'])"
        result = subprocess.run(['runit', 'python', '-c', code], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('Max Children:', result.stdout)
        # Should be at least 1 child
        lines = result.stdout.splitlines()
        for line in lines:
            if line.strip().startswith('Max Children:'):
                val = int(line.split(':')[1].strip())
                self.assertGreaterEqual(val, 1)

    def test_long_running_command_sampling(self):
        """Runs a command that sleeps and checks for multiple samples."""
        result = subprocess.run(['runit', 'python', '-c', 'import time; time.sleep(2)'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('Samples:', result.stdout)
        # Should be more than 1 sample
        lines = result.stdout.splitlines()
        for line in lines:
            if line.strip().startswith('Samples:'):
                val = int(line.split(':')[1].strip())
                self.assertGreater(val, 1)

    def test_thread_count_accuracy(self):
        """Runs a command that spawns threads and checks Max Threads > 1."""
        code = "import time;import threading; [threading.Thread(target=lambda:time.sleep(1)).start() for _ in range(3)];"
        result = subprocess.run(['runit', 'python', '-c', code], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('Max Threads:', result.stdout)
        lines = result.stdout.splitlines()
        for line in lines:
            if line.strip().startswith('Max Threads:'):
                val = int(line.split(':')[1].strip())
                self.assertGreaterEqual(val, 3)

    def test_output_file_error_handling(self):
        """Tries to write to a read-only location and expects error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ro_dir = os.path.join(tmpdir, 'ro')
            os.mkdir(ro_dir)
            os.chmod(ro_dir, 0o555)  # read-only
            out_file = os.path.join(ro_dir, 'out.txt')
            result = subprocess.run(['runit', '--out-file', out_file, 'python', '-c', 'print(123)'], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue('error' in result.stderr.lower() or 'permission' in result.stderr.lower())

    def test_malformed_cli_arguments(self):
        """Passes invalid CLI options and checks for error/help output."""
        result = subprocess.run(['runit', '--not-an-option'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue('usage:' in result.stdout.lower() or 'usage:' in result.stderr.lower())

    def test_unicode_output_handling(self):
        """Runs a command that prints Unicode and checks report and output file."""
        out_file = 'test_runit_unicode.txt'
        try:
            result = subprocess.run(['runit', '--out-file', out_file, 'python', '-c', 'print("✓ ü ñ")'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertIn('✓', result.stdout)
            with open(out_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
            self.assertIn('✓', file_content)
        finally:
            if os.path.exists(out_file):
                os.remove(out_file)

    def test_resource_chart_output(self):
        """If plotext is installed, --plot should produce chart output."""
        # This test is best-effort: checks for chart-like output
        result = subprocess.run(['runit', '--plot', 'python', '-c', 'import time; time.sleep(1)'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        # Look for plotext chart markers (e.g., 'CPU Usage', 'Memory Usage')
        self.assertTrue(r'CPU % over time' in result.stdout or 'RSS (MB) over time' in result.stdout or 'plotext' in result.stdout)

if __name__ == '__main__':
    unittest.main()
