#!/bin/bash
# Test script to demonstrate LogWatcher functionality

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create test directory
mkdir -p "$SCRIPT_DIR/test_logs"

# Start generating logs in the background
echo "Starting log generators..."
/usr/bin/python "$SCRIPT_DIR/generate_test_logs.py" -o "$SCRIPT_DIR/test_logs/app1.log" -i 0.5 &
PID1=$!
/usr/bin/python "$SCRIPT_DIR/generate_test_logs.py" -o "$SCRIPT_DIR/test_logs/app2.log" -i 0.7 &
PID2=$!

# Give the generators a moment to create some initial data
sleep 2

# Start the log watcher
echo "Starting LogWatcher..."
/usr/bin/python "$SCRIPT_DIR/logwatcher.py" -c "$SCRIPT_DIR/test_config.json"

# Clean up (this will run when the user terminates LogWatcher with Ctrl+C)
echo "Cleaning up..."
kill $PID1 $PID2 2>/dev/null
echo "Done!"
