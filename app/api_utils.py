"""Модуль с функциями для взаимодействия с API"""

import datetime
import functools
import urllib.parse

import flask
import requests
from flask import request, current_app
from flask_jwt_extended import (
    set_access_cookies, set_refresh_cookies, unset_access_cookies,
    unset_refresh_cookies, verify_jwt_in_request_optional
)
from flask_socketio import disconnect
from flask_wtf.csrf import generate_csrf


def get_access_token():
    """Получить access_token из куки."""
    return request.cookies.get(current_app.config['JWT_ACCESS_COOKIE_NAME'])


def get_refresh_token():
    """Получить refresh_token из куки."""
    return request.cookies.get(current_app.config['JWT_REFRESH_COOKIE_NAME'])


class AuthError(Exception):
    pass


class WrongUserDataError(AuthError):
    pass


def login_user(email, password, r):
    response = requests.post(
        urllib.parse.urljoin(current_app.config['API_SERVER'],
                             '/api/v1/login/'),
        json={'email': email, 'password': password}
    )
    if response:
        json_response = response.json()
        access_token = json_response['access_token']
        refresh_token = json_response['refresh_token']
        set_access_cookies(r, access_token)
        set_refresh_cookies(r, refresh_token)
    else:
        raise WrongUserDataError('Wrong email or password')


def refresh_user(r):
    response = requests.post(urllib.parse.urljoin(
        current_app.config['API_SERVER'],
        '/api/v1/refresh/'),
        json={'refresh_token': get_refresh_token()})
    if response:
        json_response = response.json()
        access_token = json_response.get('access_token')
        if access_token:
            set_access_cookies(r, access_token)
            return r


def logout_user(r):
    unset_access_cookies(r)
    unset_refresh_cookies(r)


def authenticated_only(f):
    """Декоратор по типу flask_login.login_required для FlaskIO функций"""

    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not verify_jwt_in_request_optional():
            disconnect()
        else:
            return f(*args, **kwargs)

    return wrapped


def register_user(user_data) -> bool:
    """Функция регистрирует пользователя в приложении, используя переданный
    словарь user_data. В случае успеха возвращает True, иначе - False"""
    response = requests.post(
        urllib.parse.urljoin(current_app.config['API_SERVER'],
                             '/api/v1/users/'),
        json={**user_data}
    )
    if response:
        json_response = response.json()
        if 'success' in json_response:
            return True
    return False


def get_user_token(email, password):
    """Получить токен подтверждения email пользователя через API."""
    response = requests.get(
        urllib.parse.urljoin(current_app.config['API_SERVER'], 'api/v1/tokens'),
        json={'email': email, 'password': password}
    )
    if response:
        json_response = response.json()
        if token := json_response.get('token'):
            return token


def verify_email_by_token(token) -> bool:
    response = requests.post(
        urllib.parse.urljoin(current_app.config['API_SERVER'], 'api/v1/tokens'),
        json={'token': token}
    )
    if response:
        json_response = response.json()
        if 'success' in json_response:
            return True
    return False


def nullable_bool(value):
    if value is None:
        return value
    return bool(value)


class APIModel:
    """Базовая модель API сущности."""
    # "API сущность" - объект, возвращаемый при обращении к API
    # Данный класс - обёртка для таких объектов

    _attr_types = {}
    _url = None
    _json_key = None

    def __init__(self, id_):
        self._id = id_
        self._model_attrs = {}
        self._set_model_attrs = {}

    @property
    def id(self):
        """id сущности"""
        return self._id

    def _send_commit_request(self, **additional_json):
        """Отправляет запрос к API и возвращает ответ."""
        return requests.put(self._url,
                            json={**self._set_model_attrs,
                                  'access_token': get_access_token(),
                                  **additional_json})

    def commit(self, **additional_json):
        """Отправляет к API запрос на изменение данных сущности на присвоенные
        данной модели."""
        response = self._send_commit_request(**additional_json)
        if response:
            json_response = response.json()
            if user_id := json_response.get('user_id'):
                self._model_attrs.clear()
                self._set_model_attrs.clear()
                self._id = user_id
                return True
        return False

    def __setattr__(self, key, value):
        if key.startswith('_'):
            self.__dict__[key] = value
        else:
            self._set_model_attrs[key] = value

    def __getattr__(self, item):
        if self._model_attrs:
            if item in self._model_attrs:
                attr = self._model_attrs[item]
                if attr_type := self._attr_types.get(item):
                    return attr_type(attr)
                return attr
            else:
                raise AttributeError(item)
        url = urllib.parse.urljoin(self._url, self._id)
        response = requests.get(url, headers=request.headers)
        if response:
            json_response = response.json()
            if self._from_json(json_response):
                return getattr(self, item)
            raise Exception('No such model')
        raise Exception(f'{response.status_code} {response.reason}')

    def update(self):
        """Обновить данные модели."""
        self._model_attrs.clear()

    def _from_json(self, json_) -> bool:
        """Метод отвечает за то, как будет парситься json сущности. По умолчанию
        все атрибуты присваиваются словарю self._model_attrs. Если конвертация
        прошла успешно, возвращает True, иначе False."""
        if model := json_.get(self._json_key):
            for k, v in model.items():
                self._model_attrs[k] = v
            return True
        return False


class UserAPIModel(APIModel):
    """Модель API сущности пользователя."""
    _attr_types = {'created_date': datetime.datetime.fromisoformat}
    _json_key = 'user'

    def __init__(self, user_id):
        self._url = urllib.parse.urljoin(current_app.config['API_SERVER'],
                                         '/api/v1/users/')
        self._avatar = None
        super().__init__(user_id)

    @property
    def user_id(self):
        return self.id

    def set_avatar(self, val):
        self._avatar = val

    def _send_commit_request(self, **additional_json):
        return requests.put(self._url,
                            cookies={**flask.request.cookies},
                            headers={'X-CSRFToken': generate_csrf()},
                            data={**self._set_model_attrs,
                                  'access_token': get_access_token(),
                                  **additional_json},
                            files={'avatar': (self._avatar.filename,
                                              self._avatar.stream,
                                              self._avatar.mimetype)})
