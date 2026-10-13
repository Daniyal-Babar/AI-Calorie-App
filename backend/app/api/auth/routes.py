from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from pydantic import ValidationError
from app.extensions import db
from app.models.user import User
from app.schemas.user_schema import RegisterSchema, LoginSchema, ProfileUpdateSchema
from app.services.email_service import EmailService

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    try:
        validated = RegisterSchema(**data)
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 422

    if User.query.filter_by(email=validated.email).first():
        return jsonify({"error": "An account with this email already exists."}), 409

    user = User(email=validated.email, name=validated.name or "User")
    user.set_password(validated.password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "message": "User registered successfully",
        "token": token,
        "user": user.to_dict(),
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    try:
        validated = LoginSchema(**data)
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 422

    user = User.query.filter_by(email=validated.email).first()
    if not user or not user.check_password(validated.password):
        return jsonify({"error": "Invalid email or password."}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": user.to_dict(),
    }), 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200

@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json() or {}
    try:
        validated = ProfileUpdateSchema(**data)
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 422

    for key, val in validated.model_dump(exclude_unset=True).items():
        setattr(user, key, val)

    db.session.commit()
    return jsonify({"message": "Profile updated", "user": user.to_dict()}), 200

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() or {}
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        EmailService.send_password_reset(email, "mock-reset-token-12345")

    return jsonify({"message": "If an account exists, password reset instructions have been sent."}), 200

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    # Stateless JWT logout acknowledged
    return jsonify({"message": "Logged out successfully"}), 200
