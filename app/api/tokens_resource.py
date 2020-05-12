from flask import jsonify
from flask_restful import Resource, abort

from app.api.resource_arguments import tokens_args
from app.data import db_session
from app.data.tokens import Tokens
from app.data.users import Users


class TokensResource(Resource):
    @staticmethod
    def get():
        args = tokens_args.get_parser.parse_args()
        session = db_session.create_session()
        token = session.query(Tokens).filter(
            Tokens.email == args.email
        ).first()
        if token:
            password = args.password
            user: Users = session.query(Users).filter(
                Users.email == token.email
            ).first()
            if user:
                if user.check_password(password):
                    return jsonify({'token': token.token})
                else:
                    return abort(401, message='Bad password')
            else:
                return abort(404, message=f'No user with email {args.email}')
        else:
            return abort(404, message=f'Token for email {args.email} not found')

    @staticmethod
    def post():
        args = tokens_args.post_parser.parse_args()
        session = db_session.create_session()
        token = session.query(Tokens).filter(
            Tokens.token == args.token
        ).first()
        if token:
            user: Users = session.query(Users).filter(
                Users.email == token.email
            ).first()
            if user:
                user.is_confirmed = True
                session.commit()
                return jsonify({'success': 'OK'})
            else:
                abort(404, message=f'No user with token {args.token}')
                return
        else:
            abort(404, message=f'Token {args.token} not found')
