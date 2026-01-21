import frappe
from .get_pickup_address import get_pickup_address


def get_pickup_details():
    """Get the pickup details for the delivery."""

    # get arcpos settings
    default_outlet = frappe.get_single_value("ArcPOS Settings", "default_outlet")
    if not default_outlet:
        frappe.throw("Default outlet is not set. Please set it in the ArcPOS Settings.")

    # get the outlet
    outlet = frappe.get_doc("Territory", default_outlet)
    if not outlet:
        message = "Default outlet is not found. Please set it in the ArcPOS Settings."
        frappe.throw(message, exc=frappe.NotFound)

    # prepare address
    field_map = {
        "custom_address_line1": "street_address",
        "custom_city": "city",
        "custom_state": "state",
        "custom_pincode": "zip_code",
        "custom_country": "country",
    }
    addr_dict = {}
    for field, value in field_map.items():
        addr_dict[value] = outlet.get(field)

    # get the pickup details
    pickup_details = {"address": addr_dict, "name": None, "phone_number": None}

    # validate and set name
    if not outlet.custom_outlet_name:
        msg = "Outlet name is not set. Please set it in the Territory."
        frappe.throw(msg, exc=frappe.ValidationError)
    pickup_details["name"] = outlet.custom_outlet_name

    # validate and set contact number
    for contact in outlet.get("custom_contact_numbers", []):
        if contact.is_primary_phone or contact.is_primary_mobile_no:
            pickup_details["phone_number"] = contact.phone_number
            break

    if not pickup_details["phone_number"]:
        msg = "Primary contact number is not set. Please set it in the Territory."
        frappe.throw(msg, exc=frappe.ValidationError)

    return pickup_details
