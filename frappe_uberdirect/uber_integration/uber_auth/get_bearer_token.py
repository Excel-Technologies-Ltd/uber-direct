"""Uber Direct authentication module for obtaining bearer tokens.

This module handles authentication with the Uber Direct API to retrieve
bearer tokens for API requests.
"""

import requests
import frappe


def get_bearer_token():
    """Get a bearer token from the Uber Direct API.

    This function retrieves a bearer token from the Uber Direct API using the
    client ID and client secret configured in the Frappe site configuration.
    """
    url = frappe.conf.get("uberdirect_oauth_url")
    client_id = frappe.conf.get("uberdirect_client_id")
    client_secret = frappe.conf.get("uberdirect_client_secret")
    customer_id = frappe.conf.get("customer_id")

    url = f"{url}/oauth/v2/token"

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "eats.deliveries",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    bearer_token = get_bearer_token_from_cache(customer_id)

    if bearer_token:
        return bearer_token

    # Use data=payload for form-urlencoded, requests will encode it automatically
    response = requests.post(url, headers=headers, data=payload, timeout=30)
    if response.status_code != 200:
        frappe.throw(f"Failed to get bearer token: {response.text}")

    print(response.text)

    bearer_token = response.json()["access_token"]
    expires_in = response.json()["expires_in"]

    print(f"Bearer token: {bearer_token}")
    print(f"Expires in: {expires_in} seconds")

    put_bearer_token_in_cache(customer_id, bearer_token, expires_in)
    return bearer_token


def get_bearer_token_from_cache(customer_id: str):
    """Get a bearer token from the cache.

    This function retrieves a bearer token from the cache using the
    client ID and client secret configured in the Frappe site configuration.
    """
    cache_key = prepare_cache_key(customer_id)
    return frappe.cache().get_value(cache_key)


def put_bearer_token_in_cache(customer_id: str, bearer_token: str, expires_in: int):
    """Put a bearer token in the cache.

    This function puts a bearer token in the cache using the
    client ID and client secret configured in the Frappe site configuration.

    Args:
        customer_id: Customer ID for cache key
        bearer_token: The bearer token to cache
        expires_in: Expiration time in seconds (OAuth2 standard)
    """
    cache_key = prepare_cache_key(customer_id)
    expires_in_seconds = int(expires_in)
    frappe.cache().set_value(cache_key, bearer_token, expires_in_sec=expires_in_seconds)


def prepare_cache_key(customer_id: str):
    """Prepare a cache key for the bearer token.

    This function prepares a cache key for the bearer token using the
    client ID and client secret configured in the Frappe site configuration.
    """
    return f"uberdirect_bearer_token_{customer_id}"
