import json
from pydantic import BaseModel, ConfigDict


class AppConfig(BaseModel):
    database_name: str
    face_encoding_service_url: str

    model_config = ConfigDict(frozen=True)

    @classmethod
    def load_config(cls, file_path: str) -> "AppConfig":
        with open(file_path, 'r') as f:
            config_data = json.load(f)
        return cls(**config_data)


config = AppConfig.load_config('app/config/config.json')
