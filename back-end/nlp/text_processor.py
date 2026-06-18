import re

class TextProcessor:

    def __init__(self):
        """
        Future:
        - spaCy model
        - stopword configuration
        - custom dictionaries
        - NLP pipeline settings
        """
        pass

    # ==================================================
    # STEP 1: TEXT CLEANING
    # ==================================================

    def clean_text(self,text:str):
        """
        Main cleaning pipeline.

        Steps:
        1. Remove junk characters
        2. Remove duplicate newlines
        3. Normalize whitespace
        4. Strip leading/trailing spaces
        """

        if not text:
            return ""

        text = self._remove_duplicate_newlines(text)

        text = self._normalize_whitespace(text)

        text = text.strip()

        return text

    # ==================================================
    # INTERNAL HELPERS
    # ==================================================

    def _remove_junk_characters(self, text: str) -> str:
        """
        Removes unwanted special characters while
        preserving common punctuation.
        """

        return re.sub(
            r"[^\w\s.,!?;:()\-]",
            "",
            text
        )

    def _remove_duplicate_newlines(self, text: str) -> str:
        """
        Converts 3+ consecutive newlines into 2.
        """

        return re.sub(
            r"\n{3,}",
            "\n\n",
            text
        )

    def _normalize_whitespace(self, text: str) -> str:
        """
        Converts multiple spaces/tabs into a single space.
        """

        return re.sub(
            r"[ \t]+",
            " ",
            text
        )    
    def normalize_text(self, text: str) -> str:
        pass

    def tokenize(self, text: str):
        pass

    def remove_stopwords(self, tokens):
        pass

    def lemmatize(self, tokens):
        pass