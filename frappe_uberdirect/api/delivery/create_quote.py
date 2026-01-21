"""API endpoint for creating quotes.

This module provides the API endpoint for creating quotes
through the Uber Direct integration.
"""
import json

import frappe
from frappe_uberdirect.uber_integration import create_quote
from frappe_uberdirect.uber_integration.helper.get_pickup_address import get_pickup_address


@frappe.whitelist(allow_guest=True, methods=["POST"])
def create_quote_api() -> dict:
    """Create a quote for an order through the Uber Direct integration."""

    # dropof address fields
    addr_fields = ["street_address", "city", "state", "zip_code", "country"]
    addr_dict = {field: frappe.form_dict.get(field, None) for field in addr_fields}

    # check all fields are filled
    if not all(addr_dict.values()):
        frappe.throw("All address fields are required")

    # optional fields
    optional_fields = ["pickup_ready_dt", "dropoff_phone_number", "manifest_total_value"]
    opt_dict = {}
    for field in optional_fields:
        value = frappe.form_dict.get(field, None)
        if value:
            opt_dict[field] = value

    # get the pickup address
    pickup_address = get_pickup_address()
    if not all(pickup_address.values()):
        frappe.throw("Please set the pickup address in the ArcPOS Settings.")

    
    # prepare payload for making quote
    quote_data = {
        "pickup_address": json.dumps(pickup_address),
        "dropoff_address": json.dumps(addr_dict),
        **opt_dict,
    }

    print(quote_data)
   
    # create the quote
    result = create_quote(payload=quote_data)
    

    return result
