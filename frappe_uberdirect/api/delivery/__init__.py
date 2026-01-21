"""Address API endpoints."""

from .create_delivery import create_delivery_api
from .cancel_delivery import cancel_delivery_api
from .create_quote import create_quote_api

__all__ = [
    "create_delivery_api",
    "cancel_delivery_api",
    "create_quote_api",
]

delivery_api_routes = {
    "api.deliveries.create": "frappe_uberdirect.api.delivery.create_delivery_api",
    "api.deliveries.cancel": "frappe_uberdirect.api.delivery.cancel_delivery_api",
    "api.deliveries.create_quote": "frappe_uberdirect.api.delivery.create_quote_api",
}
