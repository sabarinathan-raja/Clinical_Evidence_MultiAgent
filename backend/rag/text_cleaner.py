
import re
import unicodedata


class TextCleaner:

    @staticmethod
    def clean(text: str) -> str:

        if not text:
            return ""

        text = unicodedata.normalize("NFKC", text)

        text = text.replace("\x00", " ")
        text = text.replace("\uf0b7", " ")

        text = re.sub(
            r"[\r\t]+",
            " ",
            text
        )

        text = re.sub(
            r"(?<!\n)-\n(?=\w)",
            "",
            text
        )

        text = re.sub(
            r"[ ]{2,}",
            " ",
            text
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text
        )

        return text.strip()

    @staticmethod
    def normalize_query(text: str) -> str:
        return TextCleaner.clean(text).lower()
