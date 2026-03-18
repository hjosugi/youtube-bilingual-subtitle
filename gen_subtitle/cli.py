import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from gen_subtitle.models import CliError
from gen_subtitle.parsers import parse_subtitle_file
from gen_subtitle.translators import make_translator, translate_rows
from gen_subtitle.utils import base_stem
from gen_subtitle.writers import write_bilingual_srt, write_study_md, write_tsv
from gen_subtitle.youtube import download_subtitles


def parse_args() -> argparse.Namespace:
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Download YouTube English subtitles and create bilingual TSV / SRT / Markdown files."
    )
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument(
        "--translator",
        choices=("argos", "deepl"),
        default="argos",
        help="Translation engine to generate Japanese text. Default: argos",
    )
    parser.add_argument(
        "--deepl-auth-key",
        default=os.environ.get("DEEPL_AUTH_KEY", ""),
        help="DeepL API key. Uses DEEPL_AUTH_KEY environment variable or .env if not specified.",
    )
    parser.add_argument(
        "--out-dir",
        default="out",
        help="Output directory. Default: out",
    )
    parser.add_argument(
        "-n",
        "--output-name",
        default="",
        help="Base name for the output files. Automatically determined from video ID if not specified.",
    )
    parser.add_argument(
        "--en-only",
        action="store_true",
        help="Skip translation and output English only.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of rows to process in a single batch. Default: 50",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.batch_size <= 0:
        raise CliError("--batch-size must be 1 or greater")

    out_dir = Path(args.out_dir).resolve()
    subtitle_path = download_subtitles(args.url, out_dir)
    rows = parse_subtitle_file(subtitle_path)

    if not args.en_only:
        translator = make_translator(args.translator, args.deepl_auth_key)
        translate_rows(rows, translator, args.batch_size)

    stem = args.output_name if args.output_name else base_stem(subtitle_path)

    tsv_path = out_dir / f"{stem}.tsv"
    md_path = out_dir / f"{stem}.md"
    srt_path = out_dir / f"{stem}.srt"

    write_tsv(rows, tsv_path)
    write_study_md(rows, md_path)
    write_bilingual_srt(rows, srt_path)

    # Delete the intermediate subtitle file
    try:
        subtitle_path.unlink()
    except OSError as e:
        print(
            f"Warning: Failed to delete intermediate subtitle file ({subtitle_path}): {e}",
            file=sys.stderr,
        )

    print("Done")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CliError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(1)
