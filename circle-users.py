# Print a list of all members for an org
''' Imports'''
import os
import pprint as pp
import requests


def main(_token):
    ''' Main function. Uses # <https://api.github.com/orgs/:org/members>; '''
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': 'token ' + token
        }
    base_url = 'https://api.github.com'
    path = '/orgs/meetcircle/members'
    as_members_url = f'{base_url}{path}'
    members = []
    response = requests.get(as_members_url, headers=headers)
    members.extend(response.json())
    while 'next' in response.links.keys():
        response = requests.get(response.links['next']['url'], headers=headers)
        members.extend(response.json())

    print('meetcircle has ' + str(len(members)) + ' members')
    for member in members:
        pp.pprint(member.get('login'))


if __name__ == '__main__':
    ''' Entrypoint '''
    token = os.getenv('GITHUB_TOKEN')
    main(token)
