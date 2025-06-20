import json
import csv
from datetime import datetime

def extract_message_info(obj):
    """
    Extracts timestamp, author, and message from a single chat JSON object.
    Returns a tuple (timestamp, author, message) or None if not a chat message.
    """
    try:
        actions = obj.get('replayChatItemAction', {}).get('actions', [])
        for action in actions:
            add_action = action.get('addChatItemAction')
            if not add_action:
                continue
            item = add_action.get('item', {})
            # Handle liveChatTextMessageRenderer (normal chat messages)
            renderer = item.get('liveChatTextMessageRenderer')
            if renderer:
                # Timestamp
                ts_usec = renderer.get('timestampUsec')
                if ts_usec:
                    ts = datetime.fromtimestamp(int(ts_usec)//1000000)
                    timestamp = ts.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    timestamp = ''
                # Author
                author = renderer.get('authorName', {}).get('simpleText', '')
                # Message
                runs = renderer.get('message', {}).get('runs', [])
                message = ''.join([run.get('text', '') for run in runs])
                return (timestamp, author, message)
            # Handle liveChatViewerEngagementMessageRenderer (system messages)
            renderer = item.get('liveChatViewerEngagementMessageRenderer')
            if renderer:
                ts_usec = renderer.get('timestampUsec')
                if ts_usec:
                    ts = datetime.fromtimestamp(int(ts_usec)//1000000)
                    timestamp = ts.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    timestamp = ''
                author = '[SYSTEM]'
                runs = renderer.get('message', {}).get('runs', [])
                message = ''.join([run.get('text', '') for run in runs])
                return (timestamp, author, message)
    except Exception:
        pass
    return None

def livechat_json_to_csv(json_file_path, csv_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['timestamp', 'author', 'message']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for line in lines:
            if not line.strip():
                continue
            obj = json.loads(line)
            info = extract_message_info(obj)
            if info:
                writer.writerow({
                    'timestamp': info[0],
                    'author': info[1],
                    'message': info[2]
                })

if __name__ == '__main__':
    in_file = input("Enter path to live chat NDJSON file: ").strip()
    out_file = in_file.rsplit('.', 1)[0] + '_livechat.csv'
    livechat_json_to_csv(in_file, out_file)
    print(f"CSV saved to: {out_file}")