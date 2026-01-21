"""Helper functions for background jobs with delayed execution."""

from datetime import timedelta
from typing import Callable

import frappe
from frappe.utils.background_jobs import (
    RQ_JOB_FAILURE_TTL,
    RQ_RESULTS_TTL,
    get_queue,
    get_queues_timeout,
    truncate_failed_registry,
)
from rq import Callback
from rq.job import Job


def enqueue_delayed(
    method: str | Callable,
    delay: timedelta,
    queue: str = "default",
    timeout: int | None = None,
    job_id: str | None = None,
    **kwargs,
) -> Job:
    """
    Enqueue a method to be executed after a delay using RQ's enqueue_in.

    This function properly handles Frappe's site context and user session,
    ensuring the job runs with the correct environment when executed.

    Args:
        method: Method string or method object to execute
        delay: TimeDelta object specifying how long to delay execution
        queue: Queue name (default, short, or long). Defaults to "default"
        timeout: Job timeout in seconds. If None, uses queue default
        job_id: Optional unique job ID for deduplication
        **kwargs: Keyword arguments to pass to the method

    Returns:
        Job: The enqueued RQ job object

    Example:
        ```python
        from datetime import timedelta
        from frappe_uberdirect.utils.background_jobs import enqueue_delayed

        # Enqueue a function to run after 10 minutes
        job = enqueue_delayed(
            my_function,
            delay=timedelta(minutes=10),
            arg1="value1",
            arg2="value2"
        )
        ```
    """
    # Get queue and timeout
    queue_obj = get_queue(queue, is_async=True)
    if timeout is None:
        timeout = get_queues_timeout().get(queue) or 300

    # Prepare method name
    if isinstance(method, Callable):
        method_name = f"{method.__module__}.{method.__qualname__}"
    else:
        method_name = method

    # Prepare queue args like frappe.enqueue does
    queue_args = {
        "site": frappe.local.site,
        "user": frappe.session.user,
        "method": method,
        "event": None,
        "job_name": method_name,
        "is_async": True,
        "kwargs": kwargs,
    }

    # Enqueue with delay
    job = queue_obj.enqueue_in(
        delay,
        "frappe.utils.background_jobs.execute_job",
        on_failure=Callback(func=truncate_failed_registry),
        timeout=timeout,
        kwargs=queue_args,
        failure_ttl=frappe.conf.get("rq_job_failure_ttl") or RQ_JOB_FAILURE_TTL,
        result_ttl=frappe.conf.get("rq_results_ttl") or RQ_RESULTS_TTL,
        job_id=job_id,
    )

    log_message = f"Enqueued delayed job: {method_name} (delay: {delay}, queue: {queue}, job_id: {job.id})"
    frappe.logger().info(log_message)

    return job
