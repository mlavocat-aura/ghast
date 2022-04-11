''' Imports '''
import pandas as pd
import datetime
import argparse
import requests
import config

# Argparse Setup
parser = argparse.ArgumentParser()
parser.add_argument(
    '-o', '--org',
    help='Target organization',
    required=True
    )


def describe_alerts(_session, _org):
    ''' Get all alerts from GH '''
    _alerts = []
    as_alerts_url = f'{config.base_url}/orgs/{_org}/secret-scanning/alerts'
    response = _session.get(as_alerts_url)
    _alerts.extend(response.json())
    while 'next' in response.links.keys():
        response = _session.get(response.links['next']['url'])
        _alerts.extend(response.json())
    return _alerts


def parse_alerts(_alerts):
    ''' Parse alerts down to just the information we want in the reports '''
    now = datetime.datetime.now()
    # GH format 2021-11-30T17:18:24Z
    now = datetime.datetime.now(datetime.timezone.utc)
    _parsed = []
    for alert in _alerts:
        created = alert.get('created_at')
        created_ts = datetime.datetime.strptime(
            created,
            '%Y-%m-%dT%H:%M:%S%z'
            )
        timedelta = now - created_ts
        repository = alert.get('repository')
        details = {
            'name': repository.get('name'),
            'type': alert.get('secret_type'),
            'discovered': created,
            'timedelta': timedelta
        }
        _parsed.append(details)
    return _parsed


def write_xlsx(_parsed, _org):
    ''' Create dataframe from list of dicts and write to xlsx'''
    today = datetime.date.today()
    _df = pd.DataFrame.from_dict(_parsed)
    _df.set_index('name', inplace=True)
    # _df.to_excel(f'secrets-{_org}-{today}.xlsx')
    _df.to_excel(f'reports/secrets-{_org}-{today}.xlsx')


if __name__ == '__main__':
    ''' Entrypoint '''
    args = parser.parse_args()
    session = requests.Session()
    session.headers.update(config.rest_headers['headers'])
    session.params.update(config.rest_headers['params'])
    alerts = describe_alerts(session, args.org)
    parsed = parse_alerts(alerts)
    write_xlsx(parsed, args.org)
