"""Background job proofing of delivery."""

import requests

import frappe
from .helper import prepare_url, prepare_auth_header


def proof_of_delivery(delivery_id: str, payload: dict = None) -> dict:
    """Proof of delivery for a delivery."""

    # get customer id
    customer_id = frappe.conf.get("uberdirect_customer_id")
    if not customer_id:
        msg = "Uber Direct customer ID is not set. Please set it in the Frappe configuration."
        frappe.throw(msg=msg, exc=frappe.ValidationError)

    # prepare url
    url = prepare_url(
        f"/customers/{customer_id}/deliveries/{delivery_id}/proof_of_delivery"
    )

    # prepare headers
    headers = prepare_auth_header().get("headers")

    # send request
    response = requests.post(url, headers=headers, json=payload, timeout=10)

    # check response
    if response.status_code != 200:
        msg = f"Failed to proof of delivery. Status code: {response.status_code}. Response: {response.text}"
        frappe.throw(msg=msg, exc=frappe.ValidationError)

    # return response
    return response.json()
