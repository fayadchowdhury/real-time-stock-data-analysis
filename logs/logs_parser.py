import re

def parse_log(line):
    # Adjusted regex pattern to capture timestamp and message
    pattern = r'^(\S+\s\S+,\d+)\s+\w+\s+\w+\s+(.*)$'
    
    # Use regex to match the pattern
    match = re.match(pattern, line)
    
    if match:
        # Extract the timestamp and message
        timestamp = match.group(1)
        message = match.group(2)
        
        # Return parsed log data with only timestamp and message
        return {
            "timestamp": timestamp,
            "message": message
        }
    return None