import frappe


def refund_request_handler(payload: dict) -> None:
    """Handler for refund request event."""

    # get and validate payload
    manifest = payload.get("manifest", None)
    status = payload.get("status", None)
