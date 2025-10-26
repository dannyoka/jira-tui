import os
import httpx
import base64
import logging

logger = logging.getLogger(__name__)


class JiraClient:
    def __init__(self, host=None, username=None, api_token=None):
        self.host = host or os.environ["JIRA_HOST"]
        self.username = username or os.environ["JIRA_USERNAME"]
        self.api_token = api_token or os.environ["JIRA_API_TOKEN"]
        self.base_url = "https://qlik-dev.atlassian.net/rest/api/3"

    def get_auth_header(self):
        token = f"{self.username}:{self.api_token}"
        b64_token = base64.b64encode(token.encode()).decode()
        return f"Basic {b64_token}"

    async def fetch_issues(self, jql=None, fields=None):
        url = f"{self.base_url}/search/jql"
        query = {
            "jql": jql
            or f"project = QANS AND assignee = currentUser() AND status != Closed AND status != Resolved",
            "fields": fields or ["summary", "statusCategory"],
        }
        headers = {
            "Authorization": self.get_auth_header(),
            "Accept": "application/json",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, params=query)
            resp.raise_for_status()
            data = resp.json()
            return [
                {
                    "key": issue["key"],
                    "summary": issue["fields"]["summary"],
                    "status": issue["fields"]["statusCategory"]["name"],
                }
                for issue in data["issues"]
            ]

    async def fetch_issue(self, issue_key, fields=None):
        url = f"{self.base_url}/issue/{issue_key}"
        headers = {
            "Authorization": self.get_auth_header(),
            "Accept": "application/json",
        }
        params = {"fields": ",".join(fields or ["summary", "statusCategory"])}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            return {
                "key": data["key"],
                "summary": data["fields"]["summary"],
                "status": data["fields"]["statusCategory"]["name"],
            }

    async def fetch_issue_transitions(self, issue_key: str):
        url = f"https://qlik-dev.atlassian.net/rest/api/3/issue/{issue_key}/transitions"
        headers = {
            "Authorization": self.get_auth_header(),
            "Accept": "application/json",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            transitions = data.get("transitions", [])
            return [
                {"name": transition["name"], "id": transition["id"]}
                for transition in transitions
            ]

    async def transition_issue(self, issue_key: str, transition_id: str):
        url = f"{self.base_url}/issue/{issue_key}/transitions"
        headers = {
            "Authorization": self.get_auth_header(),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        payload = {"transition": {"id": transition_id}}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()

    async def fetch_issue_comments(self, issue_key: str):
        url = f"{self.base_url}/issue/{issue_key}/comment"
        headers = {
            "Authorization": self.get_auth_header(),
            "Accept": "application/json",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data.get("comments", [])

    async def add_issue_comment(self, issue_key: str, comment: str):
        url = f"{self.base_url}/issue/{issue_key}/comment"
        headers = {
            "Authorization": self.get_auth_header(),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        payload = {"body": comment}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()
