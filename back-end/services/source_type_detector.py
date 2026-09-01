from pathlib import Path

class SourceTypeDetector:
    """
    Detects source_type automatically from source input.
    """

    def detect(
        self,
        source:str
    ) -> str:

        if not source or not source.strip():
            return "unknown"

        source_lower = source.lower().strip()

        if "youtube.com" in source_lower or "youtu.be" in source_lower:
            return "youtube"

        if "github.com" in source_lower:
            return "github"

        if source_lower.startswith("http://") or source_lower.startswith("https://"):
            return "web"

        file_extension = Path(source_lower).suffix

        if file_extension == ".pdf":
            return "pdf"

        if file_extension in {".png", ".jpg", ".jpeg", ".webp"}:
            return "ocr"

        return "unknown"