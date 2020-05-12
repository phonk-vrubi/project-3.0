from flask import jsonify
from flask_jwt_extended import jwt_required
from flask_restful import Resource, abort

from app.api.chats_utils import (
    get_chat, abort_if_chat_not_found, create_chat,
    error_if_user_not_chat_member
)
# from app.data.chat_participants import ChatParticipants
from app.api.resource_arguments.chats_args import (
    post_parser, delete_parser, get_parser
)
from app.api.users_utils import (
    abort_if_user_not_found, current_user_from_db, user_by_alt_id
)
from app.data import db_session
from app.data.chats import Chats
from app.data.messages import Messages


class ChatsResource(Resource):
    @staticmethod
    @jwt_required
    def get():
        args = get_parser.parse_args()
        chat_id = args.chat_id
        chat_with = args.chat_with
        if not (chat_id or chat_with) or (chat_id and chat_with):
            return jsonify(
                {'error': 'You must specify chat_id OR chat_with param'}
            )
        session = db_session.create_session()
        cur_user = current_user_from_db(session)
        if chat_id:
            chat = session.query(Chats).filter(Chats.id == chat_id).first()
            chat: Chats
            if error := error_if_user_not_chat_member(cur_user, chat):
                return error
            if not chat:
                abort(404, message=f'Chat {chat_id} not found')
                return
        else:
            abort_if_user_not_found(chat_with)
            interlocutor = user_by_alt_id(session, chat_with)
            chat = get_chat(session, cur_user, interlocutor)
            if not chat:
                abort(
                    404,
                    message=f'Chat between you and user {chat_with} not found'
                )
                return
        return jsonify({'chat': chat.to_dict()})

    @jwt_required
    def post(self):
        # метод post с помощью ChatParticipants

        # args = post_parser.parse_args()
        # chat_participants = args['chat_participants']
        # chat = Chats(
        #     title=args.get('title')
        # )
        # session = db_session.create_session()
        # session.add(chat)
        # for user in chat_participants:
        #     chat_participants_obj = ChatParticipants(
        #         user_id=user.id,
        #         chat_id=chat.id
        #     )
        #     session.add(chat_participants_obj)
        # session.commit()
        # return jsonify({'success': 'OK'})

        args = post_parser.parse_args()
        session = db_session.create_session()
        users = []
        for alt_id in [args.first_author_id, args.second_author_id]:
            abort_if_user_not_found(alt_id)
            users += [user_by_alt_id(session, alt_id)]
        # chat = Chats(
        #     # title=args.get('title'),
        #     first_author_id=args['first_author_id'],
        #     second_author_id=args['second_author_id']
        # )
        create_chat(session, *users)
        return jsonify({'success': 'OK'})

    @jwt_required
    def delete(self):
        args = delete_parser.parse_args()
        alt_id = args.get('user_id')
        chat_id = args.get('id')
        session = db_session.create_session()
        cur_user = current_user_from_db(session)
        if chat_id:
            abort_if_chat_not_found(chat_id)
            chat = session.query(Chats).get(chat_id)
            if error := error_if_user_not_chat_member(cur_user, chat):
                return error
            messages = session.query(Messages).filter(
                Messages.chat_id == chat_id)
            for message in messages:
                session.delete(message)
            session.delete(chat)
            session.commit()
            return jsonify({'success': 'OK'})
        elif alt_id:
            abort_if_user_not_found(alt_id)
            user = user_by_alt_id(session, alt_id)
            chat = get_chat(session, user, cur_user)
            if chat:
                session.delete(chat)
                session.commit()
                return jsonify({'success': 'OK'})
            else:
                return jsonify({'message': f'No chat with User {alt_id}'})
        return jsonify({'error': 'Bad request'})


class ChatsListResource(Resource):
    @staticmethod
    @jwt_required
    def get():
        session = db_session.create_session()
        cur_user = current_user_from_db(session)
        return jsonify({'chats': [chat.to_dict() for chat in cur_user.chats]})
