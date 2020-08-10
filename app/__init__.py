from flask import Flask
from config import Config,redis_key
from flask_sqlalchemy import SQLAlchemy
from flask_redis import  FlaskRedis
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.debug = True
redis_store = FlaskRedis(app)
redis_key = redis_key
from app import routes
