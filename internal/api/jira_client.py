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
        self._comments_cache = {}
        self._transitions_cache = {}

    def get_auth_header(self):
        token = f"{self.username}:{self.api_token}"
        b64_token = base64.b64encode(token.encode()).decode()
        return f"Basic {b64_token}"

    async def fetch_issues(self, jql=None, fields=None):
        url = f"{self.base_url}/search/jql"
        query = {
            "jql": jql
            or f"assignee = currentUser() AND status != Closed AND status != Resolved AND status != Done",
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
                    "statusId": issue["fields"]["statusCategory"]["id"],
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
        if issue_key in self._transitions_cache:
            return self._transitions_cache[issue_key]
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
            response = [
                {"name": transition["name"], "id": transition["id"]}
                for transition in transitions
            ]
            self._transitions_cache[issue_key] = response
            return response

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
            if resp.status_code == 204:
                # clear the cache, because once the issue gets transitioned,
                # it might have a totally different set of new ones.
                self._transitions_cache[issue_key] = []
                return True  # Success, no content
            return resp.json()  # For other status codes with content

    async def fetch_issue_comments(self, issue_key: str):
        if issue_key in self._comments_cache:
            return self._comments_cache[issue_key]
        url = f"{self.base_url}/issue/{issue_key}/comment"
        headers = {
            "Authorization": self.get_auth_header(),
            "Accept": "application/json",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            response = data.get("comments", [])
            self._comments_cache[issue_key] = response
            return data.get("comments", [])

    async def add_issue_comment(self, issue_key: str, comment: str):
        url = f"{self.base_url}/issue/{issue_key}/comment"
        headers = {
            "Authorization": self.get_auth_header(),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        payload = {
            "body": {
                "content": [
                    {
                        "content": [{"text": f"{comment}", "type": "text"}],
                        "type": "paragraph",
                    }
                ],
                "type": "doc",
                "version": 1,
            },
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            new_comment = resp.json()
            self._comments_cache[issue_key].append(new_comment)
            return new_comment
