from .db_connection import get_connection, ensure_schema
from .user_repository import (
    add_user, get_all_users, get_user_by_email
)
from .attendance_repository import (
    add_session, get_all_sessions, get_sessions_by_teacher,
    add_presence, get_presences_by_session, get_students_by_presence
)

from .qr_code_repository import (
    insert_qr_code,
    get_qr_by_code,
    deactivate_qr,
    get_all_qr_codes,
)

__all__ = [
    "get_connection", "ensure_schema",
    "add_user", "get_all_users", "get_user_by_email",
    "add_session", "get_all_sessions", "get_sessions_by_teacher",
    "add_presence", "get_presences_by_session","get_students_by_presence",
    "insert_qr_code", "get_qr_by_code", "deactivate_qr", "get_all_qr_codes",
]
