"""API endpoint for canceling deliveries.

This module provides the API endpoint for canceling delivery orders
through the Uber Direct integration.
"""

import frappe

from frappe_uberdirect.uber_integration import cancel_delivery


@frappe.whitelist()
def cancel_delivery_api() -> dict:
    """Cancel a delivery."""

    # get and validate order id
    required_fields = ["order_id", "cancelation_reason", "additional_description"]

    # validate cancel required data
    for field in required_fields:
        value = frappe.form_dict.get(field, None)
        if not value:
            msg = f"{field} is required"
            frappe.throw(msg=msg, exc=frappe.ValidationError)

    #  get the delivery id
    order_id = frappe.form_dict.get("order_id")
    delivery_id = frappe.db.get_value(
        "ArcPOS Delivery", {"order_no": order_id}, "delivery_id"
    )
    if not delivery_id:
        frappe.throw(f"Delivery ID not found for order {order_id}")

    # get and validate payload
    payload = {
        "cancelation_reason": frappe.form_dict.get("cancelation_reason"),
        "additional_description": frappe.form_dict.get("additional_description"),
    }

    # cancel delivery
    response = cancel_delivery(delivery_id=delivery_id, payload=payload)
    return response
