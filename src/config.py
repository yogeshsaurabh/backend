import os
from typing import Optional

from dotenv import dotenv_values
from pydantic import BaseSettings

config = {
    **dotenv_values(".env"),
    **os.environ,  # override loaded values with environment variables
}


class CommonSettings(BaseSettings):
    APP_NAME: str = "evolve-app"
    DEBUG_MODE: bool = bool(config.get("DEBUG")) and config.get("DEBUG") == "true"


class ServerSettings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: int = config.get("PORT") or 8000


class DatabaseSettings(BaseSettings):
    DATABASE_URL: Optional[str] = config["DATABASE_URL"]
    MONGODB_URL: Optional[str] = config["MONGODB_URL"]


class JwtTokenSettings(BaseSettings):
    JWT_SECRET_KEY: Optional[str] = config["JWT_SECRET_KEY"]
    JWT_ADMIN_SECRET_KEY: Optional[str] = config["JWT_ADMIN_SECRET_KEY"]
    JWT_REFRESH_SECRET_KEY: Optional[str] = config["JWT_REFRESH_SECRET_KEY"]
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 180  # TODO: change it back to 30 minutes
    REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 180  # 6 months
    ALGORITHM: str = "HS256"


class OTPSettings(BaseSettings):
    TIME_OUT_MINUTES = 10  # 10 minutes


class GoogleOAuthCredentials(BaseSettings):
    GOOGLE_CLIENT_ID = config.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = config.get("GOOGLE_CLIENT_SECRET")
    GOOGLE_APP_DEBUG_CLIENT_ID = config.get("GOOGLE_APP_DEBUG_CLIENT_ID")
    GOOGLE_APP_RELEASE_CLIENT_ID = config.get("GOOGLE_APP_RELEASE_CLIENT_ID")
    config_data = {
        "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
        "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
        "GOOGLE_APP_DEBUG_CLIENT_ID": GOOGLE_APP_DEBUG_CLIENT_ID,
        "GOOGLE_APP_RELEASE_CLIENT_ID": GOOGLE_APP_RELEASE_CLIENT_ID,
    }


class OpenAI(BaseSettings):
    OPENAI_API_KEY = config.get("OPENAI_API_KEY")


class SMTPCredentials(BaseSettings):
    MAIL_USERNAME = config.get("MAIL_USERNAME")
    MAIL_PASSWORD = config.get("MAIL_PASSWORD")
    MAIL_SERVER = config.get("MAIL_SERVER")


class Settings(
    CommonSettings,
    JwtTokenSettings,
    OTPSettings,
    ServerSettings,
    DatabaseSettings,
    GoogleOAuthCredentials,
    OpenAI,
    SMTPCredentials,
):
    pass


settings = Settings()