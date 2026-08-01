from pathlib import Path

####################################   ROOT DIRECTORIES  #################################

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT= BACKEND_DIR.parent

####################################   DVC DIRECTORIES  #################################

RAW_DIR = BACKEND_DIR / "datasets" / "raw"
OUTPUT_FILE = BACKEND_DIR / "datasets" / "processed" / "documents.jsonl"

CHUNK_DIRECTORY= BACKEND_DIR / "datasets" / "chunks" / "chunks.jsonl"

EMBED_FILE = BACKEND_DIR / "artifacts" / "embeddings" / "chunk_embeddings.jsonl"

####################################   ENV Location  #################################

ENV_FILE = BACKEND_DIR / ".env"