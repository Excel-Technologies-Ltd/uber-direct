"""API endpoints for the Uber Direct integration."""

from .delivery import delivery_api_routes
from .webhook import webhook_api_routes

api_routes = {
    **delivery_api_routes,
    **webhook_api_routes,
}
