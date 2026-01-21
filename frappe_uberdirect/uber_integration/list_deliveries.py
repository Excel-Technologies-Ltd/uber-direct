"""Background job listing all deliveries."""

import requests

import frappe
from .helper import prepare_params, prepare_url, prepare_auth_header


def list_deliveries(params: dict = None) -> list[dict]:
    """List all deliveries."""

    # get customer id
    customer_id = frappe.conf.get("uberdirect_customer_id")
    if not customer_id:
        msg = "Uber Direct customer ID is not set. Please set it in the Frappe configuration."
        frappe.throw(msg=msg, exc=frappe.ValidationError)

    # prepare params
    query = prepare_params(params).get("query")
    url = prepare_url(f"/customers/{customer_id}/deliveries{query}")

    # prepare headers
    headers = prepare_auth_header().get("headers")

    # send request
    response = requests.get(url, headers=headers, timeout=10)

    # check response
    if response.status_code != 200:
        msg = f"Failed to list deliveries. Status code: {response.status_code}. Response: {response.text}"
        frappe.throw(msg=msg, exc=frappe.ValidationError)

    # return response
    return response.json()
