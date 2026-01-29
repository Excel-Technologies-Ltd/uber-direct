"""Courier update webhook to update the courier update in the ERPNext."""

import frappe
from .helper.uber_webhook import verify_uber_webhook
from frappe_uberdirect.uber_integration.event_handlers import courier_update_handler
from .helper.get_webhook_secret import get_webhook_secret


@frappe.whitelist(allow_guest=True, methods=["POST"])
def courier_update_webhook() -> dict:
    """Courier update webhook to update the courier update in the ERPNext."""

    # Verify signature FIRST
    secret = get_webhook_secret(kind="courier_update")
    verify_uber_webhook(secret=secret)

    # Convert frappe.form_dict to regular dict for background job serialization
    payload = dict(frappe.form_dict)

    # enqueue the background job
    frappe.enqueue(courier_update_handler, queue="short", payload=payload)

    # return response
    return {"message": "Webhook received successfully"}
