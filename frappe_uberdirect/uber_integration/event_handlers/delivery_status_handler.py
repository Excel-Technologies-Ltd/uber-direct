import frappe


def delivery_status_handler(payload: dict) -> None:
    """Handler for delivery status event."""

    # get and validate payload
    delivery_id = payload.get("delivery_id", None)
    if not delivery_id:
        frappe.throw("Delivery ID is required")

    # get the delivery
    delivery = frappe.get_doc("Delivery", delivery_id)
    if not delivery:
        frappe.throw("Delivery not found")
