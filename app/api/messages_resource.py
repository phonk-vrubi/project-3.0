import datetime
from operator import itemgetter

from flask import jsonify
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from flask_socketio import emit

from app.api.chats_utils import get_chat, create_chat
from app.api.resource_arguments.messages_args import (
    post_parser, list_get_parser
)
from app.api.users_utils import current_user_from_db, user_by_alt_id
from app.data import db_session
from app.data.chat_participants import ChatParticipants
from app.data.chats import Chats
from app.data.messages import Messages
from app.data.users import Users


class MessagesResource(Resource):
    @staticmethod
    @jwt_required
    def post():
        args = post_parser.parse_args()
        session = db_session.create_session()
        cur_user = current_user_from_db(session)
        receiver_id = args.receiver_id
        chat_id = args.chat_id
        if not (chat_id or receiver_id) or (chat_id and receiver_id):
            return jsonify({'error': 'You must specify chat_id OR receiver_id'})
        query = session.query(Chats)
        if receiver_id:
            receiver = user_by_alt_id(session, receiver_id)
            chat = get_chat(session, cur_user, receiver)
            if not chat:
                if cur_user not in receiver.friends:
                    return jsonify({'error': 'User {0} isn\' your friend'
                                   .format(cur_user.alternative_id)})
                create_chat(session, cur_user, receiver)
        else:
            chat = query.filter(Chats.id == chat_id).first()
            if not chat:
                return jsonify({'error': 'Chat with id {0} not found'
                               .format(chat_id)})
        message = Messages(
            sender_id=cur_user.id,
            chat_id=chat.id,
            text=args.text
        )
        session.add(message)
        session.commit()
        emit('new_message', message.to_dict(), room=f'chat_{chat.id}',
             namespace='/')
        return jsonify({'success': 'OK'})


class MessagesListResource(Resource):
    @staticmethod
    @jwt_required
    def get():
        args = list_get_parser.parse_args()
        receiver_id = args.receiver_id
        chat_id = args.chat_id
        session = db_session.create_session()
        cur_user = current_user_from_db(session)
        if receiver_id or chat_id:
            if receiver_id:
                receiver = user_by_alt_id(session, receiver_id)
                chat = get_chat(session, cur_user, receiver)
            else:
                chat = session.query(Chats).filter(Chats.id == chat_id).first()
            if not chat:
                return jsonify({'messages': []})
            query = session.query(Messages)
            date = datetime.datetime.fromtimestamp(args.date)
            messages = query.filter((Messages.sending_date > date) &
                                    (Messages.chat_id == chat.id)).order_by(
                Messages.sending_date).all()
            messages_serialized = [
                msg.to_dict() for msg in messages
            ]
            return jsonify({'messages': messages_serialized})
        else:
            chats_ids = list(map(
                itemgetter(0),
                session.query(ChatParticipants.chat_id).filter(
                    ChatParticipants.user_id == cur_user.id).all()
            ))
            chats_query = session.query(Chats)
            msg_query = session.query(Messages).order_by(
                Messages.sending_date.desc()
            )
            messages = []
            users_query = session.query(Users)
            for chat_id in chats_ids:
                chat: Chats = chats_query.get(chat_id)
                if chat.first_author_id == cur_user.id:
                    chat_with = users_query.get(
                        chat.second_author_id
                    ).alternative_id
                else:
                    chat_with = users_query.get(
                        chat.first_author_id
                    ).alternative_id
                if last_msg := msg_query.filter(
                        Messages.chat_id == chat_id
                ).first():
                    last_message_dict = last_msg.to_dict()
                    last_message_dict['chat_with'] = chat_with
                    messages += [last_message_dict]
            return jsonify({'messages': messages})
