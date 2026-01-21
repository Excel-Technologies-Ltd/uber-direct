"""
Helper functions for the Uber Direct integration.
"""

import frappe


def get_pickup_address():
    """
    Get the pickup address for an order from the invoice.
    """

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

    return addr_dict
