from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-5", alias="OPENAI_MODEL")
    openai_embed_model: str = Field(default="text-embedding-3-large", alias="OPENAI_EMBED_MODEL")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")

    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-sonnet-4-5", alias="ANTHROPIC_MODEL")
    anthropic_base_url: str = Field(default="https://api.anthropic.com", alias="ANTHROPIC_BASE_URL")

    docs_dir: str = Field(default="./data/docs", alias="DOCS_DIR")
    index_path: str = Field(default="./data/index.json", alias="INDEX_PATH")
    top_k: int = Field(default=5, alias="TOP_K")
    chunk_max_chars: int = Field(default=900, alias="CHUNK_MAX_CHARS")
    chunk_overlap_chars: int = Field(default=120, alias="CHUNK_OVERLAP_CHARS")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

settings = Settings()
