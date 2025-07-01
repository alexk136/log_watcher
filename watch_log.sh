#!/bin/bash
# Production script for running LogWatcher
# This script starts LogWatcher as a background process with logging
# and can be set up to run on system startup

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Configuration
CONFIG_FILE="$SCRIPT_DIR/config.json"  # Path to the config file
LOG_DIR="$SCRIPT_DIR/logs"             # Directory for LogWatcher's own logs
LOG_FILE="$LOG_DIR/logwatcher.log"     # Log file for LogWatcher output
PID_FILE="$SCRIPT_DIR/logwatcher.pid"  # PID file to track the running process

# Create necessary directories
mkdir -p "$LOG_DIR"

# Function to check if LogWatcher is already running
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0  # Running
        else
            return 1  # Not running but PID file exists
        fi
    else
        return 1  # Not running
    fi
}

# Function to start LogWatcher
start_watcher() {
    echo "Starting LogWatcher..."
    
    # Check if already running
    if is_running; then
        echo "LogWatcher is already running with PID $(cat "$PID_FILE")"
        return 1
    fi
    
    # Start the watcher in background
    nohup /usr/bin/python "$SCRIPT_DIR/logwatcher.py" -c "$CONFIG_FILE" >> "$LOG_FILE" 2>&1 &
    
    # Save PID
    PID=$!
    echo $PID > "$PID_FILE"
    
    echo "LogWatcher started with PID $PID"
    echo "Output is being logged to $LOG_FILE"
    return 0
}

# Function to stop LogWatcher
stop_watcher() {
    echo "Stopping LogWatcher..."
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Sending SIGTERM to process $PID"
            kill "$PID"
            
            # Wait for the process to terminate
            COUNTER=0
            while ps -p "$PID" > /dev/null 2>&1; do
                sleep 1
                COUNTER=$((COUNTER + 1))
                
                # If it takes more than 10 seconds, force kill
                if [ "$COUNTER" -ge 10 ]; then
                    echo "Force killing process $PID"
                    kill -9 "$PID" 2>/dev/null
                    break
                fi
            done
            
            echo "LogWatcher stopped"
        else
            echo "Process $PID does not exist"
        fi
        
        # Remove PID file
        rm -f "$PID_FILE"
    else
        echo "LogWatcher is not running"
    fi
}

# Function to restart LogWatcher
restart_watcher() {
    stop_watcher
    sleep 2
    start_watcher
}

# Function to check status
status_watcher() {
    if is_running; then
        echo "LogWatcher is running with PID $(cat "$PID_FILE")"
        echo "Log file: $LOG_FILE"
        
        # Print the last 5 lines of log
        echo "Recent log entries:"
        tail -5 "$LOG_FILE" 2>/dev/null || echo "No logs available yet"
    else
        echo "LogWatcher is not running"
    fi
}

# Parse command line arguments
case "$1" in
    start)
        start_watcher
        ;;
    stop)
        stop_watcher
        ;;
    restart)
        restart_watcher
        ;;
    status)
        status_watcher
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0
