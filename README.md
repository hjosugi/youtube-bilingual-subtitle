# gen-subtitle

A script to download English subtitles from YouTube and generate bilingual (English-Japanese) TSV, SRT, and Markdown files.

## Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) installed
- Uses `yt-dlp` internally

## Setup

This script uses `uv` to manage dependencies.

```bash
# Sync dependencies
uv sync
```

### Environment Variables

If you want to use DeepL for translation, copy `.env.template` to `.env` and configure your DeepL API key.

```bash
cp .env.template .env
```
`.env` content:
```
DEEPL_AUTH_KEY=your_deepl_auth_key_here
```

## Usage

Run the script by providing the target YouTube URL.

```bash
uv run main.py <YouTube_URL>
```

### Command Line Options

```
usage: main.py [-h] [--translator {argos,deepl}]
               [--deepl-auth-key DEEPL_AUTH_KEY] [--out-dir OUT_DIR]
               [-n OUTPUT_NAME] [--batch-size BATCH_SIZE]
               url

positional arguments:
  url                   YouTube URL

options:
  -h, --help            Show this help message and exit
  --translator {argos,deepl}
                        Translation engine to generate Japanese text. Default is argos
  --deepl-auth-key DEEPL_AUTH_KEY
                        DeepL API key. If not specified, uses the .env file or DEEPL_AUTH_KEY environment variable.
  --out-dir OUT_DIR     Output directory. Default: out
  -n, --output-name OUTPUT_NAME
                        Base name for the output files. If not specified, it is automatically determined from the video ID.
  --batch-size BATCH_SIZE
                        Number of translations to batch together. Default: 50
```

### Example Execution

By default, the script downloads English subtitles for the provided YouTube URL, generates Japanese translations using the free [Argos Translate](https://github.com/argosopentech/argos-translate) model, and outputs the following files in the `out` directory:

1. **`.tsv`**: Tab-separated data containing the translation results.
2. **`.srt`**: Bilingual subtitle (SRT) format for video players.
3. **`.md`**: Formatted Markdown file containing side-by-side translations for language study.

(After successful completion, the original subtitle file downloaded by `yt-dlp` is automatically deleted.)
