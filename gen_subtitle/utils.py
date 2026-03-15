import html
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Sequence

from gen_subtitle.models import CliError

HTML_TAG_RE = re.compile(r"<[^>]+>")


def run(cmd: Sequence[str]) -> None:
    printable = " ".join(shlex_quote(part) for part in cmd)
    print(f"$ {printable}", file=sys.stderr)
    completed = subprocess.run(cmd)
    if completed.returncode != 0:
        raise CliError(f"Command failed: {printable}")


def shlex_quote(text: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_./:=+\-]+", text):
        return text
    return '"' + text.replace('"', '\\"') + '"'


def normalize_timestamp(text: str) -> str:
    text = text.strip().replace(".", ",")
    parts = text.split(":")
    if len(parts) == 2:
        minutes, sec_ms = parts
        return f"00:{int(minutes):02d}:{sec_ms}"
    if len(parts) == 3:
        hours, minutes, sec_ms = parts
        return f"{int(hours):02d}:{int(minutes):02d}:{sec_ms}"
    raise CliError(f"Invalid timestamp format: {text}")


def clean_subtitle_text(text: str) -> str:
    text = html.unescape(text)
    text = HTML_TAG_RE.sub("", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def batched(seq: Sequence[str], size: int) -> Iterable[Sequence[str]]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def base_stem(path: Path) -> str:
    name = path.name
    name = re.sub(r"\.[A-Za-z0-9_-]+\.(?:srt|vtt)$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\.(?:srt|vtt)$", "", name, flags=re.IGNORECASE)
    return name
