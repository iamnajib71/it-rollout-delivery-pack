# UAT plan and evidence policy

> Fictional office and people. Planning and approvals are case-study simulations; technical results are historical lab evidence only.

Objective: assess 25 stories at lab component scope and expose real-office gaps. PC owns plan; IT executes technical checks; FM/UR/HR would attend business UAT. All attendees/approvals are fictional; no real business sign-off.

## Entry and environment
BRD reviewed; source revision pinned; no real data. Historical environment: Windows 11, Docker Desktop, PowerShell 5.1. Cases specify precondition, action, expectation, outcome, timestamp, proof and limit. Temporary identities and peers must be cleaned up. New source reruns follow upstream runbook and preserve new redacted evidence separately; never overwrite these historical transcripts.

## Execution and defects
Positive/negative access; recovery/revocation; queue output/admin; VPN route; visibility. Expected access denial is a pass. Critical: unintended access/security exposure, stops gate. High: core service unavailable, stops gate. Medium: workaround available. Low: cosmetic. PC logs ID, story, steps, expected/actual, owner, status and retest proof. No historical technical defect is inferred from successful runs; production coverage gaps stay in RAID.

## Exit
Historical component evidence: two scripts show zero failures; three cases recovered. Pack exit: validate.py and PDF build pass. Real-office exit: all Must requirements tested in deployed design, three-path revocation and restore proven, 15-person pilot accepted, zero Critical/High defects, owner and sponsor sign-off. These production criteria are not met.

## Limits
25 mappings are not 25 independent executions; compound tests are reused. HTTP response does not prove usability. AD flags do not prove Windows interactive login. Process approvals are not transcript evidence.
