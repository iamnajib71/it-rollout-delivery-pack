# Project charter

> Fictional office and people. Planning and approvals are case-study simulations; technical results are historical lab evidence only.

**Project:** Cedar Office IT rollout. Cedar Office and all 15 staff are fictional. **Case-study author / technical builder:** Nazmul Hassan. **Sponsor:** Maya Chen (fictional Operations Director). **Baseline:** 9 October 2026. Historical lab validation: 6 October 2026.

## Business problem and objectives
The fictional office uses individual local accounts, ad hoc file copies, manual printer diagnosis and informal remote-access requests. This is an assumed scenario, not an interview finding. Deliver a repeatable lab model for shared files, individual VPN profiles, queue administration, separate directory tasks and service visibility. Demonstrate planning, requirements, control and evidence-based handover.

## Scope
In: WireGuard peer lifecycle and isolated tunnel test; Public/Finance/Scans permissions; CUPS PDF output and simulated laser queue; Samba AD ITOPS.LAB account administration; six Kuma monitors; Homepage; documentation; traceability and PDF.
Out: real deployment, 15-user load testing, internet VPN, physical printing, Windows domain join/RSAT/GPO, AD-to-SMB integration, MFA, scheduled backups, external alerts, email migration and production certification.

## Assumptions and constraints
Fifteen staff: Operations 3, Finance 3, Sales 5, IT/support 2, management 2 (fictional). Windows/Docker host exists for the lab. Sponsor owns scope; Finance approves restricted access; analyst maintains separate AD/SMB/VPN records. Docker access is privileged. Service host ports remain loopback-bound. Production estimates require quotes and design approval. No real business-user sign-off is claimed.

## Success and gates
1. All 25 stories link to specific existing evidence and an explicit scope limit.
2. Recorded homelab and AD runs show zero failed checks; three fault recoveries have before/after proof.
3. Handover covers independent revocation of AD, SMB and VPN.
4. Pack validation and PDF build pass from clean clone; 30-90 second local demo is reproducible.
5. Real-office rollout stays on hold pending restore rehearsal, physical device test, load test and security review.

## Authority and tolerances
Budget: planning/budget.md. Sponsor approval for >10% cost or >2 working days schedule movement and production exposure. Coordinator logs changes before implementation. A failed critical access test stops cutover. Scenario acceptance: accept the evidence-backed lab deliverable; do not authorise real-office go-live. This is a model decision, not a signed approval.
