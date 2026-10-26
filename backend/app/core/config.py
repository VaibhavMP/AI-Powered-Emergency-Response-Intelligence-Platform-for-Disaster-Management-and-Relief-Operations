from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./disaster_response.db"
    secret_key: str = "dev-secret-key-change-in-production"
    environment: str = "development"
    gdacs_api_url: str = "https://www.gdacs.org/xml/rss.xml"
    usgs_earthquake_api_url: str = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
