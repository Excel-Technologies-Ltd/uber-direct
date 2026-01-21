"""Delivery status webhook to update the delivery status in the ERPNext."""

import frappe
from frappe_uberdirect.uber_integration import update_delivery


@frappe.whitelist(allow_guest=True, methods=["POST"])
def delivery_status_webhook() -> dict:
    """Delivery status webhook to update the delivery status in the ERPNext."""

    # get and validate payload
    kind = frappe.form_dict.get("kind", None)

    match kind:
        case "event.delivery_status":
            return delivery_status_update()
        case "event.courier_update":
            frappe.throw("Invalid kind")
        case "event.refund_request":
            pass

    # return response
    return {
        "payload": payload,
        "message": "Webhook received successfully",
    }
