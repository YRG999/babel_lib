import emoji
from datetime import datetime, timezone, timedelta

def extract_authorname(data):
    return data.get('authorName', {}).get('simpleText', '')

def extract_timestamp(data):
    return int(data.get('timestampUsec', '0')) // 1000000  # Convert microsecond timestamp to second

def convert_to_eastern(timestamp):
    utc_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    eastern = timezone(timedelta(hours=-5))
    return utc_time.astimezone(eastern)

def is_emoji(s):
    """Check if the input string is an emoji using the emoji library."""
    return emoji.emoji_count(s) == 1

def extract_text_and_emoji(data):
    """Extract text emoji or shortcut. Check valid emoji using the emoji library."""
    # Extracting the message runs
    message_runs = data.get('message', {}).get('runs', [])

    # Initializing an empty list to store the extracted elements
    output_elements = []
    
    # Looping through the message runs to extract text, valid emojiId, or the first shortcut
    for run in message_runs:
        if 'text' in run:
            output_elements.append(run['text'])
        elif 'emoji' in run:
            # Check if the emojiId is an actual emoji using the updated function
            if 'emojiId' in run['emoji'] and is_emoji(run['emoji']['emojiId']):
                output_elements.append(run['emoji']['emojiId'])
            # If emojiId isn't present or isn't valid, attempt to extract the first shortcut
            elif 'shortcuts' in run['emoji']:
                output_elements.append(run['emoji']['shortcuts'][0])
            else:
                # This is just a placeholder in case both are missing
                output_elements.append("[Unknown]")
    
    # Joining the extracted elements with spaces
    return ' '.join(output_elements)