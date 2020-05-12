"""Модуль с различными функциями для взаимодействия с моделью пользователей."""

from flask_jwt_extended import get_jwt_identity
from flask_restful import abort

from app.data import db_session
from app.data.users import Users

USERS_PRIVATE_ONLY = (
    'alternative_id', 'first_name', 'second_name', 'email',
    'phone_number', 'age', 'city', 'additional_inf',
    'is_confirmed', 'avatar', 'created_date')
USERS_PUBLIC_ONLY = ('first_name', 'second_name', 'alternative_id', 'avatar')


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(Users).filter(Users.alternative_id == user_id).first()
    if not user:
        abort(404, message=f'User {user_id} not found')


def users_like(field, val):
    return getattr(Users, field).like('%' + val + '%')


def current_user_from_db(session) -> Users:
    return user_by_alt_id(session, get_jwt_identity())


def user_by_alt_id(session, alt_id):
    return session.query(Users).filter(Users.alternative_id == alt_id).first()
