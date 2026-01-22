import hmac
import hashlib
import time
import frappe


def verify_uber_webhook(secret: str):
    # 1. Get headers
    signature = frappe.request.headers.get("X-Uber-Signature")
    timestamp = frappe.request.headers.get("X-Uber-Timestamp")

    # if not signature or not timestamp:
    #     frappe.throw("Missing Uber webhook headers", frappe.PermissionError)

    # # 2. Replay attack protection (5 minutes)
    # now = int(time.time())
    # if abs(now - int(timestamp)) > 300:
    #     frappe.throw("Webhook timestamp expired", frappe.PermissionError)

    # 3. Get RAW body
    raw_body = frappe.request.data
    if isinstance(raw_body, bytes):
        raw_body = raw_body.decode("utf-8")

    # 4. Create signed payload
    signed_payload = f"{raw_body}"

    # 5. Generate expected signature
    expected_signature = hmac.new(
        secret.encode("utf-8"), signed_payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    print(expected_signature)
    print(signature)

    # 6. Constant-time comparison
    if not hmac.compare_digest(expected_signature, signature):
        frappe.throw("Invalid Uber webhook signature", frappe.PermissionError)

    # ✅ Valid webhook
    return True
