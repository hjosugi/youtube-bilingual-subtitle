import sys
from typing import Sequence

from gen_subtitle.models import CliError, SubtitleRow
from gen_subtitle.utils import batched


class Translator:
    def translate_many(self, texts: Sequence[str]) -> list[str]:
        raise NotImplementedError


class DeepLTranslator(Translator):
    def __init__(self, auth_key: str):
        if not auth_key:
            raise CliError(
                "DeepL を使うには --deepl-auth-key または DEEPL_AUTH_KEY が必要です"
            )
        import deepl

        self.client = deepl.DeepLClient(auth_key)

    def translate_many(self, texts: Sequence[str]) -> list[str]:
        if not texts:
            return []
        results = self.client.translate_text(
            list(texts),
            source_lang="EN",
            target_lang="JA",
            split_sentences="off",
            preserve_formatting=True,
        )
        if not isinstance(results, list):
            results = [results]
        return [result.text.strip() for result in results]


class ArgosTranslator(Translator):
    def __init__(self, from_code: str = "en", to_code: str = "ja"):
        self.from_code = from_code
        self.to_code = to_code
        self._ensure_package_installed()

    def _ensure_package_installed(self) -> None:
        import argostranslate.translate

        translation = argostranslate.translate.get_translation_from_codes(
            self.from_code, self.to_code
        )
        if translation is not None:
            return

        print(
            f"Argos の翻訳モデル {self.from_code}->{self.to_code} を取得します...",
            file=sys.stderr,
        )
        import argostranslate.package

        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        package_to_install = next(
            (
                pkg
                for pkg in available_packages
                if pkg.from_code == self.from_code and pkg.to_code == self.to_code
            ),
            None,
        )
        if package_to_install is None:
            raise CliError(
                f"Argos の翻訳モデル {self.from_code}->{self.to_code} が見つかりません"
            )
        download_path = package_to_install.download()
        argostranslate.package.install_from_path(download_path)

        import argostranslate.translate

        translation = argostranslate.translate.get_translation_from_codes(
            self.from_code, self.to_code
        )
        if translation is None:
            raise CliError(
                f"Argos の翻訳モデル {self.from_code}->{self.to_code} の初期化に失敗しました"
            )

    def translate_many(self, texts: Sequence[str]) -> list[str]:
        import argostranslate.translate

        return [
            argostranslate.translate.translate(text, self.from_code, self.to_code).strip()
            if text.strip()
            else ""
            for text in texts
        ]


def make_translator(name: str, deepl_auth_key: str) -> Translator:
    if name == "deepl":
        return DeepLTranslator(deepl_auth_key)
    if name == "argos":
        return ArgosTranslator("en", "ja")
    raise CliError(f"未対応 translator: {name}")


def translate_rows(
    rows: list[SubtitleRow], translator: Translator, batch_size: int
) -> None:
    texts = [row.en for row in rows]
    translated: list[str] = []
    for chunk in batched(texts, batch_size):
        translated.extend(translator.translate_many(chunk))
    if len(translated) != len(rows):
        raise CliError(
            f"翻訳件数が一致しませんでした: input={len(rows)} output={len(translated)}"
        )
    for row, ja in zip(rows, translated):
        row.ja = ja.strip()
