''' Imports '''
import os
import re
import time
import json
import pprint as pp
import requests
import csv
from config import config
from ratelimit import limits
from datetime import timedelta


@limits(calls=10, period=timedelta(seconds=60).total_seconds())
def get_repositories(_session):
    '''
    Returns a list of dictionaries
    '''
    orgs = [
        'isubscribed', 'anchorfree', 'auracompany',
        'anchorfreepartner', 'figleafteam'
        ]
    base_url = 'https://api.github.com'
    _repos = []
    for org in orgs:
        path = f'/orgs/{org}/repos'
        as_repos_url = f'{base_url}{path}'
        # Get initial response
        response = _session.get(as_repos_url)
        _repos.extend(response.json())
        # Retrieve the next page until we run of out 'next' keys
        while 'next' in response.links.keys():
            response = _session.get(response.links['next']['url'])
            _repos.extend(response.json())
    return _repos


@limits(calls=10, period=timedelta(seconds=60).total_seconds())
def get_admins(_config, _full_name):
    ''' Return list of admins for a repository '''
    # /repos/{owner}/{repo}/collaborators
    collaborators = []
    admins = []
    # List of people to exclude who have org level admin so they don't
    # show up on every single repository we're inspecting
    no_admin_list = [
        'mlavocat-aura', 'rtoohil', 'jbeas408', 'Aura-IT',
        'auraShawn', 'mhelgeson', 'jeffisadams', 'peteigel',
        'taryyorn', 'dpowell-aura', 'Parker-007', 'jr-tietsort',
        'magicgrin'
        ]
    base_url = 'https://api.github.com'
    as_collab_url = f'{base_url}/repos/{_full_name}/collaborators'
    response = requests.get(as_collab_url, headers=_config['h'])
    collaborators.extend(response.json())
    while 'next' in response.links.keys():
        response = requests.get(response.links['next']['url'], headers=_config['h'], params=_config['p'])
        collaborators.extend(response.json())
    for collaborator in collaborators:
        login = collaborator.get('login')
        permissions = collaborator.get('permissions')
        if permissions.get('admin') is True and login not in no_admin_list:
            admins.append(login)

    return admins

@limits(calls=10, period=timedelta(seconds=60).total_seconds())
def get_secrets(_config, _full_name):
    ''' Return count of secrets from given repository '''
    base_url = 'https://api.github.com'
    as_secrets_url = f'{base_url}/repos/{_full_name}/secret-scanning/alerts'
    response = requests.get(as_secrets_url, headers=_config['h'])
    secrets = response.json()

    return len(secrets)

# @limits(calls=10, period=timedelta(seconds=60).total_seconds())
def get_workflows(_session, _full_name):
    '''
    Check for CodeQL workflow
    '''
    regex = re.compile('codeql')
    base_url = 'https://api.github.com'
    as_workflow_url = f'{base_url}/repos/{_full_name}/actions/workflows'
    response = _session.get(as_workflow_url)
    workflows = response.json().get('workflows')
    workflow_names = []
    if len(workflows) > 0:
        for workflow in workflows:
            workflow_names.append(workflow.get('name').lower())
    matches = list(filter(regex.match, workflow_names))

    return True if len(matches) > 0 else False


def parse_repositories(_session, _repos):
    ''' Parse repositories for required content '''
    parsed = []
    for repo in _repos:
        full_name = repo.get('full_name')
        organization, name = full_name.split('/')
        time.sleep(1)
        workflow_status = get_workflows(_session, full_name)
        # Temporarily disabling admins
        # admins = get_admins(_headers, full_name)
        admins = []
        # secrets = get_secrets(_config, full_name)
        secrets = 0
        data = {
            'Name': name,
            'Organization': organization,
            'Admins': ('; ').join(admins),
            'Status': workflow_status,
            'Secrets': secrets
        }
        parsed.append(data)
    return parsed


def write_csv(_parsed):
    ''' Write results from parsed respositories to CSV file '''
    columns = ['Name', 'Organization', 'Admins', 'Status', 'Secrets']
    with open('codeql.csv', 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=columns)
        writer.writeheader()
        for key in _parsed:
            writer.writerow(key)


def describe_rate_limit(_session):
    now = int(time.time())
    base_url = 'https://api.github.com'
    as_ratelimit_url = f'{base_url}/rate_limit'
    response = _session.get(as_ratelimit_url)
    limits = response.json()
    rate = limits.get('rate')
    time_delta = round((rate['reset'] - now)/60)
    print(f'Calls remaining: {rate["remaining"]} | Next reset: {time_delta}m')


if __name__ == '__main__':
    ''' Entrypoint '''
    session = requests.Session()
    session.headers.update(config['h'])
    session.params.update(config['p'])
    describe_rate_limit(session)
    repos = get_repositories(session)
    parsed = parse_repositories(session, repos)
    # describe_rate_limit(config)
    # write_csv(parsed)
