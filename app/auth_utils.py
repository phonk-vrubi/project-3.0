"""Модуль содержит вспомогательные функции для аутентификации в приложении."""
import datetime
import hashlib

from flask import current_app, request

from app.setup_app import csrf


def create_email_token(email):
    """Создаёт токен для подтверждения email пользователя для текущего
    приложения."""
    secret_key = current_app.config['SECRET_KEY']
    # Создаём хэш, используя алгоритм SHA256, который будем использовать как
    # токен для подтверждения email пользователя
    hash_object = hashlib.sha256(
        bytes(secret_key + email + str(datetime.datetime.now()),
              encoding='utf-8')
    )
    return hash_object.hexdigest()


def csrf_protected():
    """Функция проверяет CSRF токен запроса, в случае если в куки передан ключ
    доступа (т.к. скорее всего доступ пытается получить пользователь, а не API)
    """
    access_token_key = current_app.config['JWT_ACCESS_COOKIE_NAME']
    refresh_token_key = current_app.config['JWT_REFRESH_COOKIE_NAME']
    access_token = request.cookies.get(access_token_key)
    refresh_token = request.cookies.get(refresh_token_key)
    if access_token or refresh_token:
        csrf.protect()
