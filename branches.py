''' Imports '''
import pprint as pp
import datetime
import time
import argparse
import pandas as pd
import requests
import config


# Argparse Setup
parser = argparse.ArgumentParser()
parser.add_argument(
    '-o', '--org',
    help='Target organization')


def get_repositories(_session, _org):
    '''
    Returns a list of dictionaries of all repositories
    '''
    _repos = []
    path = f'/orgs/{_org}/repos'
    as_repos_url = f'{config.base_url}{path}'
    # Get initial response
    response = _session.get(as_repos_url)
    _repos.extend(response.json())
    # Retrieve the next page until we run of out 'next' keys
    while 'next' in response.links.keys():
        response = _session.get(response.links['next']['url'])
        _repos.extend(response.json())
    return _repos


def get_branch_protection(_session, _repos):
    ''' Inserts branch protection information into repos dict '''
    # /repos/{owner}/{repo}/branches/{branch}/protection
    for repo in _repos:
        name = repo.get('full_name')
        default = repo.get('default_branch', 'master')
        path = f'/repos/{name}/branches/{default}/protection'
        as_branch_url = f'{config.base_url}{path}'
        response = _session.get(as_branch_url)
        repo['branch_protection'] = response.json()
    return _repos


def parse_repositories(_repos):
    ''' Parse full responses down to a single dict of the data we need '''
    result_list = []
    for repo in _repos:
        settings = repo.get('branch_protection')
        default = repo.get('default_branch', 'master')
        name = repo.get('name')
        html_url = repo.get('html_url')
        hyperlink = make_hyperlink(html_url, name)

        if 'message' in settings:
            message = settings['message']
            results = {
                'repository': hyperlink,
                'default_branch': default,
                'allow_deletions': message,
                'allow_force_pushes': message,
                'block_creations': message,
                'enforce_admins': message,
                'required_pull_request_reviews': '0'
            }
        else:
            reviewers = '0' if 'required_pull_request_reviews' not in settings else settings['required_pull_request_reviews']['required_approving_review_count']
            results = {
                'repository': hyperlink,
                'default_branch': default,
                'allow_deletions': settings['allow_deletions']['enabled'],
                'allow_force_pushes': settings['allow_force_pushes']['enabled'],
                'block_creations': settings['block_creations']['enabled'],
                'enforce_admins': settings['enforce_admins']['enabled'],
                'required_pull_request_reviews': reviewers
            }
        result_list.append(results)
    return result_list


def write_xlsx(_parsed, _org):
    ''' Write data to excel spreadsheet '''
    today = datetime.date.today()
    _df = pd.DataFrame.from_dict(_parsed)
    _df.set_index('repository', inplace=True)
    _df.to_excel(f'reports/branches-{_org}-{today}.xlsx')


def make_hyperlink(_name, _url):
    ''' Returns Excel formatted hyperlink '''
    return f'=HYPERLINK("{_name}", "{_url}")'


def describe_rate_limit(_session):
    ''' Print # calls remaining and time until next reset '''
    ''' API is limited to 5,000 calls per hour '''
    now = int(time.time())
    as_ratelimit_url = f'{config.base_url}/rate_limit'
    response = _session.get(as_ratelimit_url)
    _limits = response.json()
    rate = _limits.get('rate')
    time_delta = round((rate['reset'] - now)/60)
    print(f'Calls remaining: {rate["remaining"]} | Next reset: {time_delta}m')


if __name__ == '__main__':
    ''' Main '''
    args = parser.parse_args()
    session = requests.Session()
    session.headers.update(config.rest_headers['headers'])
    session.params.update(config.rest_headers['params'])
    describe_rate_limit(session)
    repos = get_repositories(session, args.org)
    repos = get_branch_protection(session, repos)
    parsed = parse_repositories(repos)
    write_xlsx(parsed, args.org)
