import sqlalchemy

from .db_session import SqlAlchemyBase


class ChatParticipants(SqlAlchemyBase):
    """Модель участников чата."""
    __tablename__ = 'chat_participants'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey('users.id'))
    chat_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey('chats.id'))
