from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    ## BASIC DETAILS
    APP_NAME: str = "ARIOS"
    ENV: str = "dev"

    ## DATABASE 
    DATABASE_URL: str

    groq_api_key: str
    groq_model: str = "llama-3.1-8b-instant"
    
    class Config:
        env_file = ".env"

settings = Settings()
