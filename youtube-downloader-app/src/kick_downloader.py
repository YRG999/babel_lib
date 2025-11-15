from playwright.sync_api import sync_playwright, TimeoutError
import subprocess
import argparse
import sys
import shlex
import os
import configparser

PAGE_URL = "https://kick.com/PAGE"
M3U8_URL = "https://stream.kick.com/MEDIA/media/hls/master.m3u8"
OUTPUT = "output.mp4"

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

def main():
    parser = argparse.ArgumentParser(description="Download Kick master.m3u8 using Playwright + ffmpeg")
    parser.add_argument("--page", help="Kick page URL (page with the player)", default=PAGE_URL)
    parser.add_argument("--m3u8", help="master.m3u8 URL", default=M3U8_URL)
    parser.add_argument("--out", help="output file", default=OUTPUT)
    parser.add_argument("--headful", action="store_true", help="run browser headful (useful for login/verification)")
    parser.add_argument("--use-profile", action="store_true", help="use system Firefox profile (reuse logged-in session)")
    parser.add_argument("--profile-path", help="path to Firefox profile directory (overrides auto-detect)")
    parser.add_argument("--firefox-exec", help="path to Firefox executable (optional)")
    args = parser.parse_args()

    if not args.page or not args.m3u8:
        print("Provide --page and --m3u8 (or set PAGE_URL / M3U8_URL in the script).", file=sys.stderr)
        sys.exit(1)

    with sync_playwright() as p:
        used_persistent = False
        context = None
        browser = None
        if args.use_profile:
            profile_dir = args.profile_path or find_default_firefox_profile()
            if not profile_dir or not os.path.exists(profile_dir):
                print("Firefox profile not found. Pass --profile-path or ensure Firefox has a profile.", file=sys.stderr)
                sys.exit(1)
            exec_path = args.firefox_exec or find_firefox_exec()
            print(f"Launching persistent Firefox context using profile: {profile_dir}")
            # launch_persistent_context returns a BrowserContext
            context = p.firefox.launch_persistent_context(profile_dir, headless=not args.headful, executable_path=exec_path)
            used_persistent = True
        else:
            browser = p.firefox.launch(headless=not args.headful, executable_path=(args.firefox_exec or None))
            context = browser.new_context()

        page = context.new_page()
        print("Opening page to establish session / Cloudflare checks...")
        try:
            page.goto(args.page, wait_until="networkidle", timeout=60000)
        except TimeoutError:
            print("Page.goto timed out waiting for networkidle — retrying with 'load' and longer timeout.", file=sys.stderr)
            try:
                page.goto(args.page, wait_until="load", timeout=120000)
            except TimeoutError:
                print("Second attempt timed out. If Cloudflare requires interaction, run with --headful to complete verification.", file=sys.stderr)
                # close whichever we created
                if used_persistent:
                    context.close()
                else:
                    browser.close()
                sys.exit(1)
        # small wait to ensure any JS token fetches complete
        page.wait_for_timeout(1500)

        # If user requested headful mode, let them complete interactive verification (2FA/code)
        if args.headful:
            print()
            print("Headful mode: complete any login / verification (enter codes, solve captchas) in the opened browser.")
            print("When finished, return to this terminal and press Enter to continue.")
            try:
                input()
            except KeyboardInterrupt:
                print("Interrupted. Exiting.", file=sys.stderr)
                if used_persistent:
                    context.close()
                else:
                    browser.close()
                sys.exit(1)
            # reload page/context to ensure fresh cookies/tokens after manual login
            try:
                page.reload(wait_until="networkidle", timeout=30000)
            except TimeoutError:
                # fallback to load if networkidle hangs
                page.reload(wait_until="load", timeout=60000)

        # collect cookies for kick domains
        cookies = [c for c in context.cookies() if "kick.com" in c.get("domain", "")]
        cookie_str = build_cookie_string(cookies)
        # get browser UA from navigator
        user_agent = page.evaluate("() => navigator.userAgent")

        print("Sending a request for the m3u8 via the browser context to validate access...")
        # try fetching the m3u8 using Playwright's request (uses browser context)
        try:
            resp = page.request.get(args.m3u8, headers={"Referer": args.page})
        except Exception as e:
            print("Playwright request failed:", e, file=sys.stderr)
            if used_persistent:
                context.close()
            else:
                browser.close()
            sys.exit(1)

        if resp.status != 200:
            print(f"m3u8 fetch returned status {resp.status}. Proceeding to run ffmpeg may still fail.", file=sys.stderr)

        # build ffmpeg headers - lines must end with CRLF
        headers = f"User-Agent: {user_agent}\\r\\nReferer: {args.page}\\r\\nCookie: {cookie_str}\\r\\n"

        # run ffmpeg to download segments and mux to mp4 (copy streams)
        ffmpeg_cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "info",
            "-headers", headers,
            "-i", args.m3u8,
            "-c", "copy",
            args.out
        ]
        print("Running ffmpeg to download. Command:")
        print(" ".join(shlex.quote(x) for x in ffmpeg_cmd))
        try:
            subprocess.run(ffmpeg_cmd, check=True)
            print("Download complete:", args.out)
        except subprocess.CalledProcessError as e:
            print("ffmpeg failed, see output above.", file=sys.stderr)
            if used_persistent:
                context.close()
            else:
                browser.close()
            sys.exit(e.returncode)

        if used_persistent:
            context.close()
        else:
            browser.close()

if __name__ == "__main__":
    main()
