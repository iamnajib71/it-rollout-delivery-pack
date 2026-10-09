# Historical lab UAT results

> Fictional office and people. Planning and approvals are case-study simulations; technical results are historical lab evidence only.

Real run date: **6 October 2026, Australia/Sydney**. Pack review: 9 October 2026. Retrospective component UAT evidence only; no new homelab run or business sign-off.

| Runner | Local timestamp | Observed result | Evidence filename |
|---|---|---|---|
| tests/homelab_check.ps1 | 2026-10-06 21:12:39 | 0 failed checks; 6 monitors UP | homelab-check-20261006-211239-566.txt |
| tests/ad_tasks.ps1 | 2026-10-06 15:55:16 | 0 failed checks; lifecycle tested | ad-tasks-20261006-155516-705.txt |
| tests/reproduce_cases.py | 2026-10-06 15:55:25 | 3 faults repaired and cleaned up | support-cases-20261006-155525.txt |

Exact snapshots: evidence/homelab/docs/evidence; SHA-256 and source URLs: evidence/manifest.json. Each UAT row names a specific assertion. homelab_check tests five running containers; ad_tasks separately checks directory health. Six-container coverage comes from both scripts, not six running assertions in the first.

Disposition: historical technical evidence accepted as input. 25 mappings pass at stated scope. Complete onboarding/offboarding, persistent SMB recreation, 15-person business UAT, physical print, restore, public VPN and production security are **not run / not proven**, not passed. Real-office go-live: **hold**. A fictional sponsor acknowledgement cannot change this.
