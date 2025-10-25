import os
import httpx
import base64

JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]
JIRA_USERNAME = os.environ["JIRA_USERNAME"]
JIRA_HOST = os.environ["JIRA_HOST"]


def get_jira_auth_header(username, api_token):
    token = f"{username}:{api_token}"
    b64_token = base64.b64encode(token.encode()).decode()
    return f"Basic {b64_token}"


async def fetch_issues():
    url = "https://qlik-dev.atlassian.net/rest/api/3/search"
    jql = (
        f"assignee = {JIRA_USERNAME} AND resolution = Unresolved ORDER BY updated DESC"
    )
    headers = {
        "Authorization": get_jira_auth_header(JIRA_USERNAME, JIRA_API_TOKEN),
        "Accept": "application/json",
    }
    params = {"jql": jql, "fields": "key,summary"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        return [
            {"key": issue["key"], "summary": issue["fields"]["summary"]}
            for issue in data["issues"]
        ]
