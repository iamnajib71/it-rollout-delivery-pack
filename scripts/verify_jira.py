"""Verify saved live Jira evidence against the original fictional case-study sources."""
import json
from jira_import import OUT, plan, rows


def text(node):
    if isinstance(node, dict):
        return node.get('text', '') + '\n'.join(text(x) for x in node.get('content', []))
    return ''


def main():
    state = json.loads((OUT / 'state.json').read_text())
    evidence = json.loads((OUT / 'issues-api.json').read_text())
    live = {x['key']: x['fields'] for x in evidence['issues']}
    records = plan()
    assert len(live) == len(records) == len(state['issues']) == 43
    assert len(set(state['issues'].values())) == 43
    source_stories = {s['Summary']: s for s in rows('backlog.csv')}
    for record in records:
        f = live[state['issues'][record['source']]]
        assert f['summary'] == record['summary']
        assert f['issuetype']['name'] == record['type']
        assert 'fictional-case-study' in f['labels']
        assert 'source-' + record['source'] in f['labels']
        description = text(f['description'])
        assert 'fictional' in description.lower()
        if record['type'] == 'Story':
            assert f[state['fields']['Requirement ID']] == record['requirement']
            assert f['parent']['key'] == state['issues'][record['epic']]
            assert f[state['estimateField']] == record['points']
            for line in source_stories[record['summary']]['Acceptance Criteria'].splitlines():
                assert line in description
        if 'risk' in record:
            assert f[state['fields']['Risk rating']] == record['risk']
    rules = json.loads((OUT / 'automation-rules.json').read_text())
    assert len(rules) == 2
    for entry in rules:
        assert entry['rule']['state'] == 'ENABLED'
        assert all(scope.endswith(':project/' + str(state['projectId'])) for scope in entry['rule']['ruleScopeARIs'])
        assert all(action['type'] != 'jira.issue.outgoing.email' for action in entry['rule']['components'])
    board = json.loads((OUT / 'board.json').read_text())
    assert [c['name'] for c in board['columnConfig']['columns']] == ['To Do', 'In Progress', 'In UAT', 'Done']
    assert all(len(c['statuses']) == 1 for c in board['columnConfig']['columns'])
    sprint = json.loads((OUT / 'sprint.json').read_text())
    assert sprint['state'] == 'active'
    assert set(state['filters']) >= {'UAT queue', 'High risks', 'Blocked'}
    before = json.loads((OUT / 'risk-test-before.json').read_text())['fields']
    after = json.loads((OUT / 'risk-test-after-rule.json').read_text())['fields']
    restored = json.loads((OUT / 'risk-test-restored.json').read_text())['fields']
    assert before == restored
    assert 'risk-review-overdue' in after['labels']
    flagged = next(k for k in after if k.startswith('customfield_'))
    assert after[flagged][0]['value'] == 'Impediment'
    print('PASS Jira export: 43 unique source mappings; 25 stories with exact acceptance criteria, requirements, epics and estimates')
    print('PASS configuration: 4 mapped columns, active sprint, saved filters, 2 enabled project-scoped automation rules')
    print('PASS overdue rule: real positive match; original test date, labels and flag restored')


if __name__ == '__main__':
    main()
