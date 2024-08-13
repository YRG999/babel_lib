# extract_functions_new.py

import emoji
from typing import Dict, Any

def extract_authorname(data: Dict[str, Any]) -> str:
    return data.get('authorName', {}).get('simpleText', '')

def extract_timestamp(data: Dict[str, Any]) -> int:
    return int(data.get('timestampUsec', '0')) // 1000000

def is_emoji(s: str) -> bool:
    return emoji.emoji_count(s) == 1

def extract_text_and_emoji(data: Dict[str, Any]) -> str:
    message_runs = data.get('message', {}).get('runs', [])
    output_elements = []
    
    for run in message_runs:
        if 'text' in run:
            output_elements.append(run['text'])
        elif 'emoji' in run:
            if 'emojiId' in run['emoji'] and is_emoji(run['emoji']['emojiId']):
                output_elements.append(run['emoji']['emojiId'])
            elif 'shortcuts' in run['emoji']:
                output_elements.append(run['emoji']['shortcuts'][0])
            else:
                output_elements.append("[Unknown]")
    
    return ''.join(output_elements)
