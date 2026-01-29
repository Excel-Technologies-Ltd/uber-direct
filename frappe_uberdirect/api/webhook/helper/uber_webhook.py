import hmac
import hashlib
import frappe


def verify_uber_webhook(secret: str) -> bool:
    """Verify the Uber webhook signature."""

    # get uber header signature
    uber_signature = frappe.request.headers.get("X-Uber-Signature")
    if not uber_signature:
        frappe.throw("Missing Uber webhook signature", frappe.PermissionError)

    # get raw body
    raw_body = frappe.request.data

    # generate signature
    signature = hmac.new(
        secret.encode("utf-8"), raw_body.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    # compare signatures
    if not hmac.compare_digest(signature, uber_signature):
        frappe.throw("Invalid Uber webhook signature", frappe.PermissionError)

    # valid webhook
    return True
