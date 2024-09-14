import sqlalchemy
from ..db_session import SqlAlchemyBase


class Error(SqlAlchemyBase):
    __tablename__ = 'errors'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    tg_id = sqlalchemy.Column(sqlalchemy.Integer)
    thread_id = sqlalchemy.Column(sqlalchemy.Text)
    full_name = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    model = sqlalchemy.Column(sqlalchemy.Text, default='gpt-4o')
    datetime = sqlalchemy.Column(sqlalchemy.DateTime)
    reqMessage = sqlalchemy.Column(sqlalchemy.Text)
    error = sqlalchemy.Column(sqlalchemy.Text)
    full_error = sqlalchemy.Column(sqlalchemy.Text)