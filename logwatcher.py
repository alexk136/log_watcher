#!/usr/bin/env python3
"""
Asynchronous Log Watcher - monitors multiple log files for errors and outputs them with highlighting.
"""
import asyncio
import re
import argparse
import sys
import os
import json
import signal
import atexit
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Color mappings for different error types
ERROR_COLORS = {
    "error": Fore.RED,
    "exception": Fore.MAGENTA,
    "fatal": Fore.YELLOW,
    "warning": Fore.CYAN,
    "default": Fore.WHITE,
}


class LogWatcher:
    def __init__(self, config_path=None):
        """Initialize the LogWatcher with the given configuration."""
        self.config = self._load_config(config_path)
        self.error_patterns = self._compile_patterns(self.config.get("patterns", {}))
        self.exclude_patterns = self._compile_exclude_patterns(
            self.config.get("exclude", [])
        )
        self.logs = self.config.get("logs", [])
        self.tasks = []

    def _load_config(self, config_path):
        """Load configuration from JSON file."""
        default_config = {
            "logs": [],
            "patterns": {
                "error": r"error",
                "exception": r"exception",
                "fatal": r"fatal",
                "warning": r"warning",
            },
            "exclude": [],
        }

        if not config_path:
            return default_config

        path = Path(config_path)
        if not path.exists():
            print(f"{Fore.RED}Config file not found: {config_path}{Style.RESET_ALL}")
            return default_config

        try:
            with path.open("r", encoding="utf-8") as f:
                if path.suffix.lower() == ".json":
                    return json.load(f) or default_config
                else:
                    print(
                        f"{Fore.RED}Unsupported config format: {path.suffix}, expected .json{Style.RESET_ALL}"
                    )
                    return default_config
        except Exception as e:
            print(f"{Fore.RED}Failed to load config: {str(e)}{Style.RESET_ALL}")
            return default_config

    def _compile_patterns(self, patterns_dict):
        """Compile regex patterns from the configuration."""
        compiled_patterns = {}
        for error_type, pattern in patterns_dict.items():
            try:
                compiled_patterns[error_type] = re.compile(pattern, re.IGNORECASE)
            except re.error:
                print(
                    f"{Fore.RED}Invalid regex pattern for {error_type}: {pattern}{Style.RESET_ALL}"
                )
        return compiled_patterns

    def _compile_exclude_patterns(self, exclude_list):
        """Compile exclude regex patterns from the configuration."""
        compiled_exclude = []
        for pattern in exclude_list:
            try:
                compiled_exclude.append(re.compile(pattern, re.IGNORECASE))
            except re.error:
                print(
                    f"{Fore.RED}Invalid exclude regex pattern: {pattern}{Style.RESET_ALL}"
                )
        return compiled_exclude

    async def tail_log(self, log_info):
        """Watch a log file for new lines and check for errors."""
        file_path = log_info["path"]
        log_name = log_info.get("name", os.path.basename(file_path))

        path = Path(file_path)
        
        # Wait for the file to appear if it doesn't exist
        while not path.exists():
            await asyncio.sleep(2)  # Check every 2 seconds
        
        print(
            f"{Fore.GREEN}Started watching: {log_name} ({file_path}){Style.RESET_ALL}"
        )

        try:
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                # Move to the end of file
                f.seek(0, 2)

                while True:
                    line = f.readline()
                    if not line:
                        await asyncio.sleep(0.2)
                        continue

                    self._process_line(line, log_name)
        except Exception as e:
            print(f"{Fore.RED}Error watching {log_name}: {str(e)}{Style.RESET_ALL}")

    def _process_line(self, line, log_name):
        """Process a log line and check for error patterns."""
        line = line.strip()

        # Check if line should be excluded
        for exclude_pattern in self.exclude_patterns:
            if exclude_pattern.search(line):
                return  # Skip this line

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for error_type, pattern in self.error_patterns.items():
            match = pattern.search(line)
            if match:
                color = ERROR_COLORS.get(error_type.lower(), ERROR_COLORS["default"])
                highlighted_line = pattern.sub(
                    lambda m: f"{color}{m.group(0)}{Style.RESET_ALL}", line
                )
                print(
                    f"[{timestamp}] {Fore.GREEN}{log_name}{Style.RESET_ALL} "
                    f"[{color}{error_type.upper()}{Style.RESET_ALL}]: {highlighted_line}"
                )
                return

    async def start(self):
        """Start watching all configured log files."""
        if not self.logs:
            print(f"{Fore.RED}No log files configured.{Style.RESET_ALL}")
            return

        self.tasks = [asyncio.create_task(self.tail_log(log)) for log in self.logs]

        await asyncio.gather(*self.tasks)

    def stop(self):
        """Stop all running tasks and clean up resources."""
        print(f"{Fore.CYAN}Stopping all log watchers...{Style.RESET_ALL}")
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Короткая пауза для завершения задач
        print(f"{Fore.CYAN}Cleanup complete.{Style.RESET_ALL}")


def parse_arguments():
    """Parse command line arguments."""
    # Get script directory for default config path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_config = os.path.join(script_dir, "config.json")

    parser = argparse.ArgumentParser(description="Asynchronous Log Watcher")
    parser.add_argument(
        "-c",
        "--config",
        default=default_config,
        help="Path to configuration file JSON",
    )
    parser.add_argument("-l", "--logs", nargs="+", help="List of log files to watch")
    return parser.parse_args()


async def main():
    args = parse_arguments()

    # Create a configuration if logs are provided via command line
    if args.logs and not args.config:
        config = {
            "logs": [
                {"path": path, "name": os.path.basename(path)} for path in args.logs
            ]
        }
        watcher = LogWatcher()
        watcher.logs = config["logs"]
    else:
        watcher = LogWatcher(args.config)

    try:
        await watcher.start()
    except KeyboardInterrupt:
        print(f"\n{Fore.CYAN}Stopping log watcher (Ctrl+C received)...{Style.RESET_ALL}")
        watcher.stop()
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        return 1

    return 0


if __name__ == "__main__":
    # Register handler for normal exit
    atexit.register(lambda: print(f"{Fore.CYAN}Log watcher exited.{Style.RESET_ALL}"))
    
    # Register signal handlers for graceful shutdown
    if hasattr(signal, 'SIGINT'):  # For handling Ctrl+C
        signal.signal(signal.SIGINT, lambda signum, frame: print(f"\n{Fore.CYAN}Received Ctrl+C, shutting down gracefully...{Style.RESET_ALL}"))
    
    if hasattr(signal, 'SIGTERM'):  # For handling termination signal (e.g., from systemd)
        signal.signal(signal.SIGTERM, lambda signum, frame: print(f"\n{Fore.CYAN}Received termination signal, shutting down gracefully...{Style.RESET_ALL}"))
    
    sys.exit(asyncio.run(main()))
