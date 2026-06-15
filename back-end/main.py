from fastapi import FastAPI
import uvicorn
from routes.health import router as health_router

app=FastAPI(title="ARIOS Backend")

# register routes
app.include_router(health_router)

@app.get("/")
def root():
    return {"message": "ARIOS is running"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )