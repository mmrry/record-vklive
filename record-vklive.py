import argparse
import time
from datetime import datetime

import yt_dlp
from yt_dlp.utils import DownloadError

URL_TEMPLATE = "https://live.vkvideo.ru/{channel}"

YDL_OPTS = {
    # Template file name; %(title).150B  - 150 bytes for NTFS / ext4 / APFS
    "outtmpl": "%(title).150B [%(id)s].%(ext)s",

    # yt-dlp use stromg wimdows filenames rules
    "windowsfilenames": True,

    # restrictfilenames=True -  if neeed - only ASCII
    "restrictfilenames": False,

    # Trim filename if path long
    "trim_file_name": 240,

    "noprogress": False,
    "quiet": False,
    "no_warnings": False,
    "continuedl": True,
}

def ts() -> str:
    return datetime.now().strftime("%H:%M:%S")

def try_download(url: str) -> int:
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            return ydl.download([url])
    except DownloadError as e:
        print(f"[{ts()}] yt-dlp: {e}")
        return 1
    except Exception as e:
        print(f"[{ts()}] Exception: {e!r}")
        return 2

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Waiting for stream live.vkvideo.ru and record witj yt-dlp."
    )
    p.add_argument(
        "channel",
        help="Channel name (part after live.vkvideo.ru/)",
    )
    p.add_argument("--wait-offline", type=int, default=5,
                   help="How many seconds wait, if channel offline (5)")
    p.add_argument("--wait-after", type=int, default=10,
                   help="How mane seconds wait if record stop (10)")
    return p.parse_args()

def main() -> None:
    args = parse_args()
    channel = args.channel.rstrip("/").split("/")[-1]
    url = URL_TEMPLATE.format(channel=channel)

    print(f"[{ts()}] Watching '{channel}' -> {url}")

    while True:
        print(f"[{ts()}] Checking {url} ...")
        try:
            rc = try_download(url)
        except KeyboardInterrupt:
            print(f"\n[{ts()}] User stopped.")
            return

        if rc == 0:
            print(f"[{ts()}] Record finished. Waiting {args.wait_after} c.")
            sleep_for = args.wait_after
        else:
            print(f"[{ts()}] Offline (код {rc}). Waiting {args.wait_offline} c.")
            sleep_for = args.wait_offline

        try:
            time.sleep(sleep_for)
        except KeyboardInterrupt:
            print(f"\n[{ts()}] User stopped.")
            return

if __name__ == "__main__":
    main()
