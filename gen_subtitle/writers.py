import csv
from pathlib import Path

from gen_subtitle.models import SubtitleRow


def write_tsv(rows: list[SubtitleRow], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["no", "start", "end","en", "ja"])
        for i, row in enumerate(rows, start=1):
            writer.writerow([i, row.start, row.end,  row.en, row.ja])


def write_study_md(rows: list[SubtitleRow], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for i, row in enumerate(rows, start=1):
            f.write(f"## {i}\n")
            f.write(f"EN: {row.en}\n")
            if row.ja:
                f.write(f"JA: {row.ja}\n")
            f.write("\n")


def write_bilingual_srt(rows: list[SubtitleRow], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for i, row in enumerate(rows, start=1):
            f.write(f"{i}\n")
            f.write(f"{row.en}\n")
            if row.ja:
                f.write(f"{row.ja}\n")
            f.write("\n")
