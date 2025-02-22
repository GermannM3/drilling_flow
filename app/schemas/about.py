from pydantic import BaseModel

class LegalInfo(BaseModel):
    maps_terms: str = "https://yandex.ru/legal/maps_api/"
    maps_attribution: str = "© Яндекс Карты"

class AboutInfo(BaseModel):
    app_name: str = "DrillFlow"
    version: str = "1.0.0"
    legal: LegalInfo
    contacts: dict 