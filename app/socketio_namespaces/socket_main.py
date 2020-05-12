import urllib.parse

import flask
import requests
from flask_jwt_extended import get_jwt_identity, jwt_optional
from flask_socketio import join_room, Namespace

from app.api_utils import get_access_token


class MainNamespace(Namespace):
    """Главное пространство имён SocketIO приложения."""

    @staticmethod
    @jwt_optional
    def on_connect():
        """При присоединении пользователя добавляем его в его личную комнату, а
        также в комнаты всех чатов, в которых он состоит."""
        identity = get_jwt_identity()
        if identity:
            join_room(f'user_{identity}')
            response = requests.get(
                urllib.parse.urljoin(flask.current_app.config['API_SERVER'],
                                     '/api/v1/chats'),
                json={'access_token': get_access_token()}
            )
            if response:
                if json_response := response.json():
                    if chats := json_response.get('chats'):
                        for chat in chats:
                            join_room(f'chat_{chat["id"]}')
