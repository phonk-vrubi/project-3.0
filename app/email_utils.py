"""Модуль для отправки email через текущее приложение."""

import threading

from flask import current_app
from flask_mail import Message, Mail

from app.setup_app import mail


def send_msg_in_thread(msg: Message, mail_obj: Mail = mail):
    """Отправить в отдельном потоке email, используя прикреплённый к текущему
    приложению (либо переданный в параметрах) объёкт flask_mail.Mail."""
    thread = threading.Thread(target=send_msg(msg, mail_obj))
    thread.start()
    return thread


def send_msg(msg: Message, mail_obj: Mail = mail):
    """Отправить email, используя прикреплённый к текущему приложению (либо
    переданный в параметрах) объёкт flask_mail.Mail."""
    with current_app.app_context():
        mail_obj.send(msg)
