from datetime import datetime
from functools import wraps

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from app.data.db_session import SqlAlchemyBase, create_session
from app.data.users import Users


class Messages(SqlAlchemyBase, SerializerMixin):
    """Модель сообщений."""
    # При сериализации конвертируем дату отправки в UNIX-время
    serialize_types = (
        (datetime, datetime.timestamp),
    )
    serialize_only = ('sender_id', 'text', 'is_read', 'sending_date', 'chat_id')

    __tablename__ = 'messages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    sender_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey('users.id'),
                                  nullable=False)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey('chats.id'),
                                nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String)
    is_read = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    sending_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)
    additives = orm.relation('Additives', backref='message')

    @wraps(SerializerMixin.to_dict)
    def to_dict(self, *args, **kwargs):
        session = create_session()
        msg_dict = super().to_dict(*args, **kwargs)
        if sender_id := msg_dict.get('sender_id'):
            user: Users = session.query(Users).get(sender_id)
            msg_dict['sender_id'] = user.alternative_id
        return msg_dict
