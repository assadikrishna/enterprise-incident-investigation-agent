# Inventory Service Runbook

## Delayed Inventory Updates

Inventory updates may be delayed when messaging infrastructure is unavailable or when consumers cannot process events fast enough.

Investigation steps:

1. Check inventory-service logs for queue or consumer errors.
2. Review message broker availability.
3. Inspect consumer lag and processing latency.
4. Check for recent deployment or configuration changes.
5. Verify connectivity between inventory-service and the messaging platform.

Production changes require engineer review and approval.