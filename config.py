import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
class Config:
    """Base configuration class."""
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://learn_db_60lp_user:jhxk4lcw9nD2QnrjquV8sf9fboTmdnPs@dpg-cv4mijlds78s73e0osj0-a.oregon-postgres.render.com/learn_db_60lp")

    #SQLALCHEMY_DATABASE_URI = os.getenv("postgresql://learn_db_60lp_user:jhxk4lcw9nD2QnrjquV8sf9fboTmdnPs@dpg-cv4mijlds78s73e0osj0-a.oregon-postgres.render.com/learn_db_60lp", )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_secret_key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=10)  
    CORS_RESOURCES = {r"/": {"origins": ""}}


# Flask Extensions (initialized without app to enable factory pattern)
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
api = Api()
jwt = JWTManager()

def init_extensions(app):
    """Initialize extensions with the Flask app."""
    db.init_app(app)
    api.init_app(app)
    jwt.init_app(app)
    CORS(app, supports_credentials=True, resources=Config.CORS_RESOURCES)