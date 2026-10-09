# Business requirements document

> Fictional office and people. Planning and approvals are case-study simulations; technical results are historical lab evidence only.

**Version 1.0:** 9 October 2026. **Method:** source inspection, not real stakeholder elicitation. Business outcome: repeatable requests, least privilege, supportable services and evidence for the fictional office.

## Functional requirements
| ID | Requirement | MoSCoW | Fictional owner | Stories |
|---|---|---|---|---|
| BR-01 | Directory identity and recovery | Must | HR / IT | US-01 to US-06 |
| BR-02 | Revoke directory / peers; track SMB separately | Must | HR / IT | US-07, US-08, US-18 |
| BR-03 | Public files and restricted Finance | Must | FM | US-09 to US-12, US-20 |
| BR-04 | PDF printing and protected administration | Must | UR / IT | US-13 to US-16, US-21 |
| BR-05 | Individual lab remote access | Must | IT / SO | US-17, US-19 |
| BR-06 | Office service visibility | Should | IT / UR | US-22 to US-24 |
| BR-07 | Remove test access / preserve evidence | Must | SO / PC | US-25 |

## Nonfunctional requirements and gaps
- NFR-01 Security: loopback host bindings and no committed secrets. Code inspection supports bindings; no production penetration test.
- NFR-02 Reproducibility: pack builds with one command; clean clone validates evidence hashes and mappings.
- NFR-03 Availability: six-monitor UP snapshot is proven; no measured uptime SLA or 15-user capacity claim.
- NFR-04 Recovery: runbook proposes 14 daily off-host versions and monthly restore tests; no installed backup or measured RTO/RPO. Proposed targets: RTO 4h/RPO 24h, pending rehearsal.
- NFR-05 Usability: proposed starter and staff UAT; no real user attendance or survey result.

## Rules, data and interfaces
Manager approval precedes access (simulated). AD groups do not grant standalone SMB. Track request ID, person, role, approver, device peer, AD identity, SMB identity, timestamps and result privately. Never record keys/passwords in the tracker. Public/Finance/Scans are Samba shares; Office-PDF writes Scans/pdf. LAN 172.20.0.0/16, tunnel 10.8.0.0/24, domain ITOPS.LAB are lab facts.

## Acceptance and control
Each story uses Given/When/Then and has a UAT row. RTM qualifies component coverage. Full workflows, persistent Finance recreation, public VPN, physical printing, notifications and business capacity remain untested; these block real-office acceptance. PC maintains baseline; FM reviews access; HR reviews identity; IT verifies feasibility; SO reviews security; SP decides scope. Reviews are fictional planned activities. CR-001 illustrates change control. US IDs are stable regardless of Jira keys.
