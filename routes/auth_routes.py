

from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
import re
from config import db, api
from models import User

def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username, email, password = data.get("username"), data.get("email"), data.get("password")

        if not username or not email or not password:
            return {"error": "Missing required fields"}, 400

        if not is_valid_email(email):
            return {"error": "Invalid email format"}, 400

        try:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return {"message": "User registered successfully"}, 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Username or email already exists"}, 409


class Login(Resource):
    def post(self):
        data = request.get_json()
        email, password = data.get("email"), data.get("password")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            token = create_access_token(identity={"id": user.id, "username": user.username})
            return {"message": "Login successful", "token": token}, 200

        return {"error": "Invalid email or password"}, 401

api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")