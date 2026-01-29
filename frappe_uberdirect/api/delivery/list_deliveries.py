import frappe

from frappe_uberdirect.uber_integration import list_deliveries


@frappe.whitelist()
def list_deliveries_api() -> list[dict]:
    """List all deliveries."""

    # get and validate params
    params_key = ["filter", "start_dt", "end_dt", "limit", "offset"]
    params: dict = {}
    for key in params_key:
        value = frappe.form_dict.get(key, None)
        if value is not None:
            params[key] = value

    # list deliveries
    deliveries = list_deliveries(params=params)
    return deliveries
