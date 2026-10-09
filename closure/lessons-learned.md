# Lessons learned

> Fictional office and people. Planning and approvals are case-study simulations; technical results are historical lab evidence only.

## Evidence-grounded technical lessons
- Source results record CRLF hash parsing broke VPN admin login; robust parsing plus API check verified the fix.
- AD container ACLs needed xattr TDB backend; SYSVOL check passes. Test actual storage behaviour.
- Samba LDAP lacks Who am I extension; authenticated search verifies unlock.
- Case 01: handshake alone misses a route failure; verify wg0 route and authenticated file access.
- Case 02: Finance is a standalone Samba group; fix membership without widening ACLs.
- Case 03: HTTP availability misses paused queues; verify original job reaches state 9.

## Project / BA reflections
Traceability needs specific assertions and scope limits. Fictional approvals are not elicitation evidence. Keep assumed dates, estimates and real outcomes separate. Record production gaps with owners before claiming office readiness.

## Actions
IT: persistent provisioning and independent revocation; SO: production security; IT: backup/restore rehearsal; PC: real staff/capacity UAT; UR: physical print test. Open for real deployment. No real retrospective workshop claimed.
