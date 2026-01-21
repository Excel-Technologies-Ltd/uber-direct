import json
import frappe
from excel_restaurant_pos.shared.contacts import get_customer_phones
from ..helper import get_pickup_details


# prepare dropoff details
def _prepare_dropoff_details(sales_invoice) -> dict:
    """Prepare the dropoff details for the delivery."""

    # get default customer
    dropoff_address = {}
    field_map = {
        "custom_address_line1": "street_address",
        "custom_city": "city",
        "custom_state": "state",
        "custom_pincode": "zip_code",
        "custom_country": "country",
    }
    for field, value in field_map.items():
        dropoff_address[value] = getattr(sales_invoice, field)

    # prepare the dropoff details
    dropoff_details = {"address": dropoff_address, "name": None, "phone_number": None}

    # get and validte default customer
    default_customer = frappe.get_single_value("ArcPOS Settings", "default_customer")
    if not default_customer:
        msg = "Default customer is not set in the ArcPOS Settings."
        frappe.throw(msg=msg, exc=frappe.ValidationError)

    # if invoice create on behalf of default customer
    if default_customer == sales_invoice.customer:
        # set customer details
        dropoff_details["name"] = getattr(sales_invoice, "custom_customer_full_name")
        dropoff_details["phone_number"] = getattr(sales_invoice, "custom_mobile_no")
        return dropoff_details

    # get the customer contacts
    customer_phones = get_customer_phones(customer_code=sales_invoice.customer)
    if not customer_phones or len(customer_phones) == 0:
        msg = f"No primary phone found for customer {sales_invoice.customer}."
        frappe.throw(msg=msg, exc=frappe.ValidationError)

    # set the primary phone as phone
    for phone in customer_phones:
        if phone["is_primary_phone"] or phone["is_primary_mobile_no"]:
            dropoff_details["phone_number"] = phone["phone"]
            break

    # set customer name as name
    dropoff_details["name"] = getattr(sales_invoice, "customer_name")

    # return the dropoff details
    return dropoff_details


def create_delivery_handler(invoice_id: str) -> dict:
    """Create a delivery for an order through the Uber Direct integration."""

    # get and validate the sales invoice
    invoice = frappe.get_doc("Sales Inovice", invoice_id)
    if not invoice:
        msg = f"Sales Invoice {invoice_id} not found."
        frappe.throw(msg=msg, exc=frappe.ValidationError)

    # get the pickup address
    pickup_details = get_pickup_details()

    # prepare manifest items
    fmt_items = []
    for item in invoice.items:
        fmt_items.append(
            {
                "name": item.item_name,
                "quantity": item.qty,
                "unit_of_measurement": item.uom,
                "price": item.rate,
            }
        )

    # prepare the dropoff details
    dropoff_details = _prepare_dropoff_details(sales_invoice=invoice)

    # find the first quote for the invoice
    if not invoice.custom_quotes or len(invoice.custom_quotes) == 0:
        msg = f"No quote found for invoice {invoice.name}."
        frappe.throw(msg=msg, exc=frappe.ValidationError)

    # get the first quote
    quote = invoice.custom_quotes[0]
    if not quote:
        msg = f"No quote found for invoice {invoice.name}."
        frappe.throw(msg=msg, exc=frappe.ValidationError)

    # prepare the delivery payload
    delivery_payload = {
        # dropoff details
        "dropoff_address": json.dumps(dropoff_details["address"]),
        "dropoff_name": dropoff_details["name"],
        "dropoff_phone_number": dropoff_details["phone_number"],
        # pickup details
        "pickup_address": json.dumps(pickup_details["address"]),
        "pickup_name": pickup_details["name"],
        "pickup_phone_number": pickup_details["phone_number"],
        # items
        "manifest_items": fmt_items,
        "manifest_reference": invoice.name,
        "manifest_total_value": invoice.total,
    }

    # set delivery quote
    quote_id = None
    if len(invoice.get("custom_quotes", [])) > 0:
        quote_id = invoice.custom_quotes[0].delivery_quote_id

    # if quote id is found, set it in the delivery payload
    if quote_id:
        delivery_payload["quote_id"] = quote_id

    print(delivery_payload)

    # return the delivery payload
    return delivery_payload


# calculate the delay time to cancel the delivery
def _calculate_delay_time(delivery_payload: dict) -> int:
    """Calculate the delay time to cancel the delivery."""

    # get the delay time
    delay_time = delivery_payload["delay_time"]
    return delay_time
