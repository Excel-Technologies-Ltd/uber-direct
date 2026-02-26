import frappe


def delivery_status_handler(payload: dict) -> None:
    """Handler for delivery status event."""

    # get and validate payload
    delivery_id = payload.get("delivery_id", None)
    if not delivery_id:
        frappe.throw("Delivery ID is required")

    # get the delivery doc
    delivery_status = payload.get("status", None)
    delivery = frappe.get_doc("ArcPOS Delivery", {"delivery_id": delivery_id})
    if not delivery:
        frappe.throw("Delivery not found")

    # update the delivery doc
    delivery.status = delivery_status
    delivery.save(ignore_permissions=True)

    # update the sales invoice doc

    map_status = {
        "delivered": "Delivered",
        "pickup_complete": "Handover to Delivery",
        "dropoff": "On the Way",
        "canceled": "Ready to Deliver",
    }

    partner_map = {
        "delivered": "Delivered",
        "pickup_complete": "Rider on Delivery",
        "dropoff": "Rider on Delivery",
        "canceled": "Cancelled from Marchant",
    }

    if delivery_status in map_status:
        invoice_doc = frappe.get_doc("Sales Invoice", delivery.order_no)
        if invoice_doc:
            invoice_doc.custom_order_status = map_status[delivery_status]
            invoice_doc.custom_delivery_partner_status = partner_map[delivery_status]
            if delivery_status == "delivered":
                for item in invoice_doc.items:
                    item.custom_order_item_status = "Delivered"
            invoice_doc.save(ignore_permissions=True)

    # log the event
    frappe.logger(module="frappe_uberdirect", with_more_info=True).info(
        f"Delivery status updated successfully for delivery {delivery_id} to {delivery.status}"
    )
