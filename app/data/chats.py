import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Chats(SqlAlchemyBase, SerializerMixin):
    """Модель чатов."""
    # Комментарий

    # Это почему-то ни в какую не работает
    # serialize_rules = ('-chat_participants',)
    serialize_only = ('id', 'first_author_id', 'second_author_id', 'title')

    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    first_author_id = sqlalchemy.Column(sqlalchemy.Integer,
                                        sqlalchemy.ForeignKey('users.id'),
                                        nullable=False)
    second_author_id = sqlalchemy.Column(sqlalchemy.Integer,
                                         sqlalchemy.ForeignKey('users.id'),
                                         nullable=False)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=None)
    chat_participants = orm.relation('ChatParticipants', backref='chats')
