import sqlalchemy
from ..db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    tg_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    thread_id = sqlalchemy.Column(sqlalchemy.Text)
    full_name = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    model = sqlalchemy.Column(sqlalchemy.Text, default='gpt-4o')
    created_date = sqlalchemy.Column(sqlalchemy.DateTime)
    last_activity = sqlalchemy.Column(sqlalchemy.DateTime)