
# An example to get the remaining rate limit using the Github GraphQL API.
import pprint as pp
import requests
import json
import config
import pandas as pd
import argparse
import datetime

# Argparse Setup
parser = argparse.ArgumentParser()
parser.add_argument(
    '-o', '--org',
    help='Target organization')


def run_query(_org, _cursor=None):
    query = config.query
    if _cursor is not None:
        variables = {"organization": _org, "previousEndCursor": _cursor}
    else:
        variables = {"organization": _org}
    request = requests.post(
        config.graphql_base_url,
        json={"query": query, "variables": variables},
        headers=config.graphql_headers
        )
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, config.query)) 


def write_xlsx(_results, _org):
    ''' Write data to excel spreadsheet '''
    today = datetime.date.today()
    _df = pd.DataFrame.from_dict(_results)
    _df.set_index('name', inplace=True)
    _df.to_excel(f'reports/dependabot-{_org}-{today}.xlsx')


def parse_results(_results):
    parsed = []
    now = datetime.datetime.now(datetime.timezone.utc)
    for result in _results:
        name = result.get('nameWithOwner')
        alerts = result['vulnerabilityAlerts']['nodes']
        if len(alerts) > 0:
            for alert in alerts:
                state = alert.get('state')
                if state == 'OPEN':
                    created = alert.get('createdAt')
                    created_ts = datetime.datetime.strptime(
                        created,
                        '%Y-%m-%dT%H:%M:%S%z'
                        )
                    timedelta = now - created_ts
                    _details = {
                        'name': name,
                        'created_at': alert.get('createdAt'),
                        'time_open': timedelta,
                        'state': alert.get('state'),
                        'package': alert['securityVulnerability']['package']['name'],
                        'severity': alert['securityAdvisory']['severity']
                    }
                    parsed.append(_details)
    return parsed


def main():
    args = parser.parse_args()
    resp = run_query(args.org)
    results = resp['data']['organization']['repositories']['nodes']
    has_next_page = resp['data']['organization']['repositories']['pageInfo']['hasNextPage']
    end_cursor = resp['data']['organization']['repositories']['pageInfo']['endCursor']
    while has_next_page:
        resp = run_query(args.org, end_cursor)
        end_cursor = resp['data']['organization']['repositories']['pageInfo']['endCursor']
        has_next_page = resp['data']['organization']['repositories']['pageInfo']['hasNextPage']
        results = results + resp['data']['organization']['repositories']['nodes']
    parsed = parse_results(results)
    write_xlsx(parsed, args.org)


if __name__ == '__main__':
    main()