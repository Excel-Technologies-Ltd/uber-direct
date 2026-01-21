"""Helper functions for preparing parameters."""


def prepare_params(params: dict) -> str:
    """Prepare the parameters for the Uber Direct integration."""

    # prepare query string
    qry_list = []
    for key, value in params.items():
        qry_list.append(f"{key}={value}")

    # join query string
    query = "&".join(qry_list)
    query = f"?{query}"

    return {"query": query}
