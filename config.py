import os

try:
    token = os.getenv('GITHUB_TOKEN')
except KeyError:
    print('Did you forget to export GITHUB_TOKEN?')

config = {
    'h': {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': 'token ' + token
    },
    'p': {'per_page': 100},
    'b': 'https://api.github.com'
}