from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    ## BASIC DETAILS
    APP_NAME: str = "ARIOS"
    ENV: str = "dev"
    FRONTEND_URL: str

    ## DATABASE 
    DATABASE_URL: str

    groq_api_key: str
    groq_model: str = "llama-3.1-8b-instant"

    # AWS S3
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "ap-south-1"
    AWS_S3_BUCKET_NAME: str

    class Config:
        env_file = ".env"

settings = Settings()
