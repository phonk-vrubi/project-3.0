import logging
import os

import sqlalchemy as sa
import sqlalchemy.ext.declarative as dec
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session


SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    db_file = db_file.strip()

    if not db_file:
        raise Exception("Необходимо указать файл базы данных.")

    # Если директории, в которой должна лежать БД, не существует, то создаём её
    db_file_dir = os.path.dirname(db_file)
    if not os.path.exists(db_file_dir):
        os.makedirs(db_file_dir)

    conn_str = f'sqlite:///{db_file}?check_same_thread=False'
    logging.info(f"Подключение к базе данных по адресу {conn_str}")
    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    # noinspection PyUnresolvedReferences
    from . import __all_models

    # Импортируем файл здесь, чтобы не произошло циклического импорта
    from . import additives_types_setting

    SqlAlchemyBase.metadata.create_all(engine)

    additives_types_setting.set_types_table()


def create_session() -> Session:
    global __factory
    return __factory()
