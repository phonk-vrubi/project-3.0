"""Модуль, отвечающий за создание различных частей приложения, которые будут
прикреплены к нему на этапе инициализации"""

import logging

from flask import redirect, url_for, request, make_response
from flask_jwt_extended import (
    JWTManager, )
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect

from app.api_utils import UserAPIModel, refresh_user

mail = Mail()
socketio = SocketIO()
jwt = JWTManager()
csrf = CSRFProtect()


@jwt.unauthorized_loader
def unauthorized_loader(msg):
    return redirect(url_for('main.login'))


@jwt.user_loader_callback_loader
def user_loader(identity):
    return UserAPIModel(identity)


@jwt.expired_token_loader
def expired_token_loader(msg):
    r = make_response(redirect(request.path))
    try:
        refresh_user(r)
        return r
    except Exception as e:
        logging.warning(e)
    return redirect(url_for('main.login'))
