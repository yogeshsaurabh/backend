from datetime import datetime


def get_current_time():
    """Get current time in ISO format."""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
