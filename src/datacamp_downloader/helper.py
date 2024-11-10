import itertools
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

from termcolor import colored
from texttable import Texttable


class Logger:
    show_warnings = True
    is_writing = False

    @classmethod
    def error(cls, text):
        Logger.print(text, "ERROR:", "red")

    @classmethod
    def clear(cls):
        sys.stdout.write("\r" + " " * 100 + "\r")

    @classmethod
    def warning(cls, text):
        if cls.show_warnings:
            Logger.print(text, "WARNING:", "yellow")

    @classmethod
    def info(cls, text):
        Logger.print(text, "INFO:", "green")

    @classmethod
    def print(cls, text, head, color=None, background=None, end="\n"):
        cls.is_writing = True
        Logger.clear()
        print(colored(f"{head}", color, background), text, end=end, flush=True)
        cls.is_writing = False

    @classmethod
    def clear_and_print(cls, text):
        cls.is_writing = True
        Logger.clear()
        print(text, flush=True)
        cls.is_writing = False


def get_table():
    table = Texttable()
    return table


def animate_wait(f):
    done = False

    def animate():
        for c in itertools.cycle(list("/—\|")):
            if done:
                Logger.clear()
                break
            if not Logger.is_writing:
                print("\rPlease wait " + c, end="", flush=True)
            time.sleep(0.1)

    def wrapper(*args):
        nonlocal done
        done = False
        t = threading.Thread(target=animate)
        t.daemon = True
        t.start()
        output = f(*args)
        done = True
        return output

    return wrapper


def correct_path(path: str):
    return re.sub("[^-a-zA-Z0-9_.() /]+", "", path)


def download_file(link: str, path: Path, progress=True, max_retry=10, overwrite=False):
    aria2_tmp = path.parent / f"{path.name}.aria2"

    if not overwrite and not aria2_tmp.exists() and path.exists():
        Logger.warning(f"{path.name} is already downloaded")
        return

    path.parent.mkdir(exist_ok=True, parents=True)

    command = [
        "aria2c",
        link,
        "--dir",
        path.parent.as_posix(),
        "--out",
        path.name,
        f"--allow-overwrite={'true' if overwrite else 'false'}",
        "--console-log-level=warn",
        "--summary-interval=0",
        "--download-result=hide",
        "--auto-file-renaming=false",
        "--max-connection-per-server=5",
        "--min-split-size=1M",
    ]

    try:
        if progress:
            Logger.print(f"{path.name}", "[Downloading]", "blue", end="\n")
            subprocess.run(command, check=True)
        else:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
    except Exception:
        print("Failed to download video")

    if progress:
        sys.stdout.write("\n")


def print_progress(progress, total, name, max=50):
    done = int(max * progress / total)
    Logger.print(
        "[%s%s] %d%%" % ("=" * done, " " * (max - done), done * 2),
        f"Downloading [{name}]",
        "blue",
        end="\r",
    )
    sys.stdout.flush()


def save_text(path: Path, content: str, overwrite=False):
    if not path.is_file:
        Logger.error(f"{path.name} isn't a file")
        return
    if not overwrite and path.exists():
        Logger.warning(f"{path.name} is already downloaded")
        return
    path.parent.mkdir(exist_ok=True, parents=True)
    path.write_text(content, encoding="utf8")
    # Logger.info(f"{path.name} has been saved.")


def fix_track_link(link):
    if "?" in link:
        link += "&embedded=true"
    else:
        link += "?embedded=true"
    return link
