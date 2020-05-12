import sqlalchemy

from .db_session import SqlAlchemyBase


class Stickers(SqlAlchemyBase):
    """Модель стикеров."""
    __tablename__ = 'stickers'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    image_path = sqlalchemy.Column(sqlalchemy.String)
