# Remote Access process map

> Fictional office and people. Planning and approvals are case-study simulations; technical results are historical lab evidence only.

## Current state - assumed fictional baseline
```mermaid
flowchart TD
 S([Start]) --> A[Staff informal request] --> B[IT shares profile manually] --> C[Handshake treated as success] --> D[Missing route reported as file fault] --> E([End])
```

## Future state - proposed controlled process
BPMN-style flowchart: start/end events, task rectangles and decision gateways. This is not a BPMN 2.0 interchange file. Tasks identify their owner.
```mermaid
flowchart TD
 S([Start]) --> H
 H[Staff requests named device access] --> M{Manager and device approved?}
 M -->|No| X[Return request]
 M -->|Yes| V[IT creates individual peer]
 V --> D[Securely deliver current profile]
 D --> T[Verify handshake and route to 172.20.0.0/16]
 T --> B[Authenticate to Public through tunnel]
 B --> G{Handshake and files work?}
 G -->|No| F[Check AllowedIPs and permissions separately] --> T
 G -->|Yes| R[Record owner and revocation procedure]
 R --> E([Close request])
```

## Evidence and improvement measure
Case 01 proves handshake, route failure and Public access through an isolated Docker VPN client. No public endpoint is tested.
Proposed measure: request-to-completion time and rework rate across a 15-person pilot. No business KPI values were collected.
