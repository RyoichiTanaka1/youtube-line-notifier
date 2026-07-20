from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    line_channel_access_token: str
    line_user_id: str

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
