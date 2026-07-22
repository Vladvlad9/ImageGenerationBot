from settings import settings
from src.database.alchemy.connection import AlchemyDBConnection

__all__ = ["alchemy_db_connection"]

alchemy_db_connection = AlchemyDBConnection(settings.DATABASE.POSTGRES_DSN.unicode_string())
