"""Модуль с различными функциями для взаимодействия с моделью чатов."""

from flask import jsonify
from flask_restful import abort

from app.data import db_session
from app.data.chat_participants import ChatParticipants
from app.data.chats import Chats


def get_chat(session, first_user, second_user):
    chat = session.query(Chats).filter(
        ((Chats.first_author_id == first_user.id) &
         (Chats.second_author_id == second_user.id)) |
        ((Chats.first_author_id == second_user.id) &
         (Chats.second_author_id == first_user.id))).first()
    return chat


def create_chat(session, first_user, second_user):
    """Создаёт чат между двумя пользователями, если он ещё не создан, и
    возвращает его"""
    if chat := get_chat(session, first_user, second_user):
        return chat
    chat = Chats()
    chat.first_author_id = first_user.id
    chat.second_author_id = second_user.id
    session.add(chat)
    session.commit()
    chat_id = chat.id

    cur_user_participant = ChatParticipants()
    cur_user_participant.chat_id = chat_id
    cur_user_participant.user_id = first_user.id

    receiver_participant = ChatParticipants()
    receiver_participant.chat_id = chat_id
    receiver_participant.user_id = second_user.id

    chat.chat_participants += [cur_user_participant,
                               receiver_participant]
    session.commit()
    return chat


def abort_if_chat_not_found(chat_id):
    session = db_session.create_session()
    chat = session.query(Chats).get(chat_id)
    if not chat:
        abort(404, message=f'Chat {chat_id} not found')


def error_if_user_not_chat_member(user, chat):
    if user not in chat.chat_participants:
        return jsonify({'error': 'You are not a member of this chat'})
