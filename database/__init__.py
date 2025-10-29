from .db_connection import get_connection, ensure_schema
from .user_repository import (
    add_user, get_all_users, get_user_by_email
)
from .attendance_repository import (
    add_session, get_all_sessions, get_sessions_by_teacher,
    add_presence, get_presences_by_session, get_students_by_presence
)
from .qr_code_repository import generate_qr_code, scan_qr_and_mark_presence

__all__ = [
    "get_connection", "ensure_schema",
    "add_user", "get_all_users", "get_user_by_email",
    "add_session", "get_all_sessions", "get_sessions_by_teacher",
    "add_presence", "get_presences_by_session", "get_students_by_presence",
    "generate_qr_code", "scan_qr_and_mark_presence"
]
