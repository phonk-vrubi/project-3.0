"""Модуль содержит основные обработчики тех страниц, которые будут видеть
обычные пользователи."""

import logging
import urllib
import urllib.parse

import flask
from flask import (Blueprint, render_template, redirect, url_for, abort,
                   make_response)
from flask_jwt_extended import (
    jwt_required, current_user, jwt_refresh_token_required
)
from flask_mail import Message

from app.api_utils import (
    WrongUserDataError, login_user, logout_user, register_user, get_user_token,
    verify_email_by_token
)
from app.api_utils import refresh_user
from app.email_utils import send_msg_in_thread
from app.forms import *
from modules import constants

blueprint = Blueprint('main', __name__)


@blueprint.route('/refresh', methods=['GET'])
@jwt_refresh_token_required
def refresh():
    next_ = flask.request.args.get('next', url_for('main.index'))
    r = make_response(redirect(next_))
    refresh_user(r)
    return r


@blueprint.route('/index', methods=['POST', 'GET'])
@blueprint.route('/', methods=['POST', 'GET'])
@jwt_required
def index():
    param = {
        'title': 'PyMessages'
    }
    return render_template('index.jinja2', **param)


@blueprint.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        r = make_response(redirect(url_for('main.index')))
        try:
            login_user(email, password, r)
        except WrongUserDataError:
            param = {
                'title': 'Войти в PyMessages',
                'form': form,
                'error_msg': 'Неверный логин или пароль'
            }
            return render_template('login.jinja2', **param)
        return r
    param = {
        'title': 'Войти в PyMessages',
        'form': form,
    }
    return render_template('login.jinja2', **param)


@blueprint.route('/logout', methods=['GET'])
def logout():
    next_ = flask.request.args.get('next', url_for('main.login'))
    r = make_response(redirect(next_))
    logout_user(r)
    return r


@blueprint.route('/register', methods=['POST', 'GET'])
def register():
    if current_user:
        return redirect('/')
    title = 'Регистрация в PyMessages'
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        data = {
            'first_name': form.first_name.data,
            'second_name': form.second_name.data,
            'email': email,
            'password': password
        }
        if register_user(data):
            # Сохраняем email в сессии, чтобы дать пользователю ссылку на его
            # почтовый ящик на странице подтверждения email
            flask.session['email'] = email

            # Получаем токен, по которому будем подтверждать email пользователя
            # и отправляем ему ссылку с подтверждением на email
            token = get_user_token(email, password)
            msg = Message('Подтвердите свой email - PyMessages',
                          recipients=[email])
            mail_param = {
                'verify_url': url_for('main.verify_email', token=token,
                                      _external=True)
            }
            msg.html = render_template('verify_email_msg.jinja2', **mail_param)
            # Если не удалось отправить сообщение, то выводим сообщение об
            # ошибке, получателя и текст письма для отладки
            try:
                send_msg_in_thread(msg)
            except Exception as e:
                log_msg = (
                    'Возникло исключение при отправке письма: \n%s\n'
                    'Вероятнее всего, вы забыли настроить конфиг приложения.\n'
                    'Чтобы настроить конфиг, перейдите в файл app/config.py и '
                    'заполните все необходимые поля.'
                )
                logging.warning(log_msg, e)
                logging.debug(email + '\n' + msg.html)
            # Отправляем пользователя на страницу с просьбой проверить почту
            return redirect(url_for('main.verify_email', token=''))
        else:
            param = {
                'title': title,
                'form': form,
                'error_msg': 'Произошла непредвиденная ошибка. '
                             'Попробуйте ещё раз.'
            }
            return render_template('register.jinja2', **param)
    param = {
        'title': title,
        'form': form,
    }
    return render_template('register.jinja2', **param)


@blueprint.route('/verify_email/')
def verify_email_message():
    if current_user:
        return redirect('/')
    # Если пользователь только что создал аккаунт и указал рабочую почту, то
    # просим его перейти в почтовый ящик и подтвердить почту
    email = flask.session.get('email')
    if email and '@' in email:
        mail_domain = email[email.index('@') + 1:]
        # Ищем URL почты пользователя,
        email_server = constants.MAIL_DOMAINS_URLS.get(mail_domain)
        # если не находим, даём ссылку на домен почты
        if email_server:
            email_server = urllib.parse.urlunsplit(
                ('http', mail_domain, *[''] * 3)
            )
    else:
        abort(403)
        return
    param = {
        'title': 'Подтвердите email - PyMessages',
        'email_server': email_server,
    }
    return render_template('verify_email.jinja2', **param)


@blueprint.route('/verify_email/<string:token>')
def verify_email(token):
    if current_user:
        return redirect('/')
    if verify_email_by_token(token):
        param = {
            'title': 'Email подтверждён - PyMessages',
        }
        return render_template('email_verified.jinja2', **param)
    abort(403)


@blueprint.route('/profile', methods=['GET', 'POST'])
@jwt_required
def profile():
    title = 'Профиль - PyMessages'
    info_form = ChangeProfileInfoForm(prefix='info')
    security_form = ChangeProfileSecurityForm(prefix='security')
    if info_form.validate_on_submit() and info_form.submit.data:
        current_user.first_name = info_form.first_name.data
        current_user.second_name = info_form.second_name.data
        current_user.phone_number = info_form.phone_number.data
        current_user.age = info_form.age.data
        current_user.city = info_form.city.data
        current_user.additional_inf = info_form.additional_inf.data
        current_user.set_avatar(info_form.avatar.data)
        current_user.commit()
        param = {
            'title': title,
            'info_form': info_form,
            'security_form': security_form,
            'info_error_msg': None,
            'info_success_msg': 'Данные успешно изменены',
            'current_tab': '#profileInfoTab'
        }
        return render_template('profile.jinja2', **param)
    elif security_form.validate_on_submit() and security_form.submit.data:
        if security_form.password.data != security_form.repeat_password.data:
            param = {
                'title': title,
                'info_form': info_form,
                'security_form': security_form,
                'security_error_msg': 'Пароли не совпадают',
                'security_success_msg': None,
                'current_tab': '#profileSecurityTab'
            }
            return render_template('profile.jinja2', **param)
        email = security_form.email.data
        password = security_form.password.data
        old_password = security_form.old_password.data
        current_user.email = email
        current_user.password = password
        cur_email = email or current_user.email
        cur_password = password or old_password
        if current_user.commit(old_password=old_password):
            param = {
                'title': title,
                'info_form': info_form,
                'security_form': security_form,
                'security_error_msg': None,
                'security_success_msg': 'Данные успешно изменены',
                'current_tab': '#profileSecurityTab'
            }
            logged_r = make_response()
            login_user(cur_email, cur_password, logged_r)
            r = make_response(render_template('profile.jinja2', **param))
            r.headers = logged_r.headers
            return r
        else:
            param = {
                'title': title,
                'info_form': info_form,
                'security_form': security_form,
                'security_error_msg': 'Неверный пароль',
                'security_success_msg': None,
                'current_tab': '#profileSecurityTab'
            }
            return render_template('profile.jinja2', **param)
    info_form.first_name.data = current_user.first_name
    info_form.second_name.data = current_user.second_name
    info_form.phone_number.data = current_user.phone_number
    info_form.age.data = current_user.age
    info_form.city.data = current_user.city
    info_form.additional_inf.data = current_user.additional_inf

    param = {
        'title': 'Профиль - PyMessages',
        'info_form': info_form,
        'security_form': security_form
    }
    return render_template('profile.jinja2', **param)


@blueprint.route('/friends')
@jwt_required
def friends():
    param = {
        'title': 'Друзья - PyMessages',
    }
    return render_template('friends.jinja2', **param)
