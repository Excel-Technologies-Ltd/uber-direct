"""Scheduler tasks for processing delayed jobs."""

from datetime import datetime, timezone

import frappe
from frappe.utils.background_jobs import get_queue, get_redis_conn, generate_qname
from rq.registry import ScheduledJobRegistry


def process_scheduled_jobs():
    """
    Process scheduled RQ jobs and move them to the queue.
    This is needed because Frappe disables RQ's scheduler.
    Runs every minute via Frappe scheduler.
    """
    # Log that scheduler is running
    print("process_scheduled_jobs: Scheduler task started")
    frappe.logger().info("process_scheduled_jobs: Scheduler task started")

    try:
        redis_conn = get_redis_conn()

        # Get all queues using the same format Frappe uses
        from frappe.utils.background_jobs import get_queues_timeout

        processed_count = 0

        for queue_type in get_queues_timeout().keys():
            try:
                # Use the same queue generation as Frappe
                queue = get_queue(queue_type, is_async=True)
                queue_name = generate_qname(queue_type)

                # Create registry for this queue
                registry = ScheduledJobRegistry(queue=queue, connection=redis_conn)

                # Get all scheduled jobs
                job_ids = registry.get_job_ids()

                if not job_ids:
                    continue

                print(f"Found {len(job_ids)} scheduled jobs in queue {queue_name}")
                frappe.logger().info(
                    f"Found {len(job_ids)} scheduled jobs in queue {queue_name}"
                )

                for job_id in job_ids:
                    try:
                        # Get scheduled timestamp from registry's sorted set
                        # RQ stores scheduled jobs in a sorted set where score = timestamp
                        scheduled_timestamp = redis_conn.zscore(registry.key, job_id)

                        if scheduled_timestamp is None:
                            # If no scheduled time, move it immediately
                            job = queue.job_class.fetch(job_id, connection=redis_conn)
                            registry.remove(job_id)
                            queue.enqueue_job(job)
                            processed_count += 1
                            frappe.logger().info(
                                f"Moved scheduled job {job_id} to queue (no scheduled time)"
                            )
                            continue

                        # Convert timestamp to datetime
                        scheduled_at = datetime.fromtimestamp(
                            scheduled_timestamp, tz=timezone.utc
                        )
                        now = datetime.now(timezone.utc)

                        print(
                            f"Job {job_id}: scheduled_at={scheduled_at}, now={now}, ready={scheduled_at <= now}"
                        )

                        if scheduled_at <= now:
                            # Move job from scheduled registry to queue
                            job = queue.job_class.fetch(job_id, connection=redis_conn)
                            registry.remove(job_id)
                            queue.enqueue_job(job)
                            processed_count += 1
                            print(f"Moved scheduled job {job_id} to queue")
                            frappe.logger().info(
                                f"Moved scheduled job {job_id} to queue {queue_name} "
                                f"(was scheduled for {scheduled_at}, now is {now})"
                            )
                        else:
                            print(
                                f"Job {job_id} not ready yet (scheduled for {scheduled_at}, now is {now})"
                            )
                    except Exception as e:
                        frappe.logger().error(
                            f"Error processing scheduled job {job_id}: {str(e)}",
                            exc_info=True,
                        )
            except Exception as e:
                frappe.logger().error(
                    f"Error processing scheduled jobs for queue {queue_type}: {str(e)}",
                    exc_info=True,
                )

        if processed_count > 0:
            frappe.logger().info(f"Processed {processed_count} scheduled jobs")
    except Exception as e:
        frappe.logger().error(
            f"Error in process_scheduled_jobs: {str(e)}", exc_info=True
        )
