# GHAST - GitHub Advanced Security Tools

## Setup

Create virtualenv

``` virtualenv -p python3 venv/ ```

Activate virtualenv

``` source venv/bin/activate ```

Install dependencies

``` pip install -r requirements.txt ```


---
### codeql-report
Creates a CSV report of all repositories including their admins, CodeQL workflow status, and secret count.

Usage:

``` python codeql-report.py ```

---

### circle-users
Prints a list of all users for an organization, in this case meetcircle.  Change the path variable to query a different org.

Usage:

``` python circle-users.py ```

---
