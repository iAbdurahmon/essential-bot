from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr

    db_name: str = 'essential'
    db_user: str = 'postgres'
    db_password: SecretStr
    db_host: str = 'localhost'
    db_port: int = 5432

    mongo_user: str = ''
    mongo_password: SecretStr = SecretStr('')
    mongo_host: str = 'localhost'
    mongo_port: int = 27017
    mongo_auth_db: str = 'admin'
    mongo_db: str = 'essential'

    redis_url: str = 'redis://localhost:6379/0'

    admin_group: int
    admin_id: int
    google_project: str = ''
    google_credentials: str = ''

    log_level: str = 'INFO'

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    @property
    def mongo_uri(self) -> str:
        if not self.mongo_user:
            return f"mongodb://{self.mongo_host}:{self.mongo_port}"
        return (f"mongodb://{self.mongo_user}:{self.mongo_password.get_secret_value()}"
                f"@{self.mongo_host}:{self.mongo_port}/{self.mongo_auth_db}")


config = Settings()
