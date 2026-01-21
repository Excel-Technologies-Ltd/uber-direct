import frappe


def courier_update_handler(payload: dict) -> None:
    """Handler for courier update event."""

    # get and validate payload
    delivery_id = payload.get("delivery_id", None)
    if not delivery_id:
        frappe.throw("Delivery ID is required")

    # get the delivery
    delivery = frappe.get_doc("Delivery", delivery_id)
    if not delivery:
        frappe.throw("Delivery not found")
