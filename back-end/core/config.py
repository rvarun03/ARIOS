from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    ## BASIC DETAILS
    APP_NAME: str = "ARIOS"
    ENV: str = "dev"

    ## DATABASE 
    DATABASE_URL: str


    class Config:
        env_file = ".env"

settings = Settings()
