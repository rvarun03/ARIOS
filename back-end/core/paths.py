from pathlib import Path

####################################   ROOT DIRECTORIES  #################################

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT= BACKEND_DIR.parent

####################################   DVC DIRECTORIES  #################################

RAW_DIR = PROJECT_ROOT / "datasets" / "raw"
OUTPUT_FILE = PROJECT_ROOT / "datasets" / "processed" / "documents.jsonl"

CHUNK_DIRECTORY= PROJECT_ROOT / "datasets" / "chunks" / "chunks.jsonl"

EMBED_FILE = PROJECT_ROOT / "artifacts" / "embeddings" / "chunk_embeddings.jsonl"