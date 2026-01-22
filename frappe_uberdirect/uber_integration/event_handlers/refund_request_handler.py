import frappe


def refund_request_handler(payload: dict) -> None:
    """Handler for refund request event."""

    # get and validate payload
    delivery_id = payload.get("delivery_id", None)
    if not delivery_id:
        frappe.throw("Delivery ID is required")

    # print delivery id
    print(f"Refund request event received for delivery: {delivery_id}")

    # log the event
    frappe.logger(module="frappe_uberdirect", with_more_info=True).info(f"Refund request event received for delivery: {delivery_id}")
    