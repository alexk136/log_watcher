#!/usr/bin/env python3
"""
Test script to demonstrate exclude functionality
"""
import time
import random

# Create test log entries with some deprecated warnings
test_entries = [
    "INFO: Application started successfully",
    "ERROR: Database connection failed",
    "WARNING: Deprecated function used in module X",
    "FATAL: Critical system failure",
    "DEBUG: Processing user request",
    "ERROR: File not found: config.xml",
    "WARNING: This method is deprecated and will be removed",
    "EXCEPTION: NullPointerException in handler",
    "DEBUG: Cache miss for key: user_123",
    "ERROR: Authentication failed for user admin",
]

if __name__ == "__main__":
    print("Generating test log entries...")
    for i in range(20):
        entry = random.choice(test_entries)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {entry}")
        time.sleep(1)
