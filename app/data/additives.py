import sqlalchemy

from .db_session import SqlAlchemyBase


class Additives(SqlAlchemyBase):
    """Модель приложений к сообщениям."""
    __tablename__ = 'additives'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    additive_type_id = sqlalchemy.Column(sqlalchemy.Integer,
                                         sqlalchemy.ForeignKey(
                                             'additives_types.id'))
    message_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey('messages.id'))
    additive = sqlalchemy.Column(sqlalchemy.String)
