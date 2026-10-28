# Jira UI configuration and manual follow-up

Fictional case study run in a real Jira site. These steps distinguish UI work completed during this run from future work that requires an actual review decision. No paid feature or upgrade was used.

## UI steps completed during the run

1. Signed in to the site in the browser; API tokens do not create browser sessions. The account owner completed sign-in.
2. Opened ITROLL board → Board settings → Columns. Added **In UAT**, placed it between **In Progress** and **Done**, and mapped the existing In UAT status into it. The public Agile board configuration API exposes a read operation, so the column edit was performed in the UI. With a keyboard, focus a column/status, press Space, use arrows, and press Space to drop. [Actual mapping](board.json) and [capture](screenshots/board-columns.png).
3. Opened dashboard → Edit. For Sprint burndown, chose ITROLL board and Pilot 1 - fictional rollout, enabled board/sprint names, then saved. For Filter results, chose **ITROLL - Open risks** and saved. For Pie chart, chose **IT Rollout - Fictional Case Study** and **Status**, then saved. Waited for each save before leaving edit mode. [Dashboard](screenshots/dashboard.png). Gadget creation is scripted; these preferences were set through the supported UI.
4. Started the pilot sprint with a 14-day window on 22 October 2026. Its four source stories are US-01, US-02, US-09 and US-10, each estimated at 2 points in the source backlog. Actual timestamps are in [sprint.json](sprint.json). The importer leaves a newly created sprint planned; it does not start or restart sprints on reruns.
5. Moved US-01 through In Progress to In UAT and US-02 to In Progress as administration exercises. Each issue has an explanatory comment. The UAT rule assigned the account owner. This is not business-user acceptance or proof of completing a rollout.

## Manual follow-up for meaningful operating evidence

- Decide actual review due dates for the risk records. The source RAID uses gates such as “Before production”; the importer preserves those words and does not invent dates. Set **Due date** to the agreed risk review date. The enabled rule checks at 08:00 Australia/Sydney daily for open, risk-labelled issues overdue before today, adds `risk-review-overdue`, and sets Flagged to Impediment. It excludes already-labelled issues to avoid repeated changes. Clear the flag/label after a real review and set the next agreed due date. This is a review convention, not a new custom review-date field.
- Both rules passed live administration exercises. For the overdue rule, ITROLL-33 temporarily received a clearly labelled fictional test review date; **Run scheduled flow now** added the overdue label and Impediment flag. Original date, labels and flag were then restored. [Before](risk-test-before.json), [after rule](risk-test-after-rule.json), [restored](risk-test-restored.json). This verifies the scheduled rule's action path, not unattended passage of a real review date. Inspect Space settings → Automation → Audit log after an agreed date becomes overdue. Check plan execution quotas under Usage; this run did not establish a plan quota or purchase anything.
- To change the UAT owner, edit the **ITROLL - Assign UAT owner** rule's assignee. It currently uses the authenticated account as the sole real owner; fictional RACI participants were not created as Jira users. The configure script uses the authenticated account on rerun.
- Only move a story to Done after the relevant acceptance evidence and limitations are reviewed. Completing the sprint and gathering business-user UAT remain separate future activities.

## Rebuild the report and evidence

Run `python scripts/jira_import.py --export-only`, then `python scripts/verify_jira.py`. Refresh the browser and capture the actual board and dashboard into `jira/screenshots/`. The committed PNGs are actual Jira pages, not reconstructed charts. Automation definitions are actual GET responses from the public Automation API, not a guessed import file. Use `scripts/jira_configure.py` to recreate them in another site rather than importing IDs from this site.

The Excel report builder is `scripts/jira_report.mjs`. It needs a local Node.js runtime and the `@oai/artifact-tool` spreadsheet package; it is not a pip dependency.

For a fresh site, create the project with `jira_import.py`, map UAT into the board as above, run `jira_configure.py`, configure the three gadget preferences, and start a suitable sprint manually. Run only one importer at a time; retain `state.json` and resolve uncertain create responses before retrying. The script creates missing source issues but does not synchronise changed source text into existing issues.

## Official API references used

- [Jira Cloud REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/) for projects, fields, screens, issues, filters, workflows and dashboards.
- [Workflow API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflows/) for dedicated workflow creation; the live endpoint required UUID status references.
- [Automation rule management](https://developer.atlassian.com/cloud/automation/rest/api-group-rule-management/) and [API-token authentication](https://developer.atlassian.com/cloud/automation/security/authentication/) for creation, update and readback.
