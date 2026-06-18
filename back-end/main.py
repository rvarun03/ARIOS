from fastapi import FastAPI
import uvicorn
from routes.health import router as health_router
from ingestion.web_ingestor import ingest_web
from ingestion.youtube_ingestor import ingest_youtube
from ingestion.pdf_ingestor import ingest_pdf
from ingestion.ocr_ingestor import ingest_image
from ingestion.github_ingestor import ingest_github
from ingestion.ingestion_router import ingest


app=FastAPI(title="ARIOS Backend")

# register routes
app.include_router(health_router)

@app.get("/")
def root():
    return {"message": "ARIOS is running"}

## DUMMY TEST FUNCTIONS

@app.get("/test-web")
def test_web():
    return ingest_web("https://en.wikipedia.org/wiki/Virat_Kohli")

@app.get("/test/youtube")
def test_youtube():
    return ingest_youtube(
        "https://www.youtube.com/watch?v=FzLpP8VBC6E&list=RDFzLpP8VBC6E&start_radio=1"
    )

@app.get("/test/pdf")
def test_pdf():

    return ingest_pdf(
        "Resume.pdf"
    )

@app.get("/test/ocr")
def test_ocr():

    return ingest_image(
        "sample.png"
    )

@app.get("/test/github")
def test_github():

    return ingest_github(
        "https://github.com/fastapi/fastapi.git"
    )

@app.get("/test/ingest")
def test_ingest():

    return ingest(
        source_type="web",
        source="https://en.wikipedia.org/wiki/Virat_Kohli"
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )