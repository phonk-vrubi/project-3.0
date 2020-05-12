"""Пакет приложения. Содержит фабрику приложений create_app, а также функции,
используемые в обработчике шаблонов Jinja2."""

import os
import re

from flask import Flask
from flask_jwt_extended import get_current_user
from flask_restful import Api

from app.api import (
    users_resource, users_friends_resource, chats_resource, messages_resource,
    tokens_resource, ee, auth_resources
)
from app.auth_utils import csrf_protected
from app.data import db_session
from app.setup_app import *
from app.socketio_namespaces import socket_main
from app.views import main, uploads, docs
from modules import constants, md_conversion


def translate_wtforms_error(error_text):
    """Функция переводит ошибки, генерируемые полями из модуля wtforms на
    русский язык. Если перевода ошибки не найдено, возвращается оригинальный
    текст."""
    translation = constants.WTFORMS_ERRORS_TRANSLATION.get(
        error_text, error_text)
    return translation


def create_app() -> Flask:
    """Фабрика приложений. Создаёт приложение. Конфигурация происходит следующим
    образом:
    Получается значение переменной среды (далее - переменной) APP_CONFIG.
    Если значение этой переменной является путём к файлу, то вызывается функция
    app.config.from_envvar() с переданным значением переменной APP_CONFIG. Иначе
    значение переменной расценивается как название Python класса и вызывается
    функция app.config.from_object() с переданным значением этой переменной.

    Все конфиги должны содержаться в файле app/config.py.

    По умолчанию APP_CONFIG = app.config.DevelopmentConfig.

    Чтобы сконфигурировать приложение через переменные среды, установите
    значение APP_CONFIG = app.config.EnvConfig, в переменную APP_ENV_VARS
    внесите через запятую названия всех значений конфигурации, которые вы хотите
    установить через переменные среды, и соотвествующим переменным среды
    присвойте нужные значения (учитите, что эти значения вычисляются как Python
    выражения с помощью функции eval()). Подробнее в app.config.EnvConfig.

    :return: Flask-приложение
    :rtype: Flask
    """
    app = Flask(__name__)

    # Конфигурация приложения
    app_config = os.environ.get('APP_CONFIG', 'app.config.DevelopmentConfig')
    logging.info('Конфигурация через %s', app_config)
    if os.path.isfile(app_config):
        app.config.from_pyfile(app_config)
    else:
        app.config.from_object(app_config)

    if not os.path.exists(constants.UPLOAD_PATH):
        os.makedirs(constants.UPLOAD_PATH)

    # Инициализация частей приложения
    # login_manager.init_app(app)
    mail.app = app
    mail.init_app(app)
    socketio.init_app(app)
    api_ = Api(app)
    jwt.init_app(app)
    csrf.init_app(app)

    # Настройка частей приложения
    # login_manager.login_view = 'main.login'

    # Регистрация пространств имён Socket.IO
    socketio.on_namespace(socket_main.MainNamespace('/'))

    # Регистрация чертежей
    app.register_blueprint(main.blueprint)
    app.register_blueprint(uploads.blueprint)
    app.register_blueprint(docs.blueprint)

    # Регистрация API
    api_.add_resource(auth_resources.LoginResource, '/api/v1/login/')
    api_.add_resource(auth_resources.RefreshResource, '/api/v1/refresh/')
    api_.add_resource(users_resource.UsersListResource, '/api/v1/users')
    api_.add_resource(users_resource.UsersResource, '/api/v1/users/',
                      '/api/v1/users/<string:user_id>')
    api_.add_resource(users_friends_resource.UsersFriendsListResource,
                      '/api/v1/users_friends')
    api_.add_resource(users_friends_resource.UsersFriendsResource,
                      '/api/v1/users_friends/')
    ee.__i(api_)
    api_.add_resource(chats_resource.ChatsListResource, '/api/v1/chats')
    api_.add_resource(chats_resource.ChatsResource, '/api/v1/chats/')
    api_.add_resource(messages_resource.MessagesResource, '/api/v1/messages/')
    api_.add_resource(messages_resource.MessagesListResource,
                      '/api/v1/messages')
    api_.add_resource(tokens_resource.TokensResource, '/api/v1/tokens')

    # Настройки окружения Jinja2
    app.jinja_env.add_extension('jinja2.ext.do')
    app.add_template_global(print)
    app.add_template_global(bool)
    app.add_template_global(translate_wtforms_error)
    app.add_template_global(re, 're')
    app.add_template_global(constants, 'constants')
    app.add_template_global(app, 'current_app')
    app.context_processor(lambda: dict(current_user=get_current_user()))

    # Генерация документации
    with app.app_context():
        md_conversion.convert_all_md('app/docs/',
                                     'app/docs/cached/')

    # Инициализация БД
    db_session.global_init(constants.DB_PATH)

    # Настройка приложения
    app.before_request(csrf_protected)  # Защита от csrf перед запросом

    return app
