"""Delivery status webhook to update the delivery status in the ERPNext."""

import frappe
from .helper.uber_webhook import verify_uber_webhook
from frappe_uberdirect.uber_integration.event_handlers import delivery_status_handler
from .helper.get_webhook_secret import get_webhook_secret


@frappe.whitelist(allow_guest=True, methods=["POST"])
def delivery_status_webhook() -> dict:
    """Delivery status webhook to update the delivery status in the ERPNext."""

    print("Delivery status webhook received")

    # Verify signature FIRST
    secret = get_webhook_secret(kind="delivery_status")
    verify_uber_webhook(secret=secret)

    # Convert frappe.form_dict to regular dict for background job serialization
    payload = dict(frappe.form_dict)

    # enqueue the background job
    frappe.enqueue(delivery_status_handler, queue="short", payload=payload)

    # return response
    return {"message": "Webhook received successfully"}
