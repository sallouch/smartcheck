# test_services.py
from services.qr_code_service import QRCodeService

qr_service = QRCodeService()

# Test generating a QR for session 1
result = qr_service.generate_qr(1)
print("Generate QR result:", result)

# Test scanning the QR with a student
if result.get("success"):
    qr_token = result["qr_token"]
    scan_result = qr_service.scan_qr(qr_token, 1)
    print("Scan QR result:", scan_result)

