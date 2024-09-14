import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
from sqlalchemy import URL
import os

SqlAlchemyBase = orm.declarative_base()

__factory = None


def global_init():
    global __factory

    if __factory:
        return
    conn_str = URL(
        'postgresql+psycopg2',
        username=os.getenv('DATABASE_USERNAME'),
        password=os.getenv('DATABASE_PASSWORD'),
        host=os.getenv('DATABASE_HOST'),
        database=os.getenv('DATABASE_NAME'),
        port=os.getenv('DATABASE_PORT'),
        query={}
    )
    print(conn_str, os.getenv('DATABASE_PASSWORD'))
    engine = sa.create_engine(conn_str, pool_size=0, max_overflow=0, pool_pre_ping=True)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models


    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
