from flask import jsonify
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from app.api.chats_utils import create_chat
from app.api.resource_arguments.users_friends_args import (
    list_get_parser, post_parser, delete_parser
)
from app.api.users_utils import (
    abort_if_user_not_found, USERS_PUBLIC_ONLY, current_user_from_db,
    user_by_alt_id
)
from app.data import db_session
from app.data.users import Users
from app.data.users_friends import UsersFriends


class UsersFriendsResource(Resource):
    @staticmethod
    @jwt_required
    def post():
        args = post_parser.parse_args()
        abort_if_user_not_found(args.friend_id)
        session = db_session.create_session()
        cur_user = current_user_from_db(session)
        friend = user_by_alt_id(session, args.friend_id)
        action = args.action
        if action in ('accept', 'deny'):
            request_from_friend = session.query(UsersFriends).filter(
                (UsersFriends.inviter_id == friend.id) &
                (UsersFriends.invitee_id == cur_user.id)).first()
            request_from_cur_user = session.query(UsersFriends).filter(
                (UsersFriends.inviter_id == cur_user.id) &
                (UsersFriends.invitee_id == friend.id)).first()
            if request_from_friend:
                if action == 'accept':
                    if request_from_friend.is_accepted is True:
                        return jsonify({
                            'error': f'Friend request from '
                                     f'{friend.alternative_id} already accepted'
                        })
                    request_from_friend.is_accepted = True
                    # Создаём чат между пользователями сразу, т.к. иначе на
                    # главной странице пользователь не будет добавлен в
                    # комнату SocketIO с чатом между этими пользователями, и
                    # соответственно не будет получать сообщения от этого
                    # пользователя
                    create_chat(session, cur_user, friend)
                else:
                    if request_from_friend.is_accepted is False:
                        return jsonify({
                            'error':
                                f'Friend request from {friend.id} already '
                                f'denied'
                        })
                    request_from_friend.is_accepted = False
            elif request_from_cur_user:
                if action == 'deny':
                    request = UsersFriends()
                    request.inviter_id = friend.id
                    request.invitee_id = cur_user.id
                    request.is_accepted = False
                    session.add(request)
                    session.delete(request_from_cur_user)
                else:
                    return jsonify({
                        'error': 'Only invitee can accept friend request'
                    })
            else:
                if not (request_from_friend or request_from_cur_user):
                    return jsonify(
                        {'error': '{0} didn\'t send friend request to {1}'
                            .format(friend.alternative_id,
                                    cur_user.alternative_id)}
                    )
        elif action == 'add':
            request = session.query(UsersFriends).filter(
                (UsersFriends.inviter_id == cur_user.id) &
                (UsersFriends.invitee_id == friend.id)).first()
            if request:
                return jsonify({
                    'error':
                        'Friend request to {0} already sent'.format(
                            friend.alternative_id)
                })
            users_friends_obj = UsersFriends(
                inviter_id=cur_user.id,
                invitee_id=friend.id
            )
            session.add(users_friends_obj)
        session.commit()
        return jsonify({'success': 'OK'})

    @staticmethod
    @jwt_required
    def delete():
        args = delete_parser.parse_args()
        alt_id = args.friend_id
        abort_if_user_not_found(alt_id)
        session = db_session.create_session()
        user = user_by_alt_id(session, alt_id)
        cur_user = current_user_from_db(session)
        request = session.query(UsersFriends).filter(
            (UsersFriends.inviter_id == cur_user.id) &
            (UsersFriends.invitee_id == user.id)
        ).first()
        if request:
            session.delete(request)
            session.commit()
            return jsonify({'success': 'OK'})
        else:
            return jsonify({
                'error': f'You didn\'t send friend request to user {alt_id}'
            })


class UsersFriendsListResource(Resource):
    @staticmethod
    @jwt_required
    def get():
        args = list_get_parser.parse_args()
        session = db_session.create_session()
        cur_user = current_user_from_db(session)
        type_ = args.type
        query = session.query(Users)
        if type_ == 'incoming':
            friend_dicts = []
            for request in cur_user.incoming_friend_requests:
                request: UsersFriends
                if request.is_accepted is not True:
                    user = query.filter(Users.id == request.inviter_id).first()
                    friend_dict = user.to_dict(only=USERS_PUBLIC_ONLY)
                    friend_dict['is_accepted'] = request.is_accepted
                    friend_dicts += [friend_dict]
            return jsonify({'friends': friend_dicts})
        elif type_ == 'outgoing':
            friends = []
            for request in cur_user.outgoing_friend_requests:
                request: UsersFriends
                if not request.is_accepted:
                    user = query.filter(Users.id == request.invitee_id).first()
                    friends += [user]
            return jsonify({'friends': [
                user.to_dict(only=USERS_PUBLIC_ONLY)
                for user in friends
            ]})
        else:
            return jsonify({
                'friends': [
                    user.to_dict(only=USERS_PUBLIC_ONLY)
                    for user in cur_user.friends
                ]
            })
