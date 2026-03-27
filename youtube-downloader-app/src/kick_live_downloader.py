from playwright.sync_api import sync_playwright, TimeoutError
import subprocess
import argparse
import sys
import shlex
import os
import configparser

PAGE_URL = "https://kick.com/PAGE"
OUTPUT = "output.mp4"

M3U8_INTERCEPT_TIMEOUT_MS = 15000  # max wait for m3u8 to appear in network traffic


def build_cookie_string(cookies):
    parts = []
    for c in cookies:
        parts.append(f"{c['name']}={c['value']}")
    return "; ".join(parts)


def find_default_firefox_profile():
    ini = os.path.expanduser("~/Library/Application Support/Firefox/profiles.ini")
    if not os.path.exists(ini):
        return None
    cfg = configparser.RawConfigParser()
    cfg.read(ini)
    for section in cfg.sections():
        if cfg.has_option(section, "Default") and cfg.get(section, "Default") == "1":
            path = cfg.get(section, "Path", fallback=None)
            is_rel = cfg.get(section, "IsRelative", fallback="1")
            if not path:
                continue
            if is_rel == "1":
                return os.path.expanduser(f"~/Library/Application Support/Firefox/{path}")
            return path
    return None


def find_firefox_exec():
    common = [
        "/Applications/Firefox.app/Contents/MacOS/firefox",
        "/Applications/Firefox Nightly.app/Contents/MacOS/firefox",
        "/Applications/Firefox Developer Edition.app/Contents/MacOS/firefox",
    ]
    for p in common:
        if os.path.exists(p):
            return p
    return None


def download_kick_live(
    page_url,
    m3u8_url=None,
    out=OUTPUT,
    headful=False,
    use_profile=False,
    profile_path=None,
    firefox_exec=None,
):
    """Download a Kick live stream using Playwright + ffmpeg.

    If m3u8_url is None, the URL is auto-detected by intercepting network
    requests made by the Kick player after the page loads.

    Returns True on success, False on failure.
    """
    with sync_playwright() as p:
        used_persistent = False
        context = None
        browser = None

        if use_profile:
            profile_dir = profile_path or find_default_firefox_profile()
            if not profile_dir or not os.path.exists(profile_dir):
                print(
                    "Firefox profile not found. Pass profile_path or ensure Firefox has a profile.",
                    file=sys.stderr,
                )
                return False
            exec_path = firefox_exec or find_firefox_exec()
            print(f"Launching persistent Firefox context using profile: {profile_dir}")
            context = p.firefox.launch_persistent_context(
                profile_dir, headless=not headful, executable_path=exec_path
            )
            used_persistent = True
        else:
            browser = p.firefox.launch(
                headless=not headful, executable_path=(firefox_exec or None)
            )
            context = browser.new_context()

        def _close():
            if used_persistent:
                context.close()
            else:
                browser.close()

        # Set up m3u8 interception before navigating so no requests are missed.
        detected_m3u8 = {"url": m3u8_url}

        if detected_m3u8["url"] is None:
            def _on_request(request):
                if detected_m3u8["url"] is None and "master.m3u8" in request.url:
                    detected_m3u8["url"] = request.url
                    print(f"Detected m3u8: {request.url}")

            context.on("request", _on_request)

        page = context.new_page()
        print("Opening page to establish session / Cloudflare checks...")
        try:
            page.goto(page_url, wait_until="networkidle", timeout=60000)
        except TimeoutError:
            print(
                "Page.goto timed out waiting for networkidle — retrying with 'load' and longer timeout.",
                file=sys.stderr,
            )
            try:
                page.goto(page_url, wait_until="load", timeout=120000)
            except TimeoutError:
                print(
                    "Second attempt timed out. If Cloudflare requires interaction, run with --headful to complete verification.",
                    file=sys.stderr,
                )
                _close()
                return False

        # small wait to ensure any JS token fetches complete
        page.wait_for_timeout(1500)

        # If user requested headful mode, let them complete interactive verification (2FA/code)
        if headful:
            print()
            print("Headful mode: complete any login / verification (enter codes, solve captchas) in the opened browser.")
            print("When finished, return to this terminal and press Enter to continue.")
            try:
                input()
            except KeyboardInterrupt:
                print("Interrupted. Exiting.", file=sys.stderr)
                _close()
                return False
            # reload page/context to ensure fresh cookies/tokens after manual login
            try:
                page.reload(wait_until="networkidle", timeout=30000)
            except TimeoutError:
                page.reload(wait_until="load", timeout=60000)

        # If m3u8 was not captured yet, wait longer for the player to initialise.
        if detected_m3u8["url"] is None:
            print(
                f"Waiting up to {M3U8_INTERCEPT_TIMEOUT_MS // 1000}s for m3u8 URL in network traffic..."
            )
            page.wait_for_timeout(M3U8_INTERCEPT_TIMEOUT_MS)

        if detected_m3u8["url"] is None:
            print(
                "Could not auto-detect m3u8 URL. The stream may not be live, or Cloudflare "
                "is blocking the player. Try --headful, or supply the m3u8 URL manually with --m3u8.",
                file=sys.stderr,
            )
            _close()
            return False

        resolved_m3u8 = detected_m3u8["url"]

        # collect cookies for kick domains
        cookies = [c for c in context.cookies() if "kick.com" in c.get("domain", "")]
        cookie_str = build_cookie_string(cookies)
        # get browser UA from navigator
        user_agent = page.evaluate("() => navigator.userAgent")

        print("Sending a request for the m3u8 via the browser context to validate access...")
        try:
            resp = page.request.get(resolved_m3u8, headers={"Referer": page_url})
        except Exception as e:
            print("Playwright request failed:", e, file=sys.stderr)
            _close()
            return False

        if resp.status != 200:
            print(f"m3u8 fetch returned status {resp.status}. Proceeding to run ffmpeg may still fail.", file=sys.stderr)

        # build ffmpeg headers - lines must end with CRLF
        headers = f"User-Agent: {user_agent}\\r\\nReferer: {page_url}\\r\\nCookie: {cookie_str}\\r\\n"

        # run ffmpeg to download segments and mux to mp4 (copy streams)
        ffmpeg_cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "info",
            "-headers", headers,
            "-i", resolved_m3u8,
            "-c", "copy",
            out,
        ]
        print("Running ffmpeg to download. Command:")
        print(" ".join(shlex.quote(x) for x in ffmpeg_cmd))
        try:
            subprocess.run(ffmpeg_cmd, check=True)
            print("Download complete:", out)
            _close()
            return True
        except subprocess.CalledProcessError:
            print("ffmpeg failed, see output above.", file=sys.stderr)
            _close()
            return False


def main():
    parser = argparse.ArgumentParser(description="Download Kick live stream using Playwright + ffmpeg")
    parser.add_argument("--page", help="Kick page URL (page with the player)", default=PAGE_URL)
    parser.add_argument(
        "--m3u8",
        help="master.m3u8 URL (optional — auto-detected from network traffic if omitted)",
        default=None,
    )
    parser.add_argument("--out", help="output file", default=OUTPUT)
    parser.add_argument("--headful", action="store_true", help="run browser headful (useful for login/verification)")
    parser.add_argument("--use-profile", action="store_true", help="use system Firefox profile (reuse logged-in session)")
    parser.add_argument("--profile-path", help="path to Firefox profile directory (overrides auto-detect)")
    parser.add_argument("--firefox-exec", help="path to Firefox executable (optional)")
    args = parser.parse_args()

    if not args.page:
        print("Provide --page (or set PAGE_URL in the script).", file=sys.stderr)
        sys.exit(1)

    success = download_kick_live(
        page_url=args.page,
        m3u8_url=args.m3u8,
        out=args.out,
        headful=args.headful,
        use_profile=args.use_profile,
        profile_path=args.profile_path,
        firefox_exec=args.firefox_exec,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
