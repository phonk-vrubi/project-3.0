import typing
from functools import lru_cache, wraps

from wtforms import Field


@lru_cache()  # Кэшируем результаты, дабы не плодить миллионы классов
def named_flask_form_field(wtforms_field: typing.ClassVar[Field]):
    """Принимает на вход класс поля wtforms.Field, возвращает унаследованный от
    этого класса поля класс с полем label_name, содержащий параметр label,
    который передаётся в конструктор класса.
    
    :param wtforms_field: класс поля wtforms.Field, от которого нужно
    наследоваться.
    """

    class NamedFlaskForm(wtforms_field):
        @wraps(wtforms_field.__init__)
        def __init__(self, label, *args, **kwargs):
            self.label_name = label
            super().__init__(label, *args, **kwargs)

    return NamedFlaskForm
