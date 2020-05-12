import datetime

from flask import jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jwt_identity,
    jwt_refresh_token_required
)
from flask_restful import Resource, abort

from app.api.resource_arguments.auth_args import login_post_parser
from app.data import db_session
from app.data.users import Users


class LoginResource(Resource):
    """Ресурс авторизации."""

    @staticmethod
    def post():
        """Возвращает ключ доступа и ключ обновления к API в формате
        {access_token: "ключ", refresh_token: "ключ"}.
        Параметры запроса:
            email: адрес электронной почти пользователя, для которого нужно
            получить API ключ;
            password: пароль этого пользователя.
        Если такого email нет, возвращается ошибка 404. Если пароль неверный -
        ошибка 401.
        Если все данные верны, возвращается JWT токен, содержащий alternative_id
        пользователя.
        """
        args = login_post_parser.parse_args()
        email = args.email
        session = db_session.create_session()
        user: Users = session.query(Users).filter(Users.email == email).first()
        if not user or not user.check_password(args.password):
            abort(404, message='Bad email or password')
            return
        user_id = user.alternative_id
        try:
            if expires_in := args.get('expires_in'):
                expires_in = datetime.timedelta(seconds=expires_in)
        except OverflowError:
            return jsonify({'error': 'expires_in value too big'})
        access_token = create_access_token(identity=user_id,
                                           expires_delta=expires_in)
        refresh_token = create_refresh_token(identity=user_id)
        return jsonify(access_token=access_token, refresh_token=refresh_token)


class RefreshResource(Resource):
    """Ресурс обновления токена."""

    @staticmethod
    @jwt_refresh_token_required
    def post():
        """Возвращает новый access_token в формате {access_token: "ключ"}.
        Параметры запроса:
            refresh_token в json или jwt в строке запроса: refresh_token
            пользователя, для которого необходимо сгенерировать новый
            access_token.
        """
        ret = {
            'access_token': create_access_token(identity=get_jwt_identity())
        }
        return jsonify(ret)
