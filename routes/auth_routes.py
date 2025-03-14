from flask import request, jsonify, Flask
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from config import db, api
from models import User
from sqlalchemy.exc import IntegrityError
import re

# Email validation
def is_valid_email(email):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email) is not None

# Username validation
def is_valid_username(username):
    return 3 <= len(username) <= 50

# Password validation
def is_valid_password(password):
    return len(password) >= 6  # You can add more rules like numbers/special characters

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username, email, password = data.get("username"), data.get("email"), data.get("password")

        # Validate input
        if not username or not email or not password:
            return {"error": "Missing required fields"}, 400
        if not is_valid_email(email):
            return {"error": "Invalid email format"}, 400
        if not is_valid_username(username):
            return {"error": "Username must be between 3 and 50 characters"}, 400
        if not is_valid_password(password):
            return {"error": "Password must be at least 6 characters long"}, 400

        try:
            user = User(username=username, email=email.lower())  # Store email in lowercase
            user.password = password  
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

        if not email or not password:
            return {"error": "Email and password are required"}, 400

        user = User.query.filter_by(email=email.lower()).first()  # Case-insensitive search
        if user and user.check_password(password):  # Validate password
            token = create_access_token(identity={"id": user.id, "username": user.username})
            return {"message": "Login successful", "token": token}, 200

        return {"error": "Invalid email or password"}, 401
    
    # Fetching user. 
class ProtectedUser(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        return jsonify(current_user)
