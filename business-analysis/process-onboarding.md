# Onboarding process map

> Fictional office and people. Planning and approvals are case-study simulations; technical results are historical lab evidence only.

## Current state - assumed fictional baseline
```mermaid
flowchart TD
 S([Start]) --> A[HR emails starter request] --> B[IT creates account ad hoc] --> C[Missing access discovered] --> D[Rework and informal closure] --> E([End])
```

## Future state - proposed controlled process
BPMN-style flowchart: start/end events, task rectangles and decision gateways. This is not a BPMN 2.0 interchange file. Tasks identify their owner.
```mermaid
flowchart TD
 S([Start]) --> H
 H[HR submits role, date and device] --> M{Manager approves?}
 M -->|No| X[Return request]
 M -->|Yes| A[IT creates AD user and groups]
 A --> B[IT separately provisions persistent Samba identity]
 B --> V[IT creates named VPN peer and securely delivers profile]
 V --> T[IT verifies LDAP, share allow/deny and tunnel route]
 T --> G{Tests pass?}
 G -->|No| F[IT logs and fixes defect] --> T
 G -->|Yes| U[Staff proposed usability UAT]
 U --> E([Coordinator records completion])
```

## Evidence and improvement measure
AD create/group tests and Finance support case prove components. Persistent provisioning, profile delivery and staff usability acceptance are proposed.
Proposed measure: request-to-completion time and rework rate across a 15-person pilot. No business KPI values were collected.
