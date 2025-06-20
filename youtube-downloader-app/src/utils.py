def convert_to_eastern(timestamp: float) -> datetime:
    utc_time = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
    return utc_time.astimezone(pytz.timezone('US/Eastern'))

def get_user_input() -> tuple[str, bool, bool]:
    url = input("Please enter the full YouTube URL: ")
    use_cookies = input("Do you want to use cookies from the browser? (y/n): ").strip().lower() == 'y'
    download_comments = input("Do you want to download comments? (y/n): ").strip().lower() == 'y'
    return url, use_cookies, download_comments