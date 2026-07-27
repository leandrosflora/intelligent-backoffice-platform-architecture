from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_path: str = "./vertical-slice.db"
    policy_mode: str = "embedded"
    opa_url: str = "http://opa:8181"
    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)
