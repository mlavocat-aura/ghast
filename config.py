import os

try:
    token = os.getenv('GITHUB_TOKEN')
except KeyError:
    print('Did you forget to export GITHUB_TOKEN?')

req_conf = {
    'headers': {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': 'token ' + token
    },
    'params': {'per_page': 100}
}

admin_exclusions = [
    'mlavocat-aura', 'rtoohil', 'jbeas408', 'Aura-IT',
    'auraShawn', 'mhelgeson', 'jeffisadams', 'peteigel',
    'taryyorn', 'dpowell-aura', 'Parker-007', 'jr-tietsort',
    'magicgrin'
    ]

base_url = 'https://api.github.com'