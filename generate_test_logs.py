#!/usr/bin/env python3
"""
Test script to generate sample log lines for testing LogWatcher.
"""
import os
import time
import random
import argparse
from pathlib import Path
from datetime import datetime

# Sample log messages
LOG_MESSAGES = [
    "INFO: Application started successfully",
    "DEBUG: Processing data batch #123",
    "INFO: User login successful: user123",
    "WARNING: High memory usage detected (85%)",
    "ERROR: Failed to connect to database",
    "EXCEPTION: java.lang.NullPointerException",
    "FATAL: System crashed unexpectedly",
    "ERROR: Timeout waiting for response from API",
    "WARNING: API rate limit reached",
    "DEBUG: Retrying connection (attempt 3/5)",
    "CRITICAL: Disk space below 5%",
    "INFO: Backup completed successfully",
    "ERROR: Invalid configuration parameter: max_connections"
]

def generate_logs(log_path, interval=1.0, count=None):
    """Generate sample log entries."""
    path = Path(log_path)
    
    # Create directory if it doesn't exist
    path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating logs to {path}")
    
    i = 0
    try:
        while count is None or i < count:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = random.choice(LOG_MESSAGES)
            
            with path.open('a') as f:
                f.write(f"[{timestamp}] {message}\n")
                
            time.sleep(interval)
            i += 1
            
    except KeyboardInterrupt:
        print("\nStopped log generation")

def parse_args():
    parser = argparse.ArgumentParser(description='Generate sample log files for testing')
    parser.add_argument('-o', '--output', default='sample.log', help='Output log file')
    parser.add_argument('-i', '--interval', type=float, default=1.0, 
                        help='Interval between log entries (seconds)')
    parser.add_argument('-c', '--count', type=int, help='Number of log entries to generate')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    generate_logs(args.output, args.interval, args.count)
