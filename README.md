# gen-subtitle

YouTubeの英語字幕を取得して、日英対訳の TSV / SRT / Markdown ファイルを生成するスクリプトです。

## 必須要件

- Python 3.11 以上
- [uv](https://docs.astral.sh/uv/) がインストールされていること
- 内部で `yt-dlp` コマンドを使用します。

## 準備

本スクリプトは `uv` を使用して依存関係を管理しています。

```bash
# 依存関係の同期
uv sync
```

### 環境変数設定

DeepLによる翻訳を行いたい場合は、`.env.template` ファイルを `.env` という名前でコピーして、ご自身の DeepL API キーを記述してください。

```bash
cp .env.template .env
```
`.env` の内容：
```
DEEPL_AUTH_KEY=your_deepl_auth_key_here
```

## 使い方

対象の YouTube URL を指定して実行します。

```bash
uv run main.py <YouTube_URL>
```

### コマンドラインオプション

```
usage: main.py [-h] [--translator {argos,deepl}]
               [--deepl-auth-key DEEPL_AUTH_KEY] [--out-dir OUT_DIR]
               [-n OUTPUT_NAME] [--batch-size BATCH_SIZE]
               url

positional arguments:
  url                   YouTube URL

options:
  -h, --help            ヘルプメッセージを表示
  --translator {argos,deepl}
                        日本語訳の生成に使う翻訳エンジン。既定値は argos
  --deepl-auth-key DEEPL_AUTH_KEY
                        DeepL API key。未指定時は .env または DEEPL_AUTH_KEY 環境変数を使う
  --out-dir OUT_DIR     出力先ディレクトリ。既定値: out
  -n, --output-name OUTPUT_NAME
                        出力ファイルのベース名。指定しない場合は動画ID等から自動決定します
  --batch-size BATCH_SIZE
                        翻訳をまとめる件数。既定値: 50
```

### 実行例

デフォルトでは、引数として渡した YouTube 動画から英語の字幕をダウンロードし、無料の [Argos Translate](https://github.com/argosopentech/argos-translate) モデルを用いて日本語を生成し、`out` ディレクトリに以下のファイルを出力します。

1. **`.bilingual.tsv`**: 翻訳結果をまとめたタブ区切りデータ
2. **`.bilingual.srt`**: 動画プレイヤーで字幕表示するための日英対訳 SRT ファイル
3. **`.study.md`**: 言語学習用に整形された対訳のマークダウンファイル

（処理完了後、`yt-dlp` がダウンロードしたオリジナルの字幕ファイルは自動的に削除されます。）
