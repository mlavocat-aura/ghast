
# An example to get the remaining rate limit using the Github GraphQL API.
import pprint as pp
import requests
import json
import config
import shared
import pandas as pd
import argparse
import datetime
import time

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


def parse_results(_results):
    parsed = []
    # now = datetime.datetime.now(datetime.timezone.utc)
    for result in _results:
        organization, name = result.get('nameWithOwner').split('/')
        alerts = result['vulnerabilityAlerts']['nodes']
        if len(alerts) > 0:
            for alert in alerts:
                number = alert.get('number')
                state = alert.get('state')
                created = alert.get('createdAt')
                created_ts = datetime.datetime.strptime(
                    created,
                    '%Y-%m-%dT%H:%M:%S%z'
                    )
                _details = {
                    'id': f'{name}:{number}',
                    'organization': organization,
                    'state': state,
                    'package': alert['securityVulnerability']['package']['name'],
                    'severity': alert['securityAdvisory']['severity'],
                    'created': created_ts.date(),
                    'updated': time.time()
                }
                parsed.append(_details)
    return parsed


def insert_records(_parsed):
    cnx = shared.connect_to_rds()
    cursor = cnx.cursor(prepared=True)
    query = ('INSERT INTO ghast.gh_dependabot \
        (id, organization, state, package, severity, created, updated) \
        VALUES (%s, %s, %s, %s, %s, %s, %s) \
        ON DUPLICATE KEY UPDATE \
            state = VALUES(state), \
            updated = VALUES(updated)'
    )
    for record in _parsed:
        cursor.execute(query, tuple(record.values()))
    cnx.commit()


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
    insert_records(parsed)


if __name__ == '__main__':
    main()
