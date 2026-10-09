# CR-001: prove printing beyond HTTP

> Fictional office and people. Planning and approvals are case-study simulations; technical results are historical lab evidence only.

Worked fictional change: IT requests, PC reviews, SP scenario approves. This models control of the plan; no real historical approval claimed.

## Trigger and options
HTTP 200 can coexist with paused queues. Add queue checks, PDF artifact, IPP state 9 and paused-queue recovery. A: HTTP alone, rejected as inadequate. B: PDF plus recovery, selected. C: physical printer, separate prerequisite. Keep laser simulated.

## Impact and decision
Estimated 4h at AUD75 = AUD300, inside existing 80h labour allowance; baseline cost increase AUD0. One day within readiness allowance, no milestone movement. Reduces false green printing risk; no host exposure or Finance ACL change. SP scenario approves B; I-01 stays open.

## Implementation and verification
Update BR-04, US-13 / US-21, UAT-13 / UAT-21 and maintenance checklist. Historical homelab-check-20261006-211239-566.txt proves PDF artifact/state 9; support-cases-20261006-155525.txt proves original job recovery. These runs predate the illustrative CR. PC checks exact RTM proof. Closed for lab criteria on 9 October 2026; physical printing remains unproven.
