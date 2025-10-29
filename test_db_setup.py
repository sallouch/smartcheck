# test_db_setup.py
from database import ensure_schema, add_user, get_all_users, generate_qr_code, add_session, scan_qr_and_mark_presence, get_students_by_presence

def smoke_test():
    print("Ensuring schema...")
    ensure_schema()

    print("Adding a test teacher and student...")
    add_user("Prof", "Test", "prof@test.local", "pass", "enseignant", cin="22226123")
    add_user("Student", "Demo", "student@test.local", "pass", "etudiant", cin="55555123")

    users = get_all_users()
    print("Users:", users)

    # create a dummy matiere/class row first in DB or rely on existing IDs.
    # For a quick smoke test assume matiere id=1, classe id=1 (adjust if not present)
    add_session(1, 1, 1, "2025-10-29", "08:00", "10:00")
    code = generate_qr_code(1, expire_seconds=30)
    print("Generated QR:", code)

    # scan as student id 2 (if IDs match)
    ok = scan_qr_and_mark_presence(2, code)
    print("Scan result:", ok)
    print("Present students for session 1:", get_students_by_presence(1, present=1))

if __name__ == "__main__":
    smoke_test()
