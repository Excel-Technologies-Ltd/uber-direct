import json
import frappe


def courier_update_handler(payload: dict) -> None:
    """Handler for courier update event."""

    delivery_id = payload.get("delivery_id", None)
    if not delivery_id:
        frappe.throw("Delivery ID is required")

    # get the delivery doc
    delivery = frappe.get_doc("ArcPOS Delivery", {"delivery_id": delivery_id})
    if not delivery:
        msg = f"Delivery not found for delivery {delivery_id}"
        frappe.log_error(msg, "Uber Direct Courier Update")
        return

    # get the courier details from the payload
    courier_details = payload.get("data", {}).get("courier", None)
    if not courier_details:
        msg = f"Courier details are required for delivery {delivery_id}"
        frappe.log_error(msg, "Uber Direct Courier Update")
        return

    # update the courier details
    delivery.courier_name = courier_details.get("name", None)
    delivery.courier_phone_number = courier_details.get("phone_number", None)
    delivery.courier_rating = courier_details.get("rating", None)
    delivery.courier_vehicle_type = courier_details.get("vehicle_type", None)
    delivery.courier_img_href = courier_details.get("img_href", None)
    delivery.custom_public_phone_info = json.dumps(
        courier_details.get("public_phone_info", None)
    )

    # save the delivery doc
    delivery.save(ignore_permissions=True)

    # log the event
    msg = f"Courier details updated for delivery {delivery_id} successfully"
    frappe.log_success(msg, "Uber Direct Courier Update")
