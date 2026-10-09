# Offboarding process map

> Fictional office and people. Planning and approvals are case-study simulations; technical results are historical lab evidence only.

## Current state - assumed fictional baseline
```mermaid
flowchart TD
 S([Start]) --> A[HR sends informal email] --> B[IT disables one account] --> C[SMB or VPN access remains] --> D[No complete revocation record] --> E([End])
```

## Future state - proposed controlled process
BPMN-style flowchart: start/end events, task rectangles and decision gateways. This is not a BPMN 2.0 interchange file. Tasks identify their owner.
```mermaid
flowchart TD
 S([Start]) --> H
 H[HR supplies identity, time and device inventory] --> M{Request approved?}
 M -->|No| X[Resolve with HR]
 M -->|Yes| A[IT disables AD and verifies denied LDAP bind]
 A --> B[IT removes Samba Compose user and recreates fileserver]
 B --> V[IT revokes all device peers]
 V --> T[IT verifies AD denial, SMB denial and peer absence]
 T --> G{All paths revoked?}
 G -->|No| F[Escalate incomplete revocation] --> T
 G -->|Yes| R[Collect devices and record retention]
 R --> E([Coordinator closes record])
```

## Evidence and improvement measure
AD disable and peer deletion are proven separately. A complete leaver workflow including persistent SMB removal was not run.
Proposed measure: request-to-completion time and rework rate across a 15-person pilot. No business KPI values were collected.
