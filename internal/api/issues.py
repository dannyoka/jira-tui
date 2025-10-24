import os
import httpx

JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]
JIRA_USERNAME = os.environ["JIRA_USERNAME"]
JIRA_HOST = os.environ["JIRA_HOST"]


async def fetch_issues():
    url = f"https://{JIRA_HOST}/rest/api/3/search"
    jql = (
        f"assignee = {JIRA_USERNAME} AND resolution = Unresolved ORDER BY updated DESC"
    )
    headers = {
        "Authorization": f"Basic {httpx.auth._basic_auth_str(JIRA_USERNAME, JIRA_API_TOKEN)}",
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
