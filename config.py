import os

try:
    token = os.getenv('GITHUB_TOKEN')
except KeyError:
    print('Did you forget to export GITHUB_TOKEN?')

rest_headers = {
    'headers': {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': 'token ' + token
    },
    'params': {'per_page': 50}
}

graphql_headers = {'Authorization': f'bearer {token}'}

admin_exclusions = [
    'mlavocat-aura', 'rtoohil', 'jbeas408', 'Aura-IT',
    'auraShawn', 'mhelgeson', 'jeffisadams', 'peteigel',
    'taryyorn', 'dpowell-aura', 'Parker-007', 'jr-tietsort',
    'magicgrin'
    ]

base_url = 'https://api.github.com'
graphql_base_url = 'https://api.github.com/graphql'

orgs = [
    'auracompany', 'isubscribed', 'anchorfree',
    'anchorfreepartner', 'figleafteam', 'meetcircle'
    ]

query = """
query($organization:String!, $previousEndCursor:String)
{
  organization(login: $organization) {
    repositories(first: 100, after: $previousEndCursor) {
      pageInfo {
        hasNextPage
        endCursor
        startCursor
      }
      nodes {
        nameWithOwner
        vulnerabilityAlerts(first: 10) {
          nodes {
            state
            createdAt
            securityVulnerability {
              package {
                name
              }
            }
            securityAdvisory {
              severity
            }
          }
        }
      }
    }
  }
}
"""
