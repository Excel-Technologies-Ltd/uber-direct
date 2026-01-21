"""
Helper functions for the Uber Direct integration.
"""

import frappe

from ..uber_auth.get_bearer_token import get_bearer_token


def prepare_auth_header():
    """
    Prepare the authorization header for the Uber Direct integration.
    """
    bearer_token = get_bearer_token()

    if not bearer_token:
        message = "Failed to get bearer token. Please try again later"
        frappe.throw(message, exc=frappe.ValidationError)

    # prepare headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {bearer_token}",
    }

    return {"headers": headers}
