def extract_text_and_emoji(chat_renderer):
    message = chat_renderer.get('message', {}).get('runs', [])
    return ''.join([run.get('text', '') for run in message])

def extract_timestamp(chat_renderer):
    timestamp = chat_renderer.get('timestamp', {}).get('simpleText', '')
    return float(timestamp) if timestamp.isdigit() else 0.0