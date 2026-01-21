"""Background job getting a delivery for an order."""

import requests

import frappe
from .helper import prepare_url, prepare_auth_header


def get_delivery(delivery_id: str) -> dict:
    """Get the status of a delivery for an order."""

    # get customer id
    customer_id = frappe.conf.get("uberdirect_customer_id")
    if not customer_id:
        msg = "Uber Direct customer ID is not set. Please set it in the Frappe configuration."
        frappe.throw(msg=msg, exc=frappe.ValidationError)

    # prepare url
    url = prepare_url(f"/customers/{customer_id}/deliveries/{delivery_id}")

    # prepare headers
    headers = prepare_auth_header().get("headers")

    # send request
    response = requests.get(url, headers=headers, timeout=10)

    # check response
    if response.status_code != 200:
        msg = f"Failed to get delivery. Status code: {response.status_code}. Response: {response.text}"
        frappe.throw(msg=msg, exc=frappe.ValidationError)

    # return response
    return response.json()
