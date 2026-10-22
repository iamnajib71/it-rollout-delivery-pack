"""Configure project automation and dashboard gadgets; rerunnable after jira_import.py."""
import copy
import json
import sys
from jira_import import Jira, OUT, save


def configure(jira, state):
    cloud = jira.call('GET', '/_edge/tenant_info')['cloudId']
    base = f'/gateway/api/automation/public/jira/{cloud}/rest/v1'
    scope = f'ari:cloud:jira:{cloud}:project/{state["projectId"]}'
    summaries = jira.call('GET', base + '/rule/summary')['data']
    rules = []
    me = jira.call('GET', '/rest/api/3/myself')['accountId']
    flagged = next(f['id'] for f in jira.pages('/rest/api/3/field/search?type=custom') if f['name'] == 'Flagged')
    uat = next(s['id'] for s in jira.call('GET', '/rest/api/3/status') if s['name'] == 'In UAT')
    drafts = json.loads((OUT / 'automation-drafts.json').read_text()) if (OUT / 'automation-drafts.json').exists() else []
    for i, (template, name) in enumerate([
        ('software_template_23', state['projectKey'] + ' - Assign UAT owner'),
        ('software_template_20', state['projectKey'] + ' - Flag overdue risk reviews')]):
        match = next((r for r in summaries if r['name'] == name and scope in r['ruleScopeARIs']), None)
        if match:
            live = jira.call('GET', base + '/rule/' + match['uuid'])
        elif i < len(drafts):
            live = jira.call('GET', base + '/rule/' + drafts[i]['rule']['uuid'])
        else:
            result = jira.call('POST', base + '/template/create', {'templateId': template,
                'ruleHome': scope, 'state': 'DISABLED'})
            live = jira.call('GET', base + '/rule/' + result['ruleUuid'])
            drafts.append(live)
            save('automation-drafts.json', drafts)
        rule = live['rule']
        rule.update({'name': name, 'state': 'ENABLED', 'actor': {'type': 'ACCOUNT_ID', 'actor': me},
            'writeAccessType': 'OWNER_ONLY', 'ruleScopeARIs': [scope],
            'description': 'Fictional case study run in a real Jira site. No email action.'})
        action = copy.deepcopy(live['rule']['components'][0])
        action.update({'type': 'jira.issue.edit', 'component': 'ACTION', 'schemaVersion': 12,
            'children': [], 'value': {'operations': [], 'advancedFields': None, 'sendNotifications': False}})
        if i == 0:
            rule['trigger']['value']['toStatus'] = [{'type': 'ID', 'value': uat}]
            action['value']['advancedFields'] = json.dumps({'fields': {'assignee': {'id': me}}})
        else:
            rule['trigger']['value'].update({'jql': f'project = {state["projectKey"]} AND labels = risk '
                'AND due < startOfDay() AND statusCategory != Done AND labels not in (risk-review-overdue)',
                'executionMode': 'jql', 'onlyUpdatedIssues': False})
            rule['trigger']['value']['schedule']['rRule'] = (
                'BEGIN:VEVENT\nDTSTART;TZID=Australia/Sydney:20261022T080000\n'
                'RRULE:FREQ=DAILY;BYHOUR=8;BYMINUTE=0;BYSECOND=0;INTERVAL=1\nEND:VEVENT')
            action['value']['advancedFields'] = json.dumps({'update': {'labels': [{'add': 'risk-review-overdue'}]},
                'fields': {flagged: [{'value': 'Impediment'}]}})
        rule['components'] = [action]
        for key in ['created', 'updated']:
            rule.pop(key, None)
        jira.call('PUT', base + '/rule/' + rule['uuid'], {'rule': rule, 'connections': []})
        verified = jira.call('GET', base + '/rule/' + rule['uuid'])
        rules.append(verified)
        print('Verified automation:', name, verified['rule']['state'])
    save('automation-rules.json', rules)
    state['automationRuleUuids'] = [r['rule']['uuid'] for r in rules]
    save('state.json', state)
    dashboard = str(state['dashboardId'])
    available = jira.call('GET', '/rest/api/3/dashboard/gadgets')['gadgets']
    existing = jira.call('GET', f'/rest/api/3/dashboard/{dashboard}/gadget')['gadgets']
    for i, title in enumerate(['Sprint burndown gadget', 'Pie chart', 'Filter results']):
        gadget = next(g for g in available if g['title'] == title)
        if not any(g.get('uri') == gadget['uri'] for g in existing):
            jira.call('POST', f'/rest/api/3/dashboard/{dashboard}/gadget', {'uri': gadget['uri'],
                'title': title, 'position': {'column': i % 2, 'row': i // 2}, 'color': 'blue'})
    save('dashboard-gadgets.json', jira.call('GET', f'/rest/api/3/dashboard/{dashboard}/gadget'))


if __name__ == '__main__':
    try:
        configure(Jira(), json.loads((OUT / 'state.json').read_text()))
    except (RuntimeError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
