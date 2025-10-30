# test_repositories.py
from database.user_repository import add_user, get_all_users, get_user_by_email
from database.attendance_repository import add_session, get_all_sessions
from database.qr_code_repository import insert_qr_code, get_qr_by_code, deactivate_qr, get_all_qr_codes
from database.token_repository import save_token, get_token, delete_token
from database import ensure_schema
from datetime import datetime, timedelta

def test_all_repositories():
    print("=== Ensuring schema ===")
    ensure_schema()

    print("\n=== Testing User Repository ===")
    add_user("Alice", "Marie", "alice@example.com", "pass123", "etudiant", "12345678")
    add_user("Bob", "Jean", "bob@example.com", "pass456", "enseignant", "87654321")
    users = get_all_users()
    print("All users:", users)
    user = get_user_by_email("alice@example.com")
    print("Get user by email:", user)

    print("\n=== Testing Session Repository ===")
    # Assuming matiere_id=1, classe_id=1, enseignant_id=2 exist
    add_session(1, 1, 2, "2025-10-30", "09:00", "11:00")
    sessions = get_all_sessions()
    print("All sessions:", sessions)

    print("\n=== Testing QR Code Repository ===")
    now = datetime.now()
    expire_time = now + timedelta(seconds=10)
    insert_qr_code(
        id_seance=1,
        code="TESTQR123",
        date_generation=now.strftime("%Y-%m-%d %H:%M:%S"),
        expire_le=expire_time.strftime("%Y-%m-%d %H:%M:%S"),
        actif=1
    )
    qr = get_qr_by_code("TESTQR123")
    print("Fetched QR code:", qr)
    all_qrs = get_all_qr_codes()
    print("All QR codes:", all_qrs)
    if qr:
        deactivate_qr(qr[0])
    print("QR after deactivation:", get_qr_by_code("TESTQR123"))

    print("\n=== Testing Token Repository ===")
    expires_at = (datetime.utcnow() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    save_token(user_id=1, role="etudiant", token="TOKEN123", expires_at=expires_at)
    token_info = get_token("TOKEN123")
    print("Token fetched:", token_info)
    deleted = delete_token("TOKEN123")
    print("Token deleted:", deleted)
    token_info_after = get_token("TOKEN123")
    print("Token after deletion:", token_info_after)

if __name__ == "__main__":
    test_all_repositories()
