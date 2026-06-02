# Incident Response

## Severity Levels

- SEV1: full outage, data exposure, or active security issue.
- SEV2: major feature unavailable or significant error rate.
- SEV3: degraded performance or isolated feature issue.
- SEV4: minor operational issue.

## Initial Triage

1. Assign incident lead.
2. Capture start time, affected services, and current severity.
3. Check health, readiness, logs, metrics, and recent deploys.
4. Preserve relevant logs and request IDs.

## Communication

- Share status, impact, mitigation, and next update time.
- Avoid speculation.
- Do not share secrets or sensitive user data.

## Rollback

1. Identify last known healthy image.
2. Confirm database migration compatibility.
3. Roll back service image.
4. Run smoke tests.

## Secret Leak Response

1. Revoke leaked secret immediately.
2. Rotate replacement secret.
3. Search logs and repositories for exposure.
4. Audit access during the exposure window.

## User Data Exposure

1. Disable affected path if needed.
2. Preserve evidence.
3. Identify affected workspaces and records.
4. Follow legal and customer notification requirements.

## Postmortem Template

- Summary
- Timeline
- Customer impact
- Root cause
- Detection gaps
- What went well
- Corrective actions
- Owners and due dates

