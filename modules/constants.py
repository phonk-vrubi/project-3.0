"""Модуль содержит большинство констант."""
import datetime
import os

# Выделил родительскую директорию в отдельную переменную, дабы при перемещении
# этого файла в PyCharm путь автоматически менялся (если сразу передать путь в
# функцию ниже, то PyCharm его не распознает как путь)
__parent_dir = '..'
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        __parent_dir))

LOGGING_CONFIG_FILE = os.path.join(ROOT_DIR, 'logging.ini')

# # Перевод ошибок wtforms
WTFORMS_ERRORS_TRANSLATION = {
    'Not a valid integer value': 'Указано не число'
}

# Ссылки в подвале на главной странице
PAGE_NAV_LINKS = {
    'Главная': 'main.index',
    'Вход': 'main.login',
    'Регистарция': 'main.register',
    'Профиль': 'main.profile',
    'Друзья': 'main.friends',
    'Выйти': 'main.logout'
}

# URL почт по доменам. Необходимо, чтобы при регистрации отсылать пользователя
# в его почтовый ящик
MAIL_DOMAINS_URLS = {
    "mail.ru": "https://e.mail.ru/",
    "bk.ru": "https://e.mail.ru/",
    "list.ru": "https://e.mail.ru/",
    "inbox.ru": "https://e.mail.ru/",
    "yandex.ru": "https://mail.yandex.ru/",
    "ya.ru": "https://mail.yandex.ru/",
    "yandex.ua": "https://mail.yandex.ua/",
    "yandex.by": "https://mail.yandex.by/",
    "yandex.kz": "https://mail.yandex.kz/",
    "yandex.com": "https://mail.yandex.com/",
    "gmail.com": "https://mail.google.com/",
    "googlemail.com": "https://mail.google.com/",
    "outlook.com": "https://mail.live.com/",
    "hotmail.com": "https://mail.live.com/",
    "live.ru": "https://mail.live.com/",
    "live.com": "https://mail.live.com/",
    "me.com": "https://www.icloud.com/",
    "icloud.com": "https://www.icloud.com/",
    "rambler.ru": "https://mail.rambler.ru/",
    "yahoo.com": "https://mail.yahoo.com/",
    "ukr.net": "https://mail.ukr.net/",
    "i.ua": "http://mail.i.ua/",
    "bigmir.net": "http://mail.bigmir.net/",
    "tut.by": "https://mail.tut.by/",
    "inbox.lv": "https://www.inbox.lv/",
    "mail.kz": "http://mail.kz/"
}

ADDITIVE_TYPES_TITLES = ('photo', 'video', 'audio', 'sticker', 'file')

USER_DATA_PATH = os.path.join(ROOT_DIR, 'user_data')

DB_PATH = os.path.join(USER_DATA_PATH, 'db/messenger.sqlite3')
UPLOAD_PATH = os.path.join(USER_DATA_PATH, 'upload')

ALLOWED_PHOTO_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3'}

ALLOWED_PHOTO_EXTENSIONS_HTML = ','.join({
    f'image/{ext}' for ext in ALLOWED_PHOTO_EXTENSIONS
})
ALLOWED_VIDEO_EXTENSIONS_HTML = ','.join({
    f'video/{ext}' for ext in ALLOWED_VIDEO_EXTENSIONS
})
ALLOWED_AUDIO_EXTENSIONS_HTML = ','.join({
    f'audio/{ext}' for ext in ALLOWED_AUDIO_EXTENSIONS
})

JWT_LIVE_TIME = datetime.timedelta(days=1)

# Максимальное кол-во пользователей, которое вернёт UsersListResource при GET
# запросе
USERS_LIST_RESOURCE_GET_COUNT = 20

USER_DEFAULT_AVATAR = 'avatar.jpg'

DOCS_BASE_TEMPLATE = 'docs_inherited.jinja2'
