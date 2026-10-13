from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False, default="User")

    # Profile & biometric fields
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)  # male, female, other
    height_cm = db.Column(db.Float, nullable=True)
    current_weight_kg = db.Column(db.Float, nullable=True)
    target_weight_kg = db.Column(db.Float, nullable=True)
    activity_level = db.Column(
        db.String(30), nullable=True
    )  # sedentary, light, moderate, active, very_active

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    meals = db.relationship("Meal", backref="user", lazy=True, cascade="all, delete-orphan")
    daily_goals = db.relationship("DailyGoal", backref="user", lazy=True, cascade="all, delete-orphan")
    diet_plans = db.relationship("DietPlan", backref="user", lazy=True, cascade="all, delete-orphan")
    conversations = db.relationship("Conversation", backref="user", lazy=True, cascade="all, delete-orphan")
    reminders = db.relationship("Reminder", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def is_profile_complete(self) -> bool:
        required = [self.age, self.gender, self.height_cm, self.current_weight_kg, self.activity_level]
        return all(r is not None for r in required)

    def missing_profile_fields(self) -> list[str]:
        missing = []
        if self.age is None:
            missing.append("age")
        if not self.gender:
            missing.append("gender")
        if self.height_cm is None:
            missing.append("height (cm)")
        if self.current_weight_kg is None:
            missing.append("current weight (kg)")
        if not self.activity_level:
            missing.append("activity level (sedentary, light, moderate, active)")
        if self.target_weight_kg is None:
            missing.append("target weight (kg)")
        return missing

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "height_cm": self.height_cm,
            "current_weight_kg": self.current_weight_kg,
            "target_weight_kg": self.target_weight_kg,
            "activity_level": self.activity_level,
            "is_profile_complete": self.is_profile_complete(),
            "missing_fields": self.missing_profile_fields(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
