# LogWatcher

Asynchronous log watcher that monitors multiple log files for errors and outputs them with highlighting.

## Features

- Asynchronous monitoring of multiple log files simultaneously
- "Tailing" log files to analyze only new lines (similar to `tail -F`)
- Searching for errors using regex patterns and keywords
- Console output with color highlighting for different error types
- Easy configuration via YAML or JSON files
- Command-line arguments for quick setup

## Requirements

- Python 3.7+
- Dependencies:
  - colorama

## Installation

```bash
# Clone the repository
git clone https://github.com/alexk136/log_watcher
cd LogWatcher

# Install dependencies
pip install colorama
```

## Usage

### Basic Usage

```bash
# Simple run (will automatically use config.json from the script's directory)
python logwatcher.py

# Using a specific configuration file
python logwatcher.py -c path/to/your/config.json

# Watching specific log files directly
python logwatcher.py -l /var/log/syslog /var/log/auth.log

# Using production script (for background operation)
./watch_log.sh start    # Start the log watcher as a background service
./watch_log.sh stop     # Stop the background service
./watch_log.sh restart  # Restart the service
./watch_log.sh status   # Check current status

# Quick setup for monitoring multiple logs
./setup_logs.sh --logs /var/log/app1.log,/var/log/app2.log
```

### Configuration

You can configure LogWatcher using a JSON configuration file:

**Configuration (config.json)**

```json
{
  "logs": [
    {
      "path": "/var/log/syslog",
      "name": "system"
    },
    {
      "path": "/var/log/auth.log",
      "name": "auth"
    }
  ],
  "patterns": {
    "error": "error|fail(ed|ure)",
    "exception": "exception",
    "fatal": "fatal",
    "warning": "warning"
  }
}
```

## Command Line Arguments

- `-c, --config`: Path to configuration file (YAML or JSON)
- `-l, --logs`: List of log files to watch (space-separated)

## Production Scripts

### watch_log.sh

A service control script for running LogWatcher in production environments:

- `./watch_log.sh start`: Start LogWatcher as a background service
- `./watch_log.sh stop`: Stop the running service
- `./watch_log.sh restart`: Restart the service
- `./watch_log.sh status`: Check status and show recent logs

The script handles PID management, logging, and clean shutdowns.

### setup_logs.sh

A utility script for quickly configuring log files to watch:

```bash
# Configure multiple log files at once
./setup_logs.sh --logs /path/to/log1.log,/path/to/log2.log

# Specify custom error patterns
./setup_logs.sh --logs /var/log/app.log --patterns error:"error|failed",critical:"urgent|critical"
```

### System Service

A systemd service definition is provided in `logwatcher.service`. Before installing, edit the file to set the correct paths:

```bash
# Edit the service file to set your actual installation path
# Replace %h/path/to/logwatcher with your actual path
nano logwatcher.service
```

Then install as a system service:

```bash
sudo cp logwatcher.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable logwatcher
sudo systemctl start logwatcher
```

## Features

- Color-coded output based on error type
- Timestamp for each error occurrence
- Automatic pattern matching with regex support
- Error type classification (ERROR, EXCEPTION, FATAL, etc.)
- Background operation with service management scripts
- System service integration
- Automatic failure recovery

## License

MIT
