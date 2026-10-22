# Real Jira run verification

Fictional case study run in a real Jira Cloud site on 22 October 2026 (Australia/Sydney). Office delivery, people, approvals and acceptance remain fictional. The configuration, API requests, exported issue keys and screenshots are real.

## Created and verified

| Item | Actual result | Evidence |
| --- | --- | --- |
| Scrum project | ITROLL, project ID 10001 | [State](state.json), [board configuration](board.json) |
| Epics | 5, using source traceability themes | [CSV](issues.csv), [source manifest](import-plan.json) |
| Stories | 25, with exact Given/When/Then, BR IDs, parent epic and source estimates | [API export](issues-api.json), `scripts/verify_jira.py` |
| RAID | 12 labelled tasks, including 4 risks | [CSV](issues.csv); original gates, owners and source states retained in descriptions |
| Worked change | CR-001 imported as ITROLL-43 | [CSV](issues.csv), [API export](issues-api.json) |
| Workflow | To Do → In Progress → In UAT → Done | [Workflow readback](workflow.json), [mapping capture](screenshots/board-columns.png) |
| Fields and screens | Requirement ID and Risk rating; added to dedicated ITROLL default/bug screens alongside Story Points | [State](state.json), [source verification](../scripts/verify_jira.py) |
| Automation | 2 enabled, scoped only to project 10001 | [Actual API export](automation-rules.json), [actual rules page](screenshots/automation-rules.png) |
| Pilot sprint | 4 stories, 8 source story points, active with a 14-day window | [Sprint](sprint.json), [board](screenshots/board.png) |
| Filters | UAT queue, High risks, Blocked, plus Open risks for the gadget | [JQL and IDs](filters.json) |
| Dashboard | Sprint burndown, status pie chart and open-risk results, configured in the UI | [Dashboard capture](screenshots/dashboard.png), [gadgets readback](dashboard-gadgets.json) |
| Status reporting | 25 stories: 23 To Do, 1 In Progress, 1 In UAT, 0 Done; 4 open risks, 3 rated High | [CSV](issues.csv), [Excel](status-report.xlsx), [report verification](report-verification.json) |

## Actual checks and problems resolved

- Initial Jira API authentication endpoint returned HTTP 404; the site root redirected to Confluence. No Jira mutation was attempted until the account owner enabled/corrected access. The final [access check](access-check.json) records successful authentication.
- Jira rejected custom fields absent from the project create screen. Added them to dedicated project screens. Administrator field discovery required pagination after additional site fields appeared; verification caught a retry selecting newly created empty duplicates. Corrected pagination, restored the original field IDs, and moved unused duplicates from this run into recoverable Jira trash. Shared Default Screen placement from the first attempt was undone. No pre-existing issue or project was deleted.
- Workflow creation rejected numeric status references; used stable UUID references. Jira also enforced a sprint-name limit; shortened the pilot name. The active workflow and sprint were read back from Jira.
- A full corrected importer rerun verified the same 43 source-to-Jira mappings and exported 43 issues. It did not reset the two exercise statuses or create another issue. `verify_jira.py` checks every story's acceptance lines, requirement, estimate and epic against the existing repository artefacts; it also checks the mapped columns, active sprint and enabled project-scoped rules.
- The UAT rule was exercised by moving ITROLL-6 to In UAT: the [readback](uat-rule-verification.json) shows In UAT and assignee Nazmul Hassan Najib. The overdue rule also passed a live test using Jira's **Run scheduled flow now**: ITROLL-33 received a temporary fictional date of 21 October 2026, then the rule added `risk-review-overdue` and Flagged = Impediment. Its original date, labels and flag were restored and checked exactly. [Test purpose](risk-test-purpose.json) · [before](risk-test-before.json) · [after rule](risk-test-after-rule.json) · [restored](risk-test-restored.json). This verifies the rule path, not an unattended real business deadline. Source RAID gates are not calendar dates; follow [manual steps](manual-steps.md) to set agreed review dates.
- The report was built directly from `issues.csv`. It independently reconciled story, UAT and risk counts, changed one source status temporarily to test formula recalculation, restored it, scanned for formula errors and rendered both sheets for visual review. [Formula/reconciliation record](report-verification.json). It is a static export with formula-linked analysis, not a live Jira connector.

The sprint has no completed work or elapsed delivery history to substantiate velocity or time saved. Its burndown is a real new-sprint chart. All Jira records start open except the two explicitly documented administration transitions; source lab-mitigated/closed states are preserved without claiming a new business approval. Existing historical homelab evidence remains unchanged.

[Successful scheduled-rule audit capture](screenshots/risk-rule-audit.png) shows Jira's Success result and the Scheduled / Edit work item operations.

## Repository checks

The existing pack validator, PDF build and Pages staging completed successfully. The rebuilt PDF has 64 pages. The subsequent validator checked the rebuilt media and returned zero failed pack checks. Jira snapshot verification and Python compilation also passed. CI now runs the Jira snapshot checks without credentials; live Jira mutation is never part of CI. [Final command output](checks.txt).
