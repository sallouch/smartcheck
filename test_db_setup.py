# test_db_setup.py
from database import ensure_schema, add_user, get_all_users, add_session,insert_qr_code,get_qr_by_code,deactivate_qr,get_all_qr_codes
from datetime import datetime, timedelta
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

def test_qrcode_repository():
    print("Ensuring database schema...")
    ensure_schema()

    # Generate sample QR data
    session_id = 1
    code = "TESTQR1"
    now = datetime.now()
    expire_time = now + timedelta(minutes=5)

    print("Inserting QR code...")
    inserted = insert_qr_code(
        id_seance=session_id,
        code=code,
        date_generation=now.strftime("%Y-%m-%d %H:%M:%S"),
        expire_le=expire_time.strftime("%Y-%m-%d %H:%M:%S"),
        actif=1
    )
    print("Inserted:", inserted)

    print(" Fetching QR code by code...")
    qr = get_qr_by_code(code)
    print("QR fetched:", qr)

    print("Listing all QR codes...")
    all_qrs = get_all_qr_codes()
    print("All QR codes:", all_qrs)

    print("Deactivating QR code...")
    if qr:
        deactivated = deactivate_qr(qr[0])  # qr[0] = id
        print("Deactivated:", deactivated)

        qr_after = get_qr_by_code(code)
        print("QR after deactivation:", qr_after)

    print("Test complete.")


if __name__ == "__main__":
    smoke_test()
    test_qrcode_repository()
