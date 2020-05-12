"""Модуль, содержащий все конфигруации приложения."""
import os

from modules import constants


class Config:
    JWT_TOKEN_LOCATION = ('cookies', 'json', 'query_string')
    JWT_ERROR_MESSAGE_KEY = 'message'
    WTF_CSRF_CHECK_DEFAULT = False
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_SESSION_COOKIE = False

    # Параметр ниже отвечает за то, будут ли куки отправляться только по
    # протоколу HTTPS. В данный момент у приложения нет сертификата, так что
    # параметр равен False. Но при запуске приложения на прод, то крайне
    # желательно поставить True, т.к. иначе злоумышленник сможет похитить ключ
    # доступа JWT_COOKIE_SECURE = True

    # Ограничиваем максимальный размер загружаемого файла до 16 МБ
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 1  # Значение в секундах
    UPLOAD_FOLDER = constants.UPLOAD_PATH


class DevelopmentConfig(Config):
    SECRET_KEY = JWT_SECRET_KEY = 'py_messages_test_secret_key'
    ENV = 'development'
    DEBUG = True

    # Пока на всех страницах сделан костыль, который в качестве API
    # сервера выставляет текущий URL, дабы была возможность тестировать через
    # ngrok
    API_SERVER = 'http://localhost:5000'

    # Для рассылки email, необходимо заполнить следующие поля:
    # MAIL_SERVER =
    # MAIL_PORT =
    # MAIL_USE_TLS =
    # MAIL_USE_SSL =
    # MAIL_USERNAME =
    # MAIL_PASSWORD =
    # MAIL_DEFAULT_SENDER =
    # При тестировании приложения эти поля можно не заполнять, тогда сообщение
    # и получатель будут выведены в журнал


# Во время конфигурации Flask не создаёт экземпляры классов конфигураций, а
# использует сами классы. Чтобы динамически присвоить полям класса значения
# динамически (фактически создать объект класса на лету), приходится
# использовать метаклассы

# Коротко о метаклассах:
# Объект - экземпляр класса
# Класс - экзепляр метакласса

class _EnvConfigMetaclass(type):
    """Метакласс класса EnvConfig. Создаёт все необходимые поля по описанному в
    классе EnvConfig способу."""

    def __new__(mcs, cls_name, bases, cls_attrs):

        if flask_vars := os.environ.get('APP_ENV_VARS'):
            flask_vars_list = flask_vars.split(',')
            for flask_var in flask_vars_list:
                flask_var = flask_var.strip()
                if value := os.environ.get(flask_var):
                    cls_attrs[flask_var] = eval(value)
        return super(_EnvConfigMetaclass, mcs).__new__(
            mcs, cls_name, bases, cls_attrs
        )


class EnvConfig(Config, metaclass=_EnvConfigMetaclass):
    """Конфигурация из переменных среды. В переменной среды APP_ENV_VARS через
    запятую перечисляются переменные среды, которые будут использованы для
    конфигурации приложения. Во время создания класса (в метаклассе
    _EnvConfigMetaclass) значение каждой перечисленной переменной
    выполняется как выражение Python с помощью функции eval(), а затем
    полученные значения присваиваются соотвествующим полям этого класса.

    :Example:

    В консоли / терминале
    set APP_CONFIG = app.config.EnvConfig
    set APP_ENV_VARS = SECRET_KEY, DEBUG
    set SECRET_KEY = 'SUPER_SECRET_KEY'
    set DEBUG = True
    В коде приложения
    >>> EnvConfig.SECRET_KEY
    'SUPER_SECRET_KEY'
    >>> EnvConfig.DEBUG
    True
    """
