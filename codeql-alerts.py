''' Imports'''
import argparse
import datetime
import pprint as pp
import requests
import pandas as pd
import config


# Argparse Setup
# parser = argparse.ArgumentParser()
# parser.add_argument(
#     '-o', '--org',
#     help='Target organization')


def describe_alerts(_session, _org):
    ''' For the given org generate a dictionary of all code-scanning alerts'''
    _alerts = []
    as_alerts_url = f'{config.base_url}/orgs/{_org}/code-scanning/alerts'
    response = _session.get(as_alerts_url)
    _alerts.extend(response.json())
    while 'next' in response.links.keys():
        response = _session.get(response.links['next']['url'])
        _alerts.extend(response.json())

    return _alerts


def parse_alerts(_alerts):
    ''' Parse the full response down to values that we need '''
    # GH format 2021-11-30T17:18:24Z
    now = datetime.datetime.now(datetime.timezone.utc)
    alert_list = []
    for alert in _alerts:
        rules = alert.get('rule')
        state = alert.get('state')
        severity = rules.get('severity')
        skip = ['note']
        if severity not in skip and state == 'open':
            repo = alert.get('repository')
            created = alert.get('created_at')
            created_ts = datetime.datetime.strptime(
                created,
                '%Y-%m-%dT%H:%M:%S%z'
                )
            timedelta = now - created_ts
            name = repo.get('name')
            url = alert.get('html_url')
            security_level = rules.get('security_severity_level', 'None')

            description = rules.get('description')
            alert_dict = {
                'repository': name,
                'description': description,
                'severity': severity,
                'security_level': security_level,
                'created_at': created,
                'timedelta': str(timedelta),
                'url': url
            }
            pp.pprint(alert_dict)
            alert_list.append(alert_dict)
    return alert_list


def write_xlsx(_parsed, _org):
    print(f'trying to write file for {_org}')
    today = datetime.date.today()
    ''' Create dataframe from list of dicts and write to xlsx'''
    _df = pd.DataFrame.from_dict(_parsed)
    _df.set_index('repository', inplace=True)
    _df.to_excel(f'reports/codeql-{_org}-{today}.xlsx')


if __name__ == '__main__':
    ''' Entrypoint '''
    # args = parser.parse_args()
    session = requests.Session()
    session.headers.update(config.rest_headers['headers'])
    session.params.update(config.rest_headers['params'])
    for org in config.orgs:
        try:
            alerts = describe_alerts(session, org)
            parsed = parse_alerts(alerts)
            write_xlsx(parsed, org)
        except KeyError:
            # Response is completely empty when an org has no results.
            pass
