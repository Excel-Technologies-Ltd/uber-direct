"""Delivery status webhook to update the delivery status in the ERPNext."""

import frappe
from .helper.uber_webhook import verify_uber_webhook
from frappe_uberdirect.uber_integration.event_handlers import refund_request_handler
from .helper.get_webhook_secret import get_webhook_secret


@frappe.whitelist(allow_guest=True, methods=["POST"])
def refund_request_webhook() -> dict:
    """Refund request webhook to update the refund request in the ERPNext."""

    # Verify signature FIRST
    secret = get_webhook_secret(kind="refund_request")
    verify_uber_webhook(secret=secret)

    # Convert frappe.form_dict to regular dict for background job serialization
    payload = dict(frappe.form_dict)

    # enqueue the background job
    frappe.enqueue(refund_request_handler, queue="short", payload=payload)

    # return response
    return {"message": "Webhook received successfully"}
