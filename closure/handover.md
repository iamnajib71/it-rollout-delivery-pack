# Operational handover

> Fictional office and people. Planning and approvals are case-study simulations; technical results are historical lab evidence only.

Recipient: Noah Reed (fictional technical lead). State: evidence-backed lab documentation; production acceptance on hold. Technical builder / author: Nazmul Hassan. Primary [homelab runbook](https://github.com/iamnajib71/it-support-homelab/blob/e33df8d0ec8dc2148438d379fc69e57701d7baf8/docs/homelab-runbook.md); local snapshot evidence/homelab/docs/homelab-runbook.md.

Services: wg-easy 14; standalone Samba Public/Finance/Scans; CUPS PDF / simulated laser; Samba AD ITOPS.LAB; six Kuma monitors; Homepage. Runbook owns ports, starter/leaver/lost-device, printing, backup proposal and config. Get credentials privately from lab owner. Never place .env/peer keys here.

Intake: capture person/device/path, impact, time and change history. Verify access allow/deny, route and actual job completion, not availability alone. Use three source cases as examples. Lost device: revoke named peer. Leaver: revoke AD, SMB and all peers separately.

Open actions: I-01 physical print, I-02 staffed/capacity UAT, I-03 restore, D-03 persistent SMB, R-02 resilience and R-04 hardening. PC retains RAID; SP owns go/no-go. No implemented support SLA or external alert channel. Fictional acknowledgement is not operational acceptance; real recipient confirms runbook, secure credentials, restore, monitoring and action ownership first.
