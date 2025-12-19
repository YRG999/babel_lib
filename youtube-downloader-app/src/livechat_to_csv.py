import json
import csv
from datetime import datetime

BASE_STREAM_TS_USEC = None


def _update_base_timestamp(ts_usec, offset_msec):
    global BASE_STREAM_TS_USEC
    if not ts_usec or offset_msec is None:
        return
    try:
        base_candidate = int(ts_usec) - int(offset_msec) * 1000
    except (ValueError, TypeError):
        return
    if base_candidate <= 0:
        return
    if BASE_STREAM_TS_USEC is None or base_candidate < BASE_STREAM_TS_USEC:
        BASE_STREAM_TS_USEC = base_candidate

def extract_message_info(obj):
    """
    Extracts info from a single chat JSON object.
    Returns a dict with keys: timestamp, author, message, type, amount, currency, extra, role.
    """
    try:
        offset_msec = obj.get('replayChatItemAction', {}).get('videoOffsetTimeMsec')
        actions = obj.get('replayChatItemAction', {}).get('actions', [])
        for action in actions:
            add_action = action.get('addChatItemAction')
            if not add_action:
                continue
            item = add_action.get('item', {})
            _update_base_timestamp(action.get('timestampUsec') or obj.get('timestampUsec'), offset_msec)

            # Gift messages (e.g., Jewels purchases)
            gift = item.get('giftMessageViewModel')
            if gift:
                timestamp = ''
                if offset_msec is not None and BASE_STREAM_TS_USEC is not None:
                    try:
                        absolute_usec = BASE_STREAM_TS_USEC + int(offset_msec) * 1000
                        timestamp = datetime.fromtimestamp(absolute_usec / 1000000).strftime('%Y-%m-%d %H:%M:%S')
                    except (ValueError, TypeError, OSError):
                        timestamp = ''

                author = gift.get('authorName', {}).get('content', '').strip()
                message = gift.get('text', {}).get('content', '')
                role = ''
                for badge in gift.get('authorBadges', []):
                    badge_renderer = badge.get('liveChatAuthorBadgeRenderer', {})
                    badge_type = badge_renderer.get('icon', {}).get('iconType', '')
                    if badge_type in ['OWNER', 'MODERATOR']:
                        role = badge_type.lower()
                        break

                return {
                    'timestamp': timestamp,
                    'author': author,
                    'message': message,
                    'type': 'gift',
                    'amount': '',
                    'currency': '',
                    'extra': '',
                    'role': role
                }

            # Normal chat messages
            renderer = item.get('liveChatTextMessageRenderer')
            if renderer:
                ts_usec = renderer.get('timestampUsec')
                _update_base_timestamp(ts_usec, offset_msec)
                timestamp = datetime.fromtimestamp(int(ts_usec)//1000000).strftime('%Y-%m-%d %H:%M:%S') if ts_usec else ''
                author = renderer.get('authorName', {}).get('simpleText', '')
                
                # Extract message including emojis
                runs = renderer.get('message', {}).get('runs', [])
                message_parts = []
                for run in runs:
                    if 'text' in run:
                        message_parts.append(run['text'])
                    elif 'emoji' in run:
                        emoji = run['emoji']
                        emoji_text = emoji.get('image', {}).get('accessibility', {}).get('accessibilityData', {}).get('label', '')
                        if emoji_text:
                            message_parts.append(emoji_text)
                message = ''.join(message_parts)

                # Extract user role
                role = ''
                badges = renderer.get('authorBadges', [])
                for badge in badges:
                    badge_renderer = badge.get('liveChatAuthorBadgeRenderer', {})
                    badge_type = badge_renderer.get('icon', {}).get('iconType', '')
                    if badge_type in ['OWNER', 'MODERATOR']:
                        role = badge_type.lower()
                        break

                return {
                    'timestamp': timestamp,
                    'author': author,
                    'message': message,
                    'type': 'chat',
                    'amount': '',
                    'currency': '',
                    'extra': '',
                    'role': role
                }

            # Super Chat messages
            renderer = item.get('liveChatPaidMessageRenderer')
            if renderer:
                ts_usec = renderer.get('timestampUsec')
                _update_base_timestamp(ts_usec, offset_msec)
                timestamp = datetime.fromtimestamp(int(ts_usec)//1000000).strftime('%Y-%m-%d %H:%M:%S') if ts_usec else ''
                author = renderer.get('authorName', {}).get('simpleText', '')
                
                # Extract message including emojis
                runs = renderer.get('message', {}).get('runs', [])
                message_parts = []
                for run in runs:
                    if 'text' in run:
                        message_parts.append(run['text'])
                    elif 'emoji' in run:
                        emoji = run['emoji']
                        emoji_text = emoji.get('image', {}).get('accessibility', {}).get('accessibilityData', {}).get('label', '')
                        if emoji_text:
                            message_parts.append(emoji_text)
                message = ''.join(message_parts)
                
                amount = renderer.get('purchaseAmountText', {}).get('simpleText', '')
                role = ''
                badges = renderer.get('authorBadges', [])
                for badge in badges:
                    badge_renderer = badge.get('liveChatAuthorBadgeRenderer', {})
                    badge_type = badge_renderer.get('icon', {}).get('iconType', '')
                    if badge_type in ['OWNER', 'MODERATOR']:
                        role = badge_type.lower()
                        break

                return {
                    'timestamp': timestamp,
                    'author': author,
                    'message': message,
                    'type': 'superchat',
                    'amount': amount,
                    'currency': '',
                    'extra': '',
                    'role': role
                }

            # Memberships
            renderer = item.get('liveChatMembershipItemRenderer')
            if renderer:
                ts_usec = renderer.get('timestampUsec')
                _update_base_timestamp(ts_usec, offset_msec)
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
                _update_base_timestamp(ts_usec, offset_msec)
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
                _update_base_timestamp(ts_usec, offset_msec)
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
                _update_base_timestamp(ts_usec, offset_msec)
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

    except Exception as e:
        print(f"Error processing message: {e}")
        pass
    return None

def livechat_json_to_csv(json_file_path, csv_file_path):
    global BASE_STREAM_TS_USEC
    BASE_STREAM_TS_USEC = None
    with open(json_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['timestamp', 'author', 'message', 'type', 'amount', 'currency', 'extra', 'role']
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