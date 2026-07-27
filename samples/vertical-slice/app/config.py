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
    eventing_enabled: bool = False
    kafka_bootstrap_servers: str = "redpanda:9092"
    events_topic: str = "backoffice.events.v1"
    dlq_topic: str = "backoffice.dlq.v1"
    consumer_group: str = "backoffice-workflow-v1"
    worker_poll_seconds: float = 0.5
    worker_max_attempts: int = 3
    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)
