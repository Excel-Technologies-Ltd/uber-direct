from .delivery_status import delivery_status_webhook
from .courier_update import courier_update_webhook
from .refund_request import refund_request_webhook


__all__ = [
    "delivery_status_webhook",
    "courier_update_webhook",
    "refund_request_webhook",
]


# webhook api routes
webhook_api_routes = {
    "api.webhook.delivery_status": "frappe_uberdirect.api.webhook.delivery_status_webhook",
    "api.webhook.courier_update": "frappe_uberdirect.api.webhook.courier_update_webhook",
    "api.webhook.refund_request": "frappe_uberdirect.api.webhook.refund_request_webhook",
}
