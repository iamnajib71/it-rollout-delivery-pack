# Schedule and milestones

> Fictional office and people. Planning and approvals are case-study simulations; technical results are historical lab evidence only.

**Fictional proposed rollout baseline**, not a reconstruction of engineering dates. Historical validation on 6 October is an input. This models a future pilot. Finish-to-start dependencies unless parallel; weekends excluded. Planned effort 80h; 15 working days. Hardware availability assumed; otherwise rebaseline.

```mermaid
gantt
 title Fictional Cedar Office pilot
 dateFormat YYYY-MM-DD
 excludes weekends
 section Initiation and analysis
 Charter and roles :a, 2026-10-12, 2d
 Scope gate :milestone, m1, after a, 0d
 Requirements and process review :b, after a, 3d
 Estimate and RAID baseline :c, after a, 3d
 Baseline gate :milestone, m2, after b, 0d
 section Readiness
 Configuration and recovery rehearsal :d, after b, 4d
 Staff pilot UAT :e, after d, 3d
 Pilot gate :milestone, m3, after e, 0d
 section Transition
 Cutover rehearsal :f, after e, 1d
 Lab go-live gate :milestone, m4, after f, 0d
 Hypercare and closure :g, after f, 2d
 Handover :milestone, m5, after g, 0d
```

Critical chain: charter -> requirements -> readiness -> pilot -> rehearsal -> closure. PC reviews variance weekly; >2 working days requires sponsor decision. Physical printing, restore, capacity and security are prerequisites for production; this is not an authorised production schedule.
