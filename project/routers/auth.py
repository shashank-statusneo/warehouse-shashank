import settings
from project import db, jwt
from project.schema_validators.auth import SignUpSchema, LogInSchema, UpdateProfile
from flask import Blueprint
from project.models.auth import User, TokenBlocklist

from flask import request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)

from project.managers import AuthManager

auth_router = Blueprint('auth', __name__)


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None


@auth_router.route('/signup', methods=["POST"])
def signup():
    data = request.json
    schema = SignUpSchema()
    try:
        data = schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user, error_data = AuthManager.create_new_user(data)
    if not user:
        return jsonify(error_data), 409
    return jsonify(id=user.id), 201


@auth_router.route('/login', methods=['POST'])
def login():
    data = request.json
    schema = LogInSchema()
    try:
        data = schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    token, status_code = AuthManager.get_token(data)
    return jsonify(token), status_code


@auth_router.route('/refresh', methods=['GET'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token, expire_in=60 * settings.TOKEN_EXPIRE_IN)


@auth_router.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    if request.method == "GET":
        return jsonify(AuthManager.get_current_user_profile()), 200
    data = request.json
    schema = UpdateProfile()
    try:
        data = schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    AuthManager.update_user_profile(data)
    return jsonify(status="success"), 200

# @auth_router.route('/change_password', methods=['PUT'])
# @jwt_required()
# def change_password():
#     data = request.json
#     schema = UpdatePassword()
#     try:
#         data = schema.load(data)
#     except ValidationError as err:
#         return jsonify(err.messages), 400
#
#     user = get_user()
#     if check_password_hash(user.password, data['old_password']):
#         if check_password_hash(user.password, data['new_password']):
#             return make_response('new password can not same as old password', 403)
#         user.password = generate_password_hash(data['new_password'])
#         db.session.commit()
#         return jsonify({"status": "success"}), 200
#     return make_response('Old password is invalid', 403)
#

@auth_router.route("/logout", methods=["DELETE"])
@jwt_required(verify_type=False)
def logout():
    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"]
    db.session.add(TokenBlocklist(jti=jti, type=ttype))
    db.session.commit()
    return jsonify(msg=f"{ttype.capitalize()} token successfully revoked")
