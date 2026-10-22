"""Import the fictional rollout into Jira Cloud. Never emits credentials."""
from pathlib import Path
import argparse
import base64
import csv
import json
import re
import sys
import time
from datetime import datetime, timezone
import urllib.error
import urllib.parse
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'jira'
MARKER = 'rollout-delivery-pack'


def rows(path):
    with (ROOT / path).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def save(name, value):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def adf(text):
    return {'version': 1, 'type': 'doc', 'content': [
        {'type': 'paragraph', 'content': [{'type': 'text', 'text': line}]} if line else
        {'type': 'paragraph', 'content': []} for line in text.splitlines()]}


def plan():
    rtm = {r['Story ID']: r for r in rows('business-analysis/traceability.csv')}
    records = []
    for theme in sorted({r['Epic theme'] for r in rtm.values()}):
        records.append({'source': 'epic-' + theme.lower(), 'type': 'Epic',
                        'summary': theme, 'description': 'Fictional case study: ' + theme})
    for story in rows('backlog.csv'):
        sid = story['Summary'].split(':')[0]
        trace = rtm[sid]
        records.append({'source': sid.lower(), 'type': 'Story', 'summary': story['Summary'],
            'requirement': trace['Requirement ID'], 'epic': 'epic-' + trace['Epic theme'].lower(),
            'points': int(story['Story Points']), 'priority': story['Priority'],
            'description': story['Description'] + '\n\nAcceptance criteria\n' + story['Acceptance Criteria']
                + '\n\nHistorical lab evidence (not current business-user UAT)\n'
                + trace['Exact proof'] + '\n' + trace['Source URL'] + '\nLimit: ' + trace['Limit']})
    for raid in rows('control/raid.csv'):
        records.append({'source': raid['ID'].lower(), 'type': 'Task',
            'summary': raid['ID'] + ': ' + raid['Description'], 'risk': raid['Impact'],
            'labels': ['raid', raid['Type'].lower(), 'source-status-' + re.sub('[^a-z0-9]+', '-', raid['Status'].lower())],
            'description': 'Fictional case study RAID item. Source state is preserved below; Jira starts in To Do.\n'
                + '\n'.join(k + ': ' + v for k, v in raid.items())
                + '\nNo review date is invented from a textual gate. Set a real review due date before enabling overdue automation.'})
    records.append({'source': 'cr-001', 'type': 'Task', 'summary': 'CR-001: prove printing beyond HTTP',
        'labels': ['change-request'], 'description': (ROOT / 'control/change-request-001.md').read_text(encoding='utf-8')})
    return records


def credentials():
    values = {}
    for line in (ROOT / '.env').read_text(encoding='utf-8-sig').splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            key, value = line.split('=', 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    keys = ('JIRA_BASE_URL', 'JIRA_EMAIL', 'JIRA_API_TOKEN')
    missing = [key for key in keys if not values.get(key)]
    if missing:
        raise RuntimeError('Missing required variables: ' + ', '.join(missing))
    base = values[keys[0]].rstrip('/')
    if '://' not in base:
        base = 'https://' + base
    if urllib.parse.urlsplit(base).scheme != 'https':
        raise RuntimeError('JIRA_BASE_URL must use HTTPS')
    return base, values[keys[1]], values[keys[2]]


class Jira:
    def __init__(self):
        self.base, email, token = credentials()
        self.auth = base64.b64encode((email + ':' + token).encode()).decode()

    def call(self, method, route, body=None):
        data = None if body is None else json.dumps(body).encode()
        for attempt in range(4):
            req = urllib.request.Request(self.base + route, data=data, method=method,
                headers={'Authorization': 'Basic ' + self.auth,
                         'Accept': 'application/json', 'Content-Type': 'application/json'})
            try:
                with urllib.request.urlopen(req, timeout=45) as response:
                    raw = response.read()
                    return json.loads(raw) if raw else None
            except urllib.error.HTTPError as error:
                if error.code == 429 and attempt < 3:
                    time.sleep(min(int(error.headers.get('Retry-After', '5')), 30))
                    continue
                # Jira validation messages contain field names, not request headers.
                # Redact credentials defensively before showing diagnostics.
                detail = error.read(4000).decode(errors='replace')
                _, email, token = credentials()
                for secret in (token, self.auth, email):
                    detail = detail.replace(secret, '[REDACTED]')
                raise RuntimeError(f'HTTP {error.code}: {method} {route}: {detail}') from None
            except urllib.error.URLError:
                raise RuntimeError('Jira network/DNS connection failed; no mutation result assumed') from None

    def search(self, jql, fields):
        result, token = [], None
        while True:
            body = {'jql': jql, 'fields': fields, 'maxResults': 100}
            if token:
                body['nextPageToken'] = token
            page = self.call('POST', '/rest/api/3/search/jql', body)
            result.extend(page['issues'])
            token = page.get('nextPageToken')
            if not token or page.get('isLast'):
                return result

    def pages(self, route):
        result, start = [], 0
        while True:
            join = '&' if '?' in route else '?'
            page = self.call('GET', route + join + f'startAt={start}&maxResults=100')
            result.extend(page['values'])
            start += len(page['values'])
            if page.get('isLast') or start >= page.get('total', start) or not page['values']:
                return result


def run(jira, key, me, records):
    """Only mutate a project owned by this importer; never alter shared workflows."""
    checkpoint = OUT / 'state.json'
    state = json.loads(checkpoint.read_text()) if checkpoint.exists() else {}
    if state and (state['site'] != jira.base or state['projectKey'] != key):
        raise RuntimeError('State belongs to another site/project; use a separate checkout')
    projects = jira.pages('/rest/api/3/project/search')
    project = next((p for p in projects if p['key'] == key), None)
    description = 'Fictional case study run in a real Jira site. Managed by ' + MARKER
    if project:
        full = jira.call('GET', '/rest/api/3/project/' + key)
        if MARKER not in full.get('description', ''):
            raise RuntimeError('Existing project is not marked as owned by this importer')
    else:
        project = jira.call('POST', '/rest/api/3/project', {
            'key': key, 'name': 'IT Rollout - Fictional Case Study', 'projectTypeKey': 'software',
            'projectTemplateKey': 'com.pyxis.greenhopper.jira:gh-scrum-template',
            'description': description, 'leadAccountId': me['accountId'], 'assigneeType': 'UNASSIGNED'})
    state.update({'site': jira.base, 'projectKey': key, 'projectId': project['id']})
    save('state.json', state)
    ensure_workflow(jira, state)
    fields = jira.pages('/rest/api/3/field/search?type=custom')
    custom = {}
    for name in ['Requirement ID', 'Risk rating']:
        matches = [f for f in fields if f['name'] == name]
        if len(matches) > 1:
            raise RuntimeError('Ambiguous custom field: ' + name)
        field = matches[0] if matches else jira.call('POST', '/rest/api/3/field', {
            'name': name, 'description': 'Fictional rollout case study',
            'type': 'com.atlassian.jira.plugin.system.customfieldtypes:textfield',
            'searcherKey': 'com.atlassian.jira.plugin.system.customfieldtypes:textsearcher'})
        if field.get('schema', {}).get('type') not in (None, 'string'):
            raise RuntimeError('Expected text custom field: ' + name)
        custom[name] = field['id']
    state['fields'] = custom
    save('state.json', state)
    estimate = next((f['id'] for f in fields if f['name'] == 'Story Points'), None)
    state['estimateField'] = estimate
    screens = jira.pages('/rest/api/3/screens')
    project_screens = [s for s in screens if s['name'].startswith(key + ':')]
    if not project_screens:
        raise RuntimeError('No dedicated project screens found; configure screens manually before resuming')
    for screen in project_screens:
        tabs = jira.call('GET', f'/rest/api/3/screens/{screen["id"]}/tabs')
        tab = tabs[0]['id']
        route = f'/rest/api/3/screens/{screen["id"]}/tabs/{tab}/fields'
        shown = {f['id'] for f in jira.call('GET', route)}
        for field_id in list(custom.values()) + ([estimate] if estimate else []):
            if field_id not in shown:
                jira.call('POST', route, {'fieldId': field_id})
    metadata = jira.call('GET', '/rest/api/3/project/' + key)
    types = {t['name']: t['id'] for t in metadata['issueTypes']}
    if not all(t in types for t in ['Epic', 'Story', 'Task']):
        raise RuntimeError('Scrum project must expose Epic, Story and Task issue types')
    existing = jira.search(f'project = {key} AND labels = "{MARKER}"', ['labels', 'summary'])
    by_source = {}
    source_labels = {'source-' + r['source'] for r in records}
    for issue in existing:
        for label in issue['fields']['labels']:
            if label in source_labels:
                if label in by_source:
                    raise RuntimeError('Duplicate source marker: ' + label)
                by_source[label] = issue['key']
    mapping = state.setdefault('issues', {})
    for record in records:
        source = record['source']
        label = 'source-' + source
        # Checkpoint immediately after creation protects reruns against search indexing lag.
        issue_key = mapping.get(source) or by_source.get(label)
        if issue_key:
            live = jira.call('GET', '/rest/api/3/issue/' + issue_key + '?fields=labels')
            if MARKER not in live['fields']['labels'] or label not in live['fields']['labels']:
                raise RuntimeError('Checkpoint ownership mismatch: ' + issue_key)
        else:
            payload = {'project': {'key': key}, 'issuetype': {'id': types[record['type']]},
                'summary': record['summary'], 'description': adf(record['description']),
                'labels': [MARKER, 'fictional-case-study', label] + record.get('labels', [])}
            if 'requirement' in record:
                payload[custom['Requirement ID']] = record['requirement']
                payload['parent'] = {'key': mapping[record['epic']]}
                payload['priority'] = {'name': record['priority']}
            if 'risk' in record:
                payload[custom['Risk rating']] = record['risk']
            if record['type'] == 'Story' and estimate:
                payload[estimate] = record['points']
            issue_key = jira.call('POST', '/rest/api/3/issue', {'fields': payload})['key']
        mapping[source] = issue_key
        save('state.json', state)
        print('Verified', source, issue_key)
    queries = {
        'UAT queue': f'project = {key} AND status = "In UAT" ORDER BY priority DESC',
        'High risks': f'project = {key} AND labels = risk AND "Risk rating" ~ "High" AND statusCategory != Done',
        'Blocked': f'project = {key} AND (labels = blocked OR Flagged = Impediment) AND statusCategory != Done',
        'Open risks': f'project = {key} AND labels = risk AND statusCategory != Done'}
    saved = state.setdefault('filters', {})
    owned = jira.call('GET', '/rest/api/3/filter/my')
    for name, jql in queries.items():
        title = key + ' - ' + name
        match = next((f for f in owned if f['name'] == title), None)
        if match:
            result = jira.call('PUT', '/rest/api/3/filter/' + match['id'], {'name': title, 'jql': jql})
        else:
            result = jira.call('POST', '/rest/api/3/filter', {'name': title, 'jql': jql, 'favourite': True})
        saved[name] = {'id': result['id'], 'jql': jql, 'url': jira.base + '/issues/?filter=' + result['id']}
        save('state.json', state)
    save('filters.json', saved)
    boards = jira.call('GET', '/rest/agile/1.0/board?projectKeyOrId=' + key + '&type=scrum')['values']
    if not boards:
        raise RuntimeError('Template did not create a Scrum board; see manual steps')
    board = boards[0]
    state['boardId'] = board['id']
    sprints = jira.call('GET', f'/rest/agile/1.0/board/{board["id"]}/sprint')['values']
    sprint_name = 'Pilot 1 - fictional rollout'
    sprint = next((s for s in sprints if s['name'] == sprint_name), None)
    if not sprint:
        sprint = jira.call('POST', '/rest/agile/1.0/sprint', {'name': sprint_name,
            'originBoardId': board['id'], 'goal': 'Prepare identity and least-privilege Finance pilot; fictional planning, no business UAT claimed.'})
    state['sprintId'] = sprint['id']
    # Planned scope: create/reset identity and verify Finance allow/deny; no invented progress.
    subset = [mapping['us-' + s] for s in ['01', '02', '09', '10']]
    if sprint['state'] == 'future':
        jira.call('POST', f'/rest/agile/1.0/sprint/{sprint["id"]}/issue', {'issues': subset})
    save('state.json', state)
    if not state.get('dashboardId'):
        dashboards = jira.call('GET', '/rest/api/3/dashboard/search?dashboardName=' + urllib.parse.quote(key + ' - Rollout status'))['values']
        dashboard = next((d for d in dashboards if d['name'] == key + ' - Rollout status'), None)
        if not dashboard:
            dashboard = jira.call('POST', '/rest/api/3/dashboard', {'name': key + ' - Rollout status',
                'description': description, 'sharePermissions': [], 'editPermissions': []})
        state['dashboardId'] = dashboard['id']
        save('state.json', state)
    export(jira, state)


def ensure_workflow(jira, state):
    name = state['projectKey'] + ' - Rollout UAT workflow'
    found = jira.call('GET', '/rest/api/3/workflow/search?workflowName=' + urllib.parse.quote(name))['values']
    if not found:
        references = [str(uuid.uuid5(uuid.NAMESPACE_URL, jira.base + '/' + name + '/' + str(i))) for i in range(4)]
        global_statuses = jira.call('GET', '/rest/api/3/status')
        definitions = []
        for i, (title, category) in enumerate([('To Do', 'TODO'), ('In Progress', 'IN_PROGRESS'),
                                               ('In UAT', 'IN_PROGRESS'), ('Done', 'DONE')]):
            status = next((s for s in global_statuses if s['name'].lower() == title.lower() and not s.get('scope')), None)
            definition = {'name': title, 'statusCategory': category, 'statusReference': references[i]}
            if status:
                definition['id'] = status['id']
            definitions.append(definition)
        transitions = [{'id': '1', 'name': 'Create', 'type': 'INITIAL', 'toStatusReference': references[0], 'links': []}]
        for i, title in enumerate(['Start work', 'Send to UAT', 'Accept'], 1):
            transitions.append({'id': str(i * 10 + 1), 'name': title, 'type': 'DIRECTED',
                'toStatusReference': references[i], 'links': [{'fromStatusReference': references[i - 1], 'fromPort': 0, 'toPort': 1}]})
        payload = {'scope': {'type': 'GLOBAL'}, 'statuses': definitions, 'workflows': [{
            'name': name, 'description': 'Fictional case study; sequential acceptance workflow',
            'statuses': [{'statusReference': references[i], 'properties': {}, 'layout': {'x': i * 200, 'y': 0}} for i in range(4)],
            'transitions': transitions}]}
        save('workflow-request.json', payload)
        save('workflow-created.json', jira.call('POST', '/rest/api/3/workflows/create', payload))
    schemes = jira.pages('/rest/api/3/workflowscheme')
    scheme = next((s for s in schemes if s['name'] == name), None)
    if not scheme:
        scheme = jira.call('POST', '/rest/api/3/workflowscheme', {'name': name, 'defaultWorkflow': name,
            'description': 'Dedicated to the fictional rollout case study'})
    association = jira.call('GET', '/rest/api/3/workflowscheme/project?projectId=' + str(state['projectId']))
    current = association['values'][0]['workflowScheme']['id']
    if str(current) != str(scheme['id']):
        switched = jira.call('POST', '/rest/api/3/workflowscheme/project/switch', {
            'projectId': str(state['projectId']), 'targetSchemeId': str(scheme['id'])})
        save('workflow-switch.json', switched)
        # Workflow switches can be asynchronous. Verify before creating/filtering issues.
        for attempt in range(10):
            live = jira.call('GET', '/rest/api/3/workflowscheme/project?projectId=' + str(state['projectId']))
            if str(live['values'][0]['workflowScheme']['id']) == str(scheme['id']):
                break
            time.sleep(2)
        else:
            raise RuntimeError('Workflow migration pending; rerun after Jira finishes')
    state['workflowSchemeId'] = scheme['id']
    save('state.json', state)
    save('workflow.json', jira.call('GET', '/rest/api/3/workflow/search?workflowName=' + urllib.parse.quote(name) + '&expand=statuses,transitions'))


def export(jira, state):
    if state['site'] != jira.base:
        raise RuntimeError('Export state belongs to another Jira site')
    fields = ['summary', 'issuetype', 'status', 'parent', 'labels', 'assignee', 'updated', 'description',
              state['fields']['Requirement ID'], state['fields']['Risk rating']]
    if state.get('estimateField'):
        fields.append(state['estimateField'])
    issues = jira.search(f'project = {state["projectKey"]} AND labels = "{MARKER}" ORDER BY key', fields)
    if {i['key'] for i in issues} != set(state['issues'].values()):
        raise RuntimeError('Search export incomplete (possibly indexing lag); rerun --export-only later')
    OUT.mkdir(exist_ok=True)
    headers = ['Key', 'Issue type', 'Summary', 'Status', 'Epic', 'Requirement ID', 'Risk rating', 'Labels', 'Assignee', 'Updated', 'URL']
    with (OUT / 'issues.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        for issue in issues:
            f = issue['fields']
            writer.writerow(dict(zip(headers, [issue['key'], f['issuetype']['name'], f['summary'], f['status']['name'],
                (f.get('parent') or {}).get('key', ''), f.get(state['fields']['Requirement ID'], ''),
                f.get(state['fields']['Risk rating'], ''), ';'.join(f['labels']),
                (f.get('assignee') or {}).get('displayName', ''), f['updated'], jira.base + '/browse/' + issue['key']])))
    save('issues-api.json', {'capturedAt': datetime.now(timezone.utc).isoformat(),
                            'fictionalCaseStudy': True, 'issues': issues})
    save('board.json', jira.call('GET', f'/rest/agile/1.0/board/{state["boardId"]}/configuration'))
    save('sprint.json', jira.call('GET', f'/rest/agile/1.0/sprint/{state["sprintId"]}'))
    save('dashboard.json', jira.call('GET', '/rest/api/3/dashboard/' + state['dashboardId']))
    print('Exported verified Jira issues:', len(issues))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probe', action='store_true')
    parser.add_argument('--plan', action='store_true', help='Validate and write proposed source manifest; no network')
    parser.add_argument('--project-key', default='ITROLL')
    parser.add_argument('--export-only', action='store_true')
    args = parser.parse_args()
    records = plan()
    if args.plan:
        save('import-plan.json', {'status': 'SOURCE_MANIFEST (execution recorded separately in state.json)', 'fictionalCaseStudy': True, 'records': records})
        print('Validated source records:', len(records))
        return
    if not re.fullmatch('[A-Z][A-Z0-9]{1,9}', args.project_key):
        raise RuntimeError('Use a Jira project key of 2-10 uppercase letters/digits')
    jira = Jira()
    try:
        me = jira.call('GET', '/rest/api/3/myself')
    except RuntimeError as error:
        save('access-check.json', {'capturedAt': datetime.now(timezone.utc).isoformat(),
             'site': jira.base, 'status': 'BLOCKED', 'operation': 'GET /rest/api/3/myself',
             'error': str(error), 'mutationsAttempted': False})
        raise
    print(json.dumps({'site': jira.base, 'accountId': me['accountId'], 'displayName': me['displayName']}))
    save('access-check.json', {'capturedAt': datetime.now(timezone.utc).isoformat(),
         'site': jira.base, 'status': 'AUTHENTICATED', 'operation': 'GET /rest/api/3/myself'})
    if args.export_only:
        export(jira, json.loads((OUT / 'state.json').read_text()))
        return
    if not args.probe:
        run(jira, args.project_key, me, records)
        return
    for route in ['/rest/api/3/mypermissions?permissions=ADMINISTER,CREATE_PROJECT',
                  '/rest/api/3/project/search', '/rest/api/3/field']:
        result = jira.call('GET', route)
        if route.endswith('/field'):
            result = [{'id': f['id'], 'name': f['name']} for f in result
                      if f['name'] in ('Requirement ID', 'Risk rating', 'Story Points', 'Story point estimate')]
        print(json.dumps(result))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
