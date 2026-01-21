import frappe


def get_dropoff_details(invoice_id: str) -> dict:
    """Get the dropoff details for the delivery."""

    # get the invoice
    invoice = frappe.get_doc("Sales Invoice", invoice_id)
    if not invoice:
        msg = f"Sales Invoice {invoice_id} not found."
        frappe.throw(msg=msg, exc=frappe.ValidationError)

    # get the dropoff details
    dropoff_details = {}
    return dropoff_details
