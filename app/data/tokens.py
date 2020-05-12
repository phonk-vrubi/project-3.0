import datetime

import sqlalchemy

from .db_session import SqlAlchemyBase


class Tokens(SqlAlchemyBase):
    """Модель токенов для проверки email."""
    __tablename__ = 'tokens'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String)
    token = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
