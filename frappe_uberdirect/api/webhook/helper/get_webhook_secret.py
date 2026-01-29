import frappe

"""Helper to get the webhook secret from the config."""


def get_webhook_secret(kind: str) -> str:
    """Get the webhook secret from the config."""

    # get the webhook secret from the config
    webhook_secret = frappe.conf.get("uber_webhook_secrets", {}).get(kind)
    if not webhook_secret:
        msg = f"Webhook secret not found for kind: {kind}"
        frappe.throw(msg=msg, exc=frappe.ValidationError)

    return webhook_secret
