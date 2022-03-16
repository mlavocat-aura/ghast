# GHAST - GitHub Advanced Security Tools

## Prerequisits

GitHub developer token with appropriate permissions (mostly READ on repositories)

``` export GITHUB_TOKEN='{personal access token}' ```

## Setup

Create virtualenv

``` virtualenv -p python3 venv/ ```

Activate virtualenv

``` source venv/bin/activate ```

Install dependencies

``` pip install -r requirements.txt ```


---
### codeql-usage
Creates a CSV report of all repositories including their admins, CodeQL workflow status, and secret count.  This requires a ton of API calls to gather everything, so anything not explicitly needed should be commented out.

Usage:

``` python codeql-report.py --org isubscribed```

---
### secret-scanning
Creates a XLSX report of all secret alerts currently active for the target org.

Usage:

``` python secret-scanning.py --org isubscribed ```

---
### codeql-alerts
Generates an XLSX file containing code-scanning alerts for all orgs.  

``` python codeql-alerts.py ```

---

### circle-users
Prints a list of all users for an organization, in this case meetcircle.  Change the path variable to query a different org.

Usage:

``` python circle-users.py ```

---