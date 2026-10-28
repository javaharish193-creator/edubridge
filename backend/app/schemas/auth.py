from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.user import RoleEnum

class LoginRequest(BaseModel):
    phone_number: str
    password: str

class StudentProfileInfo(BaseModel):
    student_id: str
    class_id: str
    grade_level: int
    section: str
    roll_number: str
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None

class UserProfile(BaseModel):
    id: str
    phone_number: str
    email: Optional[str] = None
    full_name: str
    role: RoleEnum
    is_active: bool
    last_login_at: Optional[datetime] = None
    student: Optional[StudentProfileInfo] = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 604800
    user: UserProfile

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)

class DeviceRegisterRequest(BaseModel):
    token: str
    platform: str = "android"
