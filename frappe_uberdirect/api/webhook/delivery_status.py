"""Delivery status webhook to update the delivery status in the ERPNext."""

import frappe
from .helper.uber_webhook import verify_uber_webhook
from frappe_uberdirect.uber_integration.event_handlers import (
    courier_update_handler,
    delivery_status_handler,
    refund_request_handler,
)


@frappe.whitelist(allow_guest=True, methods=["POST"])
def delivery_status_webhook() -> dict:
    """Delivery status webhook to update the delivery status in the ERPNext."""

    # Verify signature FIRST
    # verify_uber_webhook(secret=frappe.conf.get("uberdirect_client_secret"))

    # get and validate payload
    kind = frappe.form_dict.get("kind", None)

    # Convert frappe.form_dict to regular dict for background job serialization
    payload = dict(frappe.form_dict)

    match kind:
        case "event.delivery_status":
            frappe.enqueue(delivery_status_handler, queue="short", payload=payload)
        case "event.courier_update":
            frappe.enqueue(courier_update_handler, queue="short", payload=payload)
        case "event.refund_request":
            frappe.enqueue(refund_request_handler, queue="short", payload=payload)
        case _:
            frappe.throw(f"Invalid kind: {kind}")

    # return response
    return {
        "payload": frappe.form_dict,
        "message": "Webhook received successfully",
    }
