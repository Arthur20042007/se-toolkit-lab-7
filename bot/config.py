import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    bot_token: str = "test-token"
    lms_api_base_url: str = "http://localhost:42002"
    lms_api_key: str = "test-key"
    llm_api_key: str = ""
    llm_api_base_url: str = "http://localhost:42005/v1"
    llm_api_model: str = "coder-model"

    model_config = SettingsConfigDict(
        # We need to find the file from both se-toolkit-lab-7/ and se-toolkit-lab-7/bot/
        env_file=(".env.bot.secret", "../.env.bot.secret"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

config = Settings()
