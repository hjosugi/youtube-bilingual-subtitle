import re
from pathlib import Path

from gen_subtitle.models import CliError, SubtitleRow
from gen_subtitle.utils import clean_subtitle_text, normalize_timestamp

SRT_TIME_RE = re.compile(
    r"^(?P<start>\d{2}:\d{2}:\d{2}[,.]\d{3})\s+-->\s+(?P<end>\d{2}:\d{2}:\d{2}[,.]\d{3})$"
)
VTT_TIME_RE = re.compile(
    r"^(?P<start>(?:\d{2}:)?\d{2}:\d{2}\.\d{3})\s+-->\s+(?P<end>(?:\d{2}:)?\d{2}:\d{2}\.\d{3})(?:\s+.*)?$"
)


def parse_srt(path: Path) -> list[SubtitleRow]:
    content = path.read_text(encoding="utf-8-sig")
    blocks = re.split(r"\n\s*\n", content.strip(), flags=re.MULTILINE)
    rows: list[SubtitleRow] = []

    for block in blocks:
        lines = [line.rstrip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        if lines[0].isdigit():
            lines = lines[1:]
        if len(lines) < 2:
            continue
        match = SRT_TIME_RE.match(lines[0])
        if not match:
            continue
        text = clean_subtitle_text(" ".join(lines[1:]))
        if not text:
            continue
        rows.append(
            SubtitleRow(
                start=normalize_timestamp(match.group("start")),
                end=normalize_timestamp(match.group("end")),
                en=text,
            )
        )
    return rows


def parse_vtt(path: Path) -> list[SubtitleRow]:
    rows: list[SubtitleRow] = []
    current_start = ""
    current_end = ""
    current_text_lines: list[str] = []

    def flush() -> None:
        nonlocal current_start, current_end, current_text_lines
        if current_start and current_end and current_text_lines:
            text = clean_subtitle_text(" ".join(current_text_lines))
            if text:
                rows.append(SubtitleRow(start=current_start, end=current_end, en=text))
        current_start = ""
        current_end = ""
        current_text_lines = []

    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip("\ufeff")
        stripped = line.strip()
        if not stripped:
            flush()
            continue
        if stripped in {"WEBVTT"}:
            continue
        if stripped.startswith(("NOTE", "STYLE", "REGION")):
            continue
        match = VTT_TIME_RE.match(stripped)
        if match:
            flush()
            current_start = normalize_timestamp(match.group("start"))
            current_end = normalize_timestamp(match.group("end"))
            continue
        if stripped.isdigit() and not current_start:
            continue
        if current_start:
            current_text_lines.append(stripped)

    flush()
    return rows


def parse_subtitle_file(path: Path) -> list[SubtitleRow]:
    suffix = path.suffix.lower()
    if suffix == ".srt":
        rows = parse_srt(path)
    elif suffix == ".vtt":
        rows = parse_vtt(path)
    else:
        raise CliError(f"未対応の字幕形式です: {path.suffix}")
    if not rows:
        raise CliError(f"字幕解析結果が空でした: {path}")
    return rows
