from flask_sqlalchemy import declarative_base
from app import db

#反射到现有数据库


class Group(db.Model):
    __tablename__ = "group_info"
    _id = db.Column(db.Integer,primary_key=True,index=True)
    group_link = db.Column(db.String(400),unique=True)
    group_name = db.Column(db.String(200))
    group_intruduction = db.Column(db.String(200))

    def __repr__(self):
        return '<Reply {}>'.format(self._id)


