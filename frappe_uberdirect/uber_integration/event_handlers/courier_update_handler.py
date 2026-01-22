import frappe


def courier_update_handler(payload: dict) -> None:
    """Handler for courier update event."""

    delivery_id = payload.get("delivery_id", None)
    if not delivery_id:
        frappe.throw("Delivery ID is required")

    # print delivery id
    print(f"Courier update event received for delivery: {delivery_id}")

    # get and validate payload  
    frappe.logger(module="frappe_uberdirect", with_more_info=True).info(f"Courier update event received for delivery: {delivery_id}")
    
