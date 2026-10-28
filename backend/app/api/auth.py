from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, DeviceToken, RoleEnum
from app.models.academic import Student
from app.schemas.auth import (
    LoginRequest, TokenResponse, UserProfile, StudentProfileInfo,
    ChangePasswordRequest, DeviceRegisterRequest
)
from app.schemas.common import MessageResponse
from app.services.auth_service import verify_password, get_password_hash, create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="", tags=["Auth"])

def build_user_profile(user: User, db: Session) -> UserProfile:
    student_info = None
    if user.role == RoleEnum.STUDENT:
        st = db.query(Student).filter(Student.user_id == user.id).first()
        if st and st.student_class:
            student_info = StudentProfileInfo(
                student_id=st.id,
                class_id=st.class_id,
                grade_level=st.student_class.grade_level,
                section=st.student_class.section,
                roll_number=st.roll_number,
                guardian_name=st.guardian_name,
                guardian_phone=st.guardian_phone
            )
    return UserProfile(
        id=user.id,
        phone_number=user.phone_number,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        last_login_at=user.last_login_at,
        student=student_info
    )

@router.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == req.phone_number.strip()).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Invalid phone number or password"}
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Account has been deactivated"}
        )
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id, "role": user.role.value})
    profile = build_user_profile(user, db)
    return TokenResponse(access_token=token, user=profile)

@router.get("/auth/me", response_model=UserProfile)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return build_user_profile(current_user, db)

@router.post("/auth/change-password", response_model=MessageResponse)
def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_CREDENTIALS", "message": "Incorrect current password"}
        )
    current_user.password_hash = get_password_hash(req.new_password)
    db.commit()
    return MessageResponse(message="Password updated successfully")

@router.post("/devices/register", response_model=MessageResponse)
def register_device(
    req: DeviceRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(DeviceToken).filter(DeviceToken.token == req.token).first()
    if existing:
        existing.user_id = current_user.id
        existing.platform = req.platform
    else:
        new_token = DeviceToken(user_id=current_user.id, token=req.token, platform=req.platform)
        db.add(new_token)
    db.commit()
    return MessageResponse(message="Device registered for push notifications")

@router.delete("/devices/{token}", response_model=MessageResponse)
def unregister_device(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(DeviceToken).filter(DeviceToken.token == token, DeviceToken.user_id == current_user.id).delete()
    db.commit()
    return MessageResponse(message="Device token removed")
