from .delivery_status import delivery_status_webhook


__all__ = [
    "delivery_status_webhook",
]



webhook_api_routes = {
    "api.webhook.delivery_status": "frappe_uberdirect.api.webhook.delivery_status_webhook",
}
