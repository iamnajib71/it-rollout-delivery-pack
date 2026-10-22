# Jira CSV import instructions

> Fictional office and people. Planning and approvals are case-study simulations; technical results are historical lab evidence only.

Root backlog.csv has 25 Story rows and exactly: Summary, Issue Type, Description, Acceptance Criteria, Priority, Epic Link, Story Points. UTF-8, quoted multiline Given/When/Then cells. Map fields and preview before import. US-xx is a stable portfolio identifier, not a Jira key.

Epic Link is intentionally blank: Jira needs actual target-project epic keys. Themes are in traceability.csv. Create Identity, Files, Printing, Remote and Monitoring epics, then populate actual keys if supported. Team-managed/newer projects may use Parent instead; map to available fields. Acceptance Criteria needs a multiline custom field; alternatively merge it into Description. Map Story Points to the project estimate field. Priority names must exist. This CSV is schema-validated; no completed Jira import is claimed.

Preview 25 stories, no errors, preserved line breaks, estimates and priorities. Spot-check against RTM. Do not reimport without deduplication. Fictional approvals are not recorded transactions.

## Actual REST API import

The case study has now been imported into a real Jira Cloud site with `scripts/jira_import.py`. It uses source labels and saved Jira keys for reruns, places acceptance criteria in the description, sets Requirement ID and Story Points on dedicated project screens, and uses Parent to link stories to the five actual epic keys. The root CSV remains a portable source artefact. [Real run and limitations](../jira/verification.md) · [Live CSV export](../jira/issues.csv). The earlier CSV instructions above describe the alternative manual import method; the schema-validation statement does not describe the new API execution.
