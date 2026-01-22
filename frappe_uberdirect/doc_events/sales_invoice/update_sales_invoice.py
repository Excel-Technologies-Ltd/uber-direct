"""Document event handlers for Sales Invoice updates.

This module handles sales invoice update events and schedules delayed tasks
for order notifications.
"""

import frappe
from frappe_uberdirect.uber_integration.job_handlers import create_delivery_handler


def update_sales_invoice(doc, method):
    """
    Update sales invoice document events.
    """

    # if service type is not Delivery, return
    if doc.custom_service_type != "Delivery":
        return

    # if order status is not Accepted, return
    if doc.custom_order_status != "In kitchen":
        return

    # this is a delivery order, so we need to start delivery proccess
    frappe.enqueue(create_delivery_handler, queue="long", invoice_id=doc.name)
