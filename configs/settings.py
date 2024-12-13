from pydantic_settings import BaseSettings

from pydantic import Field


class Settings(BaseSettings):
    CUBA_URL: str
    cuba_gateway_token: str = Field(validation_alias='TB_GATEWAY_TOKEN')
    CUBA_USERNAME: str
    CUBA_PASSWORD: str

    class Config:
        env_file = ".env"
