import uuid
import io
import csv
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from jose import jwt
from app.database import get_db
from app.config import settings
from app.models.user import User, RoleEnum
from app.models.academic import Student, Class
from app.models.content import Subject
from app.models.live import LiveClass, LiveAttendance, LiveClassStatusEnum
from app.schemas.live import (
    LiveClassStartRequest, LiveClassResponse, LiveJoinResponse,
    LiveLeaveResponse, LiveEndResponse, LiveAttendanceReport, AttendanceSummary, AttendanceItem
)
from app.api.deps import get_current_user, require_admin

router = APIRouter(prefix="/live", tags=["Live Classes"])

@router.post("/start", response_model=LiveClassResponse, status_code=status.HTTP_201_CREATED)
def start_or_schedule_live(
    req: LiveClassStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    target_class = db.query(Class).filter(Class.id == req.class_id).first()
    if not target_class:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Class not found"})

    sub = db.query(Subject).filter(Subject.id == req.subject_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Subject not found"})

    now = datetime.utcnow()
    scheduled_start = req.scheduled_start or now
    
    # If scheduled for now or within next 5 mins, mark IN_PROGRESS immediately
    is_immediate = (scheduled_start <= now + timedelta(minutes=5))
    initial_status = LiveClassStatusEnum.IN_PROGRESS if is_immediate else LiveClassStatusEnum.SCHEDULED

    room_id = f"eb-{uuid.uuid4().hex[:16]}"

    live = LiveClass(
        class_id=req.class_id,
        subject_id=req.subject_id,
        title=req.title.strip(),
        meeting_room_id=room_id,
        scheduled_start=scheduled_start,
        duration_minutes=req.duration_minutes,
        status=initial_status,
        created_by=current_user.id
    )
    db.add(live)
    db.commit()
    db.refresh(live)

    enrolled = db.query(Student).filter(Student.class_id == req.class_id).count()

    return LiveClassResponse(
        id=live.id,
        class_id=live.class_id,
        subject_id=live.subject_id,
        subject_name=sub.name,
        title=live.title,
        meeting_room_id=live.meeting_room_id,
        scheduled_start=live.scheduled_start,
        duration_minutes=live.duration_minutes,
        status=live.status,
        can_join=True if live.status == LiveClassStatusEnum.IN_PROGRESS else False,
        notified_students=enrolled,
        created_at=live.created_at
    )

@router.get("/upcoming", response_model=List[LiveClassResponse])
def get_upcoming_live_classes(
    include_completed: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(LiveClass).join(Subject)

    if current_user.role == RoleEnum.STUDENT:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            return []
        query = query.filter(LiveClass.class_id == student.class_id)

    if not include_completed:
        query = query.filter(LiveClass.status.in_([LiveClassStatusEnum.IN_PROGRESS, LiveClassStatusEnum.SCHEDULED]))

    # Order by status (IN_PROGRESS first) then scheduled_start
    classes = query.order_by(LiveClass.scheduled_start.asc()).all()

    res = []
    for c in classes:
        enrolled = db.query(Student).filter(Student.class_id == c.class_id).count()
        res.append(LiveClassResponse(
            id=c.id,
            class_id=c.class_id,
            subject_id=c.subject_id,
            subject_name=c.subject.name,
            title=c.title,
            meeting_room_id=c.meeting_room_id,
            scheduled_start=c.scheduled_start,
            duration_minutes=c.duration_minutes,
            status=c.status,
            can_join=True if c.status == LiveClassStatusEnum.IN_PROGRESS else False,
            notified_students=enrolled,
            created_at=c.created_at
        ))
    return res

@router.post("/{id}/join", response_model=LiveJoinResponse)
def join_live_class(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    live = db.query(LiveClass).filter(LiveClass.id == id).first()
    if not live:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Live class not found"})

    if live.status == LiveClassStatusEnum.COMPLETED:
        raise HTTPException(status_code=400, detail={"code": "CLASS_ENDED", "message": "This live class has already ended"})

    if live.status == LiveClassStatusEnum.SCHEDULED:
        # If admin joins, start the class
        if current_user.role in [RoleEnum.SUPER_ADMIN, RoleEnum.TEACHER]:
            live.status = LiveClassStatusEnum.IN_PROGRESS
            db.commit()
        else:
            raise HTTPException(status_code=400, detail={"code": "CLASS_NOT_STARTED", "message": "Class has not started yet"})

    # Check student class
    student = None
    is_moderator = current_user.role in [RoleEnum.SUPER_ADMIN, RoleEnum.TEACHER]

    if current_user.role == RoleEnum.STUDENT:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student or student.class_id != live.class_id:
            raise HTTPException(status_code=403, detail={"code": "NOT_YOUR_CLASS", "message": "You can only join live classes of your enrolled class"})

        # Record attendance
        attendance = db.query(LiveAttendance).filter(LiveAttendance.live_class_id == live.id, LiveAttendance.student_id == student.id).first()
        now = datetime.utcnow()
        if not attendance:
            attendance = LiveAttendance(
                live_class_id=live.id,
                student_id=student.id,
                joined_at=now,
                reconnects=0
            )
            db.add(attendance)
        else:
            attendance.reconnects += 1
            if not attendance.joined_at:
                attendance.joined_at = now
        db.commit()

    # Create Jitsi JWT token claim
    token_claims = {
        "context": {
            "user": {
                "id": current_user.id,
                "name": current_user.full_name,
                "email": current_user.email or f"{current_user.phone_number}@edubridge.org",
                "avatar": ""
            },
            "features": {
                "recording": is_moderator,
                "livestreaming": False,
                "screen-sharing": True
            }
        },
        "aud": "jitsi",
        "iss": "edubridge",
        "sub": settings.JITSI_DOMAIN,
        "room": live.meeting_room_id,
        "moderator": is_moderator,
        "exp": datetime.utcnow() + timedelta(hours=3)
    }
    meeting_jwt = jwt.encode(token_claims, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return LiveJoinResponse(
        provider="jitsi",
        domain=settings.JITSI_DOMAIN,
        room=live.meeting_room_id,
        jwt=meeting_jwt,
        display_name=current_user.full_name,
        start_muted=not is_moderator,
        is_moderator=is_moderator,
        expires_in=3600
    )

@router.post("/{id}/leave", response_model=LiveLeaveResponse)
def leave_live_class(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        return LiveLeaveResponse(message="left", duration_seconds=0)

    attendance = db.query(LiveAttendance).filter(LiveAttendance.live_class_id == id, LiveAttendance.student_id == student.id).first()
    if attendance and attendance.joined_at:
        now = datetime.utcnow()
        attendance.left_at = now
        delta = int((now - attendance.joined_at).total_seconds())
        attendance.duration_seconds += max(0, delta)
        db.commit()
        return LiveLeaveResponse(message="left", duration_seconds=attendance.duration_seconds)

    return LiveLeaveResponse(message="left", duration_seconds=0)

@router.post("/{id}/end", response_model=LiveEndResponse)
def end_live_class(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    live = db.query(LiveClass).filter(LiveClass.id == id).first()
    if not live:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Live class not found"})

    live.status = LiveClassStatusEnum.COMPLETED

    # Close any open attendances
    now = datetime.utcnow()
    open_attendances = db.query(LiveAttendance).filter(LiveAttendance.live_class_id == live.id, LiveAttendance.left_at.is_(None)).all()
    for att in open_attendances:
        att.left_at = now
        delta = int((now - att.joined_at).total_seconds())
        att.duration_seconds += max(0, delta)

    db.commit()

    attendees_count = db.query(LiveAttendance).filter(LiveAttendance.live_class_id == live.id).count()
    return LiveEndResponse(status="COMPLETED", attendees=attendees_count)

@router.get("/{id}/attendance", response_model=LiveAttendanceReport)
def get_live_attendance_report(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    live = db.query(LiveClass).filter(LiveClass.id == id).first()
    if not live:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Live class not found"})

    students = db.query(Student).filter(Student.class_id == live.class_id).order_by(Student.roll_number).all()
    enrolled = len(students)

    items = []
    attended = 0
    total_minutes = 0.0

    for s in students:
        att = db.query(LiveAttendance).filter(LiveAttendance.live_class_id == live.id, LiveAttendance.student_id == s.id).first()
        is_present = att is not None and att.duration_seconds > 0
        if is_present:
            attended += 1
            dur_min = round(att.duration_seconds / 60.0, 1)
            total_minutes += dur_min
        else:
            dur_min = 0.0

        items.append(AttendanceItem(
            student_id=s.id,
            roll_number=s.roll_number,
            student_name=s.user.full_name,
            present=is_present,
            joined_at=att.joined_at if att else None,
            left_at=att.left_at if att else None,
            duration_minutes=dur_min,
            reconnects=att.reconnects if att else 0
        ))

    avg_minutes = round(total_minutes / attended, 1) if attended > 0 else 0.0

    return LiveAttendanceReport(
        live_class={
            "id": live.id,
            "title": live.title,
            "duration_minutes": live.duration_minutes,
            "scheduled_start": live.scheduled_start.isoformat(),
            "status": live.status.value
        },
        summary=AttendanceSummary(
            enrolled=enrolled,
            attended=attended,
            absent=enrolled - attended,
            average_minutes=avg_minutes
        ),
        items=items
    )

@router.get("/{id}/attendance.csv")
def download_live_attendance_csv(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    live = db.query(LiveClass).filter(LiveClass.id == id).first()
    if not live:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Live class not found"})

    students = db.query(Student).filter(Student.class_id == live.class_id).order_by(Student.roll_number).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["roll_number", "student_name", "present", "joined_at", "left_at", "duration_minutes", "reconnects"])

    for s in students:
        att = db.query(LiveAttendance).filter(LiveAttendance.live_class_id == live.id, LiveAttendance.student_id == s.id).first()
        is_present = "YES" if (att and att.duration_seconds > 0) else "NO"
        joined = att.joined_at.isoformat() if att and att.joined_at else ""
        left = att.left_at.isoformat() if att and att.left_at else ""
        dur = round(att.duration_seconds / 60.0, 1) if att else 0.0
        reconnects = att.reconnects if att else 0
        writer.writerow([s.roll_number, s.user.full_name, is_present, joined, left, dur, reconnects])

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=attendance_{live.meeting_room_id}.csv"}
    )
