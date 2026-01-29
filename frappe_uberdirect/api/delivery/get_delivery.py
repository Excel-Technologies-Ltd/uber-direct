import frappe

from frappe_uberdirect.uber_integration import get_delivery


@frappe.whitelist()
def get_delivery_api() -> dict:
    """Get a delivery."""

    # get and validate order id
    order_id = frappe.form_dict.get("order_id", None)
    if not order_id:
        frappe.throw("Order ID is required")

    # get delivery id
    delivery_id = frappe.db.get_value(
        "ArcPOS Delivery", {"order_no": order_id}, "delivery_id"
    )
    if not delivery_id:
        frappe.throw(f"Delivery ID not found for order {order_id}")

    # get delivery
    delivery = get_delivery(delivery_id=delivery_id)
    return delivery
