import json
import frappe
from frappe.utils import now_datetime, get_datetime
from excel_restaurant_pos.shared.contacts import get_customer_phones
from ..helper import get_pickup_details
from frappe_uberdirect.uber_integration.create_delivery import create_delivery


def _get_valid_quote_id(sales_invoice) -> str | None:
    """
    Get a valid (non-expired) quote ID from the sales invoice.

    Args:
        sales_invoice: Sales Invoice document

    Returns:
        str | None: Quote ID if valid and not expired, None otherwise
    """
    if not sales_invoice.get("custom_quotes") or len(sales_invoice.custom_quotes) == 0:
        return None

    quote = sales_invoice.custom_quotes[0]
    quote_id = quote.delivery_quote_id

    # Check if quote has expired
    expires = quote.get("expires")
    if not expires:
        # No expiration date, quote is valid
        return quote_id

    # Convert expires to datetime if it's a string
    expires_dt = get_datetime(expires) if isinstance(expires, str) else expires
    current_dt = now_datetime()

    # If quote has expired, return None
    if expires_dt and expires_dt < current_dt:
        frappe.log_error(
            f"Quote {quote_id} has expired. Expires: {expires_dt}, Current: {current_dt}",
            "Delivery Quote Expired",
        )
        return None

    # Quote is still valid
    return quote_id


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
    default_customer = frappe.db.get_single_value("ArcPOS Settings", "customer")
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

    # environment
    is_development = frappe.conf.get("environment", None) == "development"

    # get and validate the sales invoice
    invoice = frappe.get_doc("Sales Invoice", invoice_id)
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
                "quantity": int(item.qty),
                "price": int(item.rate * 100),  # Convert to cents (integer)
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
        "pickup_business_name": "BanCan Kitchen",
        # items
        "manifest_items": fmt_items,
        "manifest_reference": invoice.name,
        "manifest_total_value": int(invoice.total * 100),
        "idempotency_key": f"delivery_{invoice.name}",
    }

    # add robo test in developmer mode
    if is_development:
        delivery_payload["test_specifications"] = {
            "robo_courier_specification": {"mode": "auto"}
        }

    # set delivery window
    window_fields = [
        "pickup_ready_dt",
        "pickup_deadline_dt",
        "dropoff_ready_dt",
        "dropoff_deadline_dt",
    ]
    for field in window_fields:
        value = invoice.get(field, None)
        if value is not None:
            delivery_payload[field] = value

    # set delivery quote
    quote_id = _get_valid_quote_id(invoice)
    if quote_id:
        delivery_payload["quote_id"] = quote_id

    # create the delivery
    response = create_delivery(payload=delivery_payload)

    print(response)

    # create the delivery record in the db
    # Safely get nested courier data (handle None values)
    courier = response.get("courier") or {}
    if not isinstance(courier, dict):
        courier = {}

    delivery_data = {
        "order_no": invoice.name,
        "delivery_id": response.get("id", ""),
        "courier_name": courier.get("name", ""),
        "courier_rating": courier.get("rating", 0),
        "courier_vehicle_type": courier.get("vehicle_type", ""),
        "courier_phone_number": courier.get("phone_number", ""),
        "courier_img_href": courier.get("img_href", ""),
        "courier_imminent": response.get("courier_imminent", False),
        "deliverable_action": response.get("deliverable_action", ""),
        "external_id": response.get("external_id", ""),
        "fee": response.get("fee", 0),
        "manifest_reference": invoice.name,
        "status": response.get("status", ""),
        "tip": response.get("tip", 0),
        "tracking_url": response.get("tracking_url", ""),
        "uuid": response.get("uuid", ""),
        "batch_id": response.get("batch_id", ""),
    }

    print(delivery_data)
    delivery_record = frappe.get_doc({"doctype": "ArcPOS Delivery", **delivery_data})
    delivery_record.insert(ignore_permissions=True)

    # return the response
    return response


# calculate the delay time to cancel the delivery
def _calculate_delay_time(delivery_payload: dict) -> int:
    """Calculate the delay time to cancel the delivery."""

    # get the delay time
    delay_time = delivery_payload["delay_time"]
    return delay_time
