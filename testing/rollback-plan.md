# Rollback plan

> Fictional office and people. Planning and approvals are case-study simulations; technical results are historical lab evidence only.

Proposed, not rehearsed; no restore result exists. IT operates, PC communicates, SP authorises rollback, SO directs containment. Recovery target within approved window; proposed RTO 4h/RPO 24h unmeasured.

1. Stop changes; notify staff of impact and next update. Record trigger, decision, version.
2. Isolate unexpected access; revoke relevant VPN peers. AD disable alone does not revoke SMB. Preserve evidence privately.
3. Preserve current files/spool/config for investigation; reconcile post-backup writes. Do not blindly overwrite new business data.
4. Restore approved Compose/config. Rehearse consistent named-volume restore in isolation, preserving ownership/modes. Restore .env/keys privately from encrypted storage.
5. After approval restore service state. Do not use `docker compose down -v` for routine recovery. Reissue keys if compromised.
6. Verify directory, share allow/deny, tunnel/files, queues/jobs and monitors. Physical output is separately required.
7. SP accepts only after critical checks pass; otherwise isolate and escalate. PC records actual recovery time/data loss, incidents and rebaseline.

Prerequisite: selective file and isolated AD restore from upstream runbook. No automated backup/failover is proven in the lab.
