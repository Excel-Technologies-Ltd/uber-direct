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
    order_id = frappe.form_dict.get("order_id", None)
    if not order_id:
        frappe.throw("Order ID is required")

    # get and validate payload
    payload = frappe.form_dict.get("payload", None)
    if not payload:
        frappe.throw("Payload is required")

    # cancel delivery
    response = cancel_delivery(delivery_id=order_id, payload=payload)
    print(response)

    return {
        "message": "Delivery cancelled successfully",
        "order_id": order_id,
    }
