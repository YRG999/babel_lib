
from datetime import datetime, timezone, timedelta

def extract_message(data):
    message_runs = data.get('message', {}).get('runs', [])
    return next((run.get('text', '') for run in message_runs if 'text' in run), '')

def extract_emoji(data):
    message_runs = data.get('message', {}).get('runs', [])
    return next((run.get('emoji', {}).get('emojiId', '') for run in message_runs if 'emoji' in run), '')

def extract_authorname(data):
    return data.get('authorName', {}).get('simpleText', '')

def extract_timestamp(data):
    return int(data.get('timestampUsec', '0')) // 1000000  # Convert microsecond timestamp to second

def convert_to_eastern(timestamp):
    utc_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    eastern = timezone(timedelta(hours=-5))
    return utc_time.astimezone(eastern)
