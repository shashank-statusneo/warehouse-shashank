import settings

from project.models.auth import User
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity
)
from project import db
from project.utils import update_model_object, remove_unwanted_keys
from werkzeug.security import generate_password_hash, check_password_hash


class AuthManager:

    @classmethod
    def get_current_user(cls):
        identity = get_jwt_identity()
        if identity:
            return User.query.filter_by(id=identity["user_id"]).first()
        return None

    @classmethod
    def get_current_user_profile(cls):
        identity = get_jwt_identity()
        user = User.query.filter_by(id=identity["user_id"]).first()
        return {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "username": user.username,
            "gender": user.gender,
            "address": user.address,
            "mobile_number": user.mobile_number
        }

    @classmethod
    def create_new_user(cls, user_data):
        error_data = {}
        user_by_email = User.query.filter_by(email=user_data["email"]).first()
        user_by_username = User.query.filter_by(username=user_data["username"]).first()
        if user_by_email or user_by_username:
            param = "username" if user_by_username else "email"
            error_data["msg"] = f"user already exists with provided {param}"
        else:
            user_data["password"] = generate_password_hash(user_data["password"])
            user = User(**user_data)
            db.session.add(user)
            db.session.commit()
            return user, error_data
        return None, error_data

    @classmethod
    def update_user_profile(cls, user_data):
        identity = get_jwt_identity()
        user = User.query.filter_by(id=identity["user_id"]).first()
        update_model_object(user, user_data)
        db.session.commit()

    @classmethod
    def get_token(cls, login_data):
        email_or_username = login_data.get("username") or login_data.get("email")
        user = db.session.query(User).filter(
            (User.email == email_or_username) | (User.username == email_or_username)).first()
        if not user:
            return {"msg": f"user not found with {email_or_username}"}, 403

        if check_password_hash(user.password, login_data['password']):
            access_token = create_access_token(identity={"user_id": user.id})
            refresh_token = create_refresh_token(identity={"user_id": user.id})
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expire_in": settings.TOKEN_EXPIRE_IN * 60
            }, 200
        return {"msg": "wrong password"}, 403
