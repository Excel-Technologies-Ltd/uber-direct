"""Helper functions for preparing URLs."""

from urllib.parse import urljoin

import frappe


def prepare_url(path: str):
    """
    Prepare the URL for the Uber Direct integration.

    Args:
        path: The API endpoint path (e.g., "quotes", "/customers/123/delivery_quotes")

    Returns:
        str: The complete URL

    Example:
        >>> prepare_url("quotes")
        "https://api.uberdirect.com/quotes"
        >>> prepare_url("/customers/123/delivery_quotes")
        "https://api.uberdirect.com/customers/123/delivery_quotes"
    """
    base_path = frappe.conf.get("uberdirect_api_url")
    if not base_path:
        msg = "Uber Direct base URL is not set. Please set it in the Frappe configuration."
        frappe.throw(msg=msg, exc=frappe.ValidationError)

    # Use urljoin to properly handle URL joining
    # urljoin works best when base ends with '/' and path is relative
    base = base_path.rstrip("/") + "/"
    relative_path = path.lstrip("/")
    return urljoin(base, relative_path)
