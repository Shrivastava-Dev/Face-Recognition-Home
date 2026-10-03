import json
import os
from datetime import datetime

LOG_PATH = "database/activity_log.json"

def log_event(event_type, name=None, details=None):
    """
    Logs an event to our activity history.
    event_type options: "face_recognized", "new_registration", "appliance_action"
    """
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event_type": event_type,
        "name": name,
        "details": details
    }
    
    logs = load_logs()
    logs.append(entry)
    
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, 'w') as f:
        json.dump(logs, f, indent=2)
    
    return entry

def load_logs():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, 'r') as f:
            return json.load(f)
    return []