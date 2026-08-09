# Authentication Service Runbook

## Login Failures and Token Validation

Users may experience login failures when authentication tokens cannot be validated or when identity provider communication fails.

Investigation steps:

1. Check authentication-service logs for HTTP 401 and 403 responses.
2. Verify identity provider availability.
3. Check token expiration and signing certificate validity.
4. Review recent authentication configuration changes.
5. Confirm that application clocks are synchronized.

Production changes require engineer review and approval.