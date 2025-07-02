#!/bin/bash
# Setup script for LogWatcher
# Quickly configures LogWatcher to monitor multiple log files

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Configuration
CONFIG_FILE="$SCRIPT_DIR/config.json"

# Function to show usage
show_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -l, --logs PATH1,PATH2,...     Comma-separated list of log files to watch"
    echo "  -p, --patterns TYPE:REGEX,...  Comma-separated list of error patterns (TYPE:REGEX format)"
    echo "  -c, --config PATH              Path to save the configuration (default: $CONFIG_FILE)"
    echo "  -h, --help                     Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 --logs /var/log/app1.log,/var/log/app2.log --patterns error:\"error|failed\",warning:\"warning|alert\""
    echo ""
    echo "You can also monitor logs directly:"
    echo "  $0 /var/log/app1.log /var/log/app2.log"
    exit 1
}

# Parse command line arguments
LOGS=""
PATTERNS=""
TEMP_CONFIG=$(mktemp)

# Check if direct log paths are provided
if [[ $# -gt 0 && ${1:0:1} != "-" ]]; then
    # Collect all arguments as log paths
    while [[ $# -gt 0 ]]; do
        if [[ ${1:0:1} == "-" ]]; then
            break
        fi
        if [ -z "$LOGS" ]; then
            LOGS="$1"
        else
            LOGS="$LOGS,$1"
        fi
        shift
    done
fi

# Parse remaining arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -l|--logs)
            # Поддержка пробелов и запятых: объединяем все аргументы до следующего ключа в одну строку
            shift
            LOGS=""
            while [[ $# -gt 0 && ${1:0:1} != "-" ]]; do
                if [ -z "$LOGS" ]; then
                    LOGS="$1"
                else
                    LOGS="$LOGS,$1"
                fi
                shift
            done
            ;;
        -p|--patterns)
            # Remove all spaces from the comma-separated list for consistent parsing
            PATTERNS=$(echo "$2" | tr -d ' ')
            shift
            shift
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift
            shift
            ;;
        -h|--help)
            show_usage
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            ;;
    esac
done

# Check if logs are specified
if [ -z "$LOGS" ]; then
    echo "Error: No log files specified"
    show_usage
fi

# Start building JSON configuration
echo "{" > "$TEMP_CONFIG"
echo "  \"logs\": [" >> "$TEMP_CONFIG"

# Add logs to configuration
IFS=',' read -ra LOG_ARRAY <<< "$LOGS"
FIRST_LOG=true
for log in "${LOG_ARRAY[@]}"; do
    name=$(basename "$log")
    name="${name%%.*}"
    
    # Add comma before all but first log entry
    if [ "$FIRST_LOG" = true ]; then
        FIRST_LOG=false
    else
        echo "," >> "$TEMP_CONFIG"
    fi
    
    # Add log entry with a warning if the file doesn't exist, but still include it
    if [ ! -f "$log" ]; then
        echo "Warning: File '$log' does not exist yet, but will be monitored when it appears" >&2
    fi
    cat >> "$TEMP_CONFIG" << EOF
    {
      "path": "$log",
      "name": "$name"
    }
EOF
done

# Close logs array
echo "  ]," >> "$TEMP_CONFIG"

# Start patterns object
echo "  \"patterns\": {" >> "$TEMP_CONFIG"

if [ -n "$PATTERNS" ]; then
    # Add custom patterns
    IFS=',' read -ra PATTERN_ARRAY <<< "$PATTERNS"
    FIRST_PATTERN=true
    for pattern_entry in "${PATTERN_ARRAY[@]}"; do
        type="${pattern_entry%%:*}"
        regex="${pattern_entry#*:}"
        # Remove quotes if present
        regex="${regex%\"}"
        regex="${regex#\"}"
        
        # Add comma before all but first pattern
        if [ "$FIRST_PATTERN" = true ]; then
            FIRST_PATTERN=false
        else
            echo "," >> "$TEMP_CONFIG"
        fi
        
        echo "    \"$type\": \"$regex\"" >> "$TEMP_CONFIG"
    done
else
    # Default patterns
    cat >> "$TEMP_CONFIG" << EOF
    "error": "error|fail(ed|ure)",
    "exception": "exception",
    "fatal": "fatal",
    "warning": "warning",
    "critical": "critical"
EOF
fi

# Close patterns object and main object
echo "  }" >> "$TEMP_CONFIG"
echo "}" >> "$TEMP_CONFIG"

# Move the temp config to the final location
mv "$TEMP_CONFIG" "$CONFIG_FILE"
echo "Configuration saved to $CONFIG_FILE"
echo "You can start monitoring with: ./watch_log.sh start"

exit 0
