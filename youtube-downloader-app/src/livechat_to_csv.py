import json
import csv
from datetime import datetime

def extract_message_info(obj):
    """
    Extracts info from a single chat JSON object.
    Returns a dict with keys: timestamp, author, message, type, amount, currency, extra.
    """
    try:
        actions = obj.get('replayChatItemAction', {}).get('actions', [])
        for action in actions:
            add_action = action.get('addChatItemAction')
            if not add_action:
                continue
            item = add_action.get('item', {})

            # Normal chat messages
            renderer = item.get('liveChatTextMessageRenderer')
            if renderer:
                ts_usec = renderer.get('timestampUsec')
                timestamp = datetime.fromtimestamp(int(ts_usec)//1000000).strftime('%Y-%m-%d %H:%M:%S') if ts_usec else ''
                author = renderer.get('authorName', {}).get('simpleText', '')
                runs = renderer.get('message', {}).get('runs', [])
                message = ''.join([run.get('text', '') for run in runs])
                return {
                    'timestamp': timestamp,
                    'author': author,
                    'message': message,
                    'type': 'chat',
                    'amount': '',
                    'currency': '',
                    'extra': ''
                }

            # Super Chat messages
            renderer = item.get('liveChatPaidMessageRenderer')
            if renderer:
                ts_usec = renderer.get('timestampUsec')
                timestamp = datetime.fromtimestamp(int(ts_usec)//1000000).strftime('%Y-%m-%d %H:%M:%S') if ts_usec else ''
                author = renderer.get('authorName', {}).get('simpleText', '')
                runs = renderer.get('message', {}).get('runs', [])
                message = ''.join([run.get('text', '') for run in runs])
                amount = renderer.get('purchaseAmountText', {}).get('simpleText', '')
                currency = ''
                extra = ''
                return {
                    'timestamp': timestamp,
                    'author': author,
                    'message': message,
                    'type': 'superchat',
                    'amount': amount,
                    'currency': currency,
                    'extra': extra
                }

            # Memberships
            renderer = item.get('liveChatMembershipItemRenderer')
            if renderer:
                ts_usec = renderer.get('timestampUsec')
                timestamp = datetime.fromtimestamp(int(ts_usec)//1000000).strftime('%Y-%m-%d %H:%M:%S') if ts_usec else ''
                author = renderer.get('authorName', {}).get('simpleText', '')
                header = renderer.get('headerSubtext', {}).get('runs', [])
                message = ''.join([run.get('text', '') for run in header])
                extra = renderer.get('authorBadges', [{}])[0].get('tooltip', '')
                return {
                    'timestamp': timestamp,
                    'author': author,
                    'message': message,
                    'type': 'membership',
                    'amount': '',
                    'currency': '',
                    'extra': extra
                }

            # System/moderator messages
            renderer = item.get('liveChatViewerEngagementMessageRenderer')
            if renderer:
                ts_usec = renderer.get('timestampUsec')
                timestamp = datetime.fromtimestamp(int(ts_usec)//1000000).strftime('%Y-%m-%d %H:%M:%S') if ts_usec else ''
                author = '[SYSTEM]'
                runs = renderer.get('message', {}).get('runs', [])
                message = ''.join([run.get('text', '') for run in runs])
                return {
                    'timestamp': timestamp,
                    'author': author,
                    'message': message,
                    'type': 'system',
                    'amount': '',
                    'currency': '',
                    'extra': ''
                }

            # Stickers (Super Stickers)
            renderer = item.get('liveChatPaidStickerRenderer')
            if renderer:
                ts_usec = renderer.get('timestampUsec')
                timestamp = datetime.fromtimestamp(int(ts_usec)//1000000).strftime('%Y-%m-%d %H:%M:%S') if ts_usec else ''
                author = renderer.get('authorName', {}).get('simpleText', '')
                amount = renderer.get('purchaseAmountText', {}).get('simpleText', '')
                sticker = renderer.get('sticker', {}).get('accessibility', {}).get('accessibilityData', {}).get('label', '')
                return {
                    'timestamp': timestamp,
                    'author': author,
                    'message': '[STICKER] ' + sticker,
                    'type': 'supersticker',
                    'amount': amount,
                    'currency': '',
                    'extra': ''
                }

            # Moderation messages (e.g., deleted messages)
            renderer = item.get('liveChatTextMessageRenderer')
            if renderer and renderer.get('deletedState'):
                ts_usec = renderer.get('timestampUsec')
                timestamp = datetime.fromtimestamp(int(ts_usec)//1000000).strftime('%Y-%m-%d %H:%M:%S') if ts_usec else ''
                author = renderer.get('authorName', {}).get('simpleText', '')
                return {
                    'timestamp': timestamp,
                    'author': author,
                    'message': '[DELETED]',
                    'type': 'deleted',
                    'amount': '',
                    'currency': '',
                    'extra': ''
                }

    except Exception:
        pass
    return None

def livechat_json_to_csv(json_file_path, csv_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['timestamp', 'author', 'message', 'type', 'amount', 'currency', 'extra']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for line in lines:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue  # Skip lines that are not valid JSON
            info = extract_message_info(obj)
            if info:
                writer.writerow(info)

if __name__ == '__main__':
    in_file = input("Enter path to live chat NDJSON file: ").strip()
    out_file = in_file.rsplit('.', 1)[0] + '_livechat.csv'
    livechat_json_to_csv(in_file, out_file)
    print(f"CSV saved to: {out_file}")