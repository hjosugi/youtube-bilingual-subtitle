import shutil
import time
from pathlib import Path

from gen_subtitle.models import CliError
from gen_subtitle.utils import run


def choose_yt_dlp_command() -> list[str]:
    if shutil.which("yt-dlp"):
        return ["yt-dlp"]
    if shutil.which("uvx"):
        return ["uvx", "yt-dlp"]
    if shutil.which("uv"):
        return ["uv", "tool", "run", "yt-dlp"]
    raise CliError(
        "yt-dlp が見つかりません。`uv tool install yt-dlp` か `pipx install yt-dlp` などで入れてください"
    )


def download_subtitles(url: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    before = time.time() - 1.0
    cmd = choose_yt_dlp_command() + [
        "--skip-download",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs",
        "en.*",
        "--sub-format",
        "srt/vtt/best",
        "-P",
        str(out_dir),
        url,
    ]
    run(cmd)
    candidates = sorted(
        [
            p
            for ext in ("*.srt", "*.vtt")
            for p in out_dir.glob(ext)
            if p.stat().st_mtime >= before
        ],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise CliError("字幕ファイルが見つかりませんでした。英語字幕がない動画かもしれません")
    return candidates[0]
