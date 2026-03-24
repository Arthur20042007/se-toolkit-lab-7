import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    llm_api_key: str = ""
    model_config = SettingsConfigDict(
        env_file=(".env.bot.secret", "../.env.bot.secret"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

config = Settings()
print(f"API KEY IS: {config.llm_api_key}")
print(f"OS ENV: {os.environ.get('LLM_API_KEY')}")
