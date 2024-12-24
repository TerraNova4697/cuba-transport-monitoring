from pydantic_settings import BaseSettings

from pydantic import Field


class Settings(BaseSettings):
    cuba_url: str = Field(validation_alias='CUBA_URL')
    cuba_gateway_token: str = Field(validation_alias='TB_GATEWAY_TOKEN')
    CUBA_USERNAME: str = Field(validation_alias='CUBA_USERNAME')
    CUBA_PASSWORD: str = Field(validation_alias='CUBA_PASSWORD')
    CUBA_REST_URL: str = Field(validation_alias='CUBA_REST_URL')


    class Config:
        env_file = ".env"
