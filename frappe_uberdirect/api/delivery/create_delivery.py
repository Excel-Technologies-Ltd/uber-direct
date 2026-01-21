"""API endpoint for creating deliveries.

This module provides the API endpoint for creating delivery orders
through the Uber Direct integration.
"""

import frappe

from frappe_uberdirect.uber_integration.job_handlers import create_delivery_handler


@frappe.whitelist()
def create_delivery_api() -> dict:
    """Create a delivery for an order."""

    invoice_id = frappe.form_dict.get("invoice_id", None)
    if not invoice_id:
        frappe.throw("Invoice ID is required")

    delivery_payload = create_delivery_handler(invoice_id=invoice_id)

    return {
        "message": "Delivery created successfully",
        "delivery_payload": delivery_payload,
    }
