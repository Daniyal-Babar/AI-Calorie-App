from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class RegisterSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: Optional[str] = "User"

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class ProfileUpdateSchema(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=10, le=120)
    gender: Optional[str] = None  # male, female, other
    height_cm: Optional[float] = Field(None, ge=50, le=300)
    current_weight_kg: Optional[float] = Field(None, ge=20, le=500)
    target_weight_kg: Optional[float] = Field(None, ge=20, le=500)
    activity_level: Optional[str] = None  # sedentary, light, moderate, active, very_active
