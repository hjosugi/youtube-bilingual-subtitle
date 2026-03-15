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
        description="YouTube 英語字幕を取得して、日英対訳 TSV / SRT / Markdown を作る"
    )
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument(
        "--translator",
        choices=("argos", "deepl"),
        default="argos",
        help="日本語訳の生成に使う翻訳エンジン。既定値は argos",
    )
    parser.add_argument(
        "--deepl-auth-key",
        default=os.environ.get("DEEPL_AUTH_KEY", ""),
        help="DeepL API key。未指定時は DEEPL_AUTH_KEY を使う",
    )
    parser.add_argument(
        "--out-dir",
        default="out",
        help="出力先ディレクトリ。既定値: out",
    )
    parser.add_argument(
        "-n",
        "--output-name",
        default="",
        help="出力ファイルのベース名。指定しない場合は動画ID等から自動決定します",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="翻訳をまとめる件数。既定値: 50",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.batch_size <= 0:
        raise CliError("--batch-size は 1 以上にしてください")

    out_dir = Path(args.out_dir).resolve()
    subtitle_path = download_subtitles(args.url, out_dir)
    rows = parse_subtitle_file(subtitle_path)
    translator = make_translator(args.translator, args.deepl_auth_key)
    translate_rows(rows, translator, args.batch_size)

    stem = args.output_name if args.output_name else base_stem(subtitle_path)
    
    tsv_path = out_dir / f"{stem}.bilingual.tsv"
    md_path = out_dir / f"{stem}.study.md"
    srt_path = out_dir / f"{stem}.bilingual.srt"

    write_tsv(rows, tsv_path)
    write_study_md(rows, md_path)
    write_bilingual_srt(rows, srt_path)

    # Delete the intermediate subtitle file
    try:
        subtitle_path.unlink()
    except OSError as e:
        print(f"警告: 中間字幕ファイルの削除に失敗しました ({subtitle_path}): {e}", file=sys.stderr)

    print("完了")
    print(f"削除済 字幕: {subtitle_path}")
    print(f"TSV : {tsv_path}")
    print(f"MD  : {md_path}")
    print(f"SRT : {srt_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CliError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(1)
