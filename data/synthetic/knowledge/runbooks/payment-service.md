# Payment Service Runbook

## HTTP 503 and Database Connectivity

Repeated HTTP 503 responses may occur when the application cannot obtain
database connections.

Investigation steps:

1. Check database connectivity.
2. Review connection-pool utilization and wait times.
3. Compare pool configuration with the previous deployment.
4. Review recent application changes affecting connection lifecycle.
5. Check database latency and active connection counts.

Production changes require engineer review and approval.