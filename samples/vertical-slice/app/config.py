from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_path: str = "./vertical-slice.db"
    policy_mode: str = "embedded"
    opa_url: str = "http://opa:8181"
    service_name: str = "intelligent-backoffice-vertical-slice"
    environment: str = "local"
    metrics_enabled: bool = True
    tracing_enabled: bool = False
    otlp_endpoint: str = "http://otel-collector:4317"
    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)
