import os
import json
import httpx
import base64
import logging

logger = logging.getLogger(__name__)


class JiraClient:
    def __init__(self, host=None, username=None, api_token=None):
        self.username = username or os.environ["JIRA_USERNAME"]
        self.api_token = api_token or os.environ["JIRA_API_TOKEN"]
        self.base_url = f"{host or os.environ['JIRA_HOST']}/rest/api/3"
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
            or "(assignee = currentUser() OR reporter = currentUser()) AND status != Closed AND status != Resolved AND status != Done",
            "fields": fields
            or ["summary", "statusCategory", "description", "assignee", "reporter"],
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
                    "description": issue["fields"]["description"],
                    "assignee": (issue["fields"].get("assignee") or {}).get(
                        "displayName", "Unassigned"
                    ),
                    "reporter": issue["fields"]["reporter"]["displayName"],
                }
                for issue in data["issues"]
            ]

    async def fetch_issue(self, issue_key, fields=None):
        url = f"{self.base_url}/issue/{issue_key}"
        headers = {
            "Authorization": self.get_auth_header(),
            "Accept": "application/json",
        }
        params = {
            "fields": ",".join(
                fields
                or ["summary", "statusCategory", "description", "assignee", "reporter"]
            )
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            created = resp.json()
            return {
                "key": created["key"],
                "summary": created["fields"]["summary"],
                "status": created["fields"]["statusCategory"]["name"],
                "statusId": created["fields"]["statusCategory"]["id"],
                "description": created["fields"]["description"],
                "assignee": (created["fields"].get("assignee") or {}).get(
                    "displayName", "Unassigned"
                ),
                "reporter": created["fields"]["reporter"]["displayName"],
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

    async def fetch_projects(self):
        url = f"{self.base_url}/project"
        headers = {
            "Authorization": self.get_auth_header(),
            "Accept": "application/json",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def fetch_project_by_key(self, projectKey):
        url = f"{self.base_url}/project/{projectKey}"
        headers = {
            "Authorization": self.get_auth_header(),
            "Accept": "application/json",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def fetch_boards(self):
        url = f"{self.base_url.replace('/rest/api/3', '/rest/agile/1.0')}/board"
        headers = {
            "Authorization": self.get_auth_header(),
            "Accept": "application/json",
        }
        params = {"projectKeyOrId": "QANS"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            return resp.json()

    async def fetch_sprints(self, board_id):
        url = f"{self.base_url.replace('/rest/api/3', '/rest/agile/1.0')}/board/{board_id}/sprint"
        headers = {
            "Authorization": self.get_auth_header(),
            "Accept": "application/json",
        }
        params = {"state": "active"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            return resp.json()

    async def fetch_assignable_users(self, project_key, query):
        url = f"{self.base_url}/user/assignable/search"
        headers = {
            "Authorization": self.get_auth_header(),
            "Accept": "application/json",
        }
        params = {"project": project_key, "maxResults": 100, "query": query}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, params=params)
            logger.info(f"users are: {json.dumps(resp.json())}")
            resp.raise_for_status()
            return resp.json()

    async def fetch_issue_createmeta(self, project_key, issuetype_name="Story"):
        url = f"{self.base_url}/issue/createmeta"
        headers = {
            "Authorization": self.get_auth_header(),
            "Accept": "application/json",
        }
        params = {
            "projectKeys": project_key,
            "issuetypeNames": issuetype_name,
            "expand": "projects.issuetypes.fields",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            return resp.json()

    async def fetch_current_user(self):
        url = f"{self.base_url}/myself"
        headers = {
            "Authorization": self.get_auth_header(),
            "Accept": "application/json",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def create_issue(
        self,
        summary: str,
        description: dict,
        project_id: str = "",
        assignee_id: str = "",
        story_points: int = 1,
        sprint_id: str = "",
        issuetype: str = "Task",
        reporter: str = "",
    ):
        # my id 61d4db88a54af90069717fa2
        url = f"{self.base_url}/issue"
        headers = {
            "Authorization": self.get_auth_header(),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        fields = {
            "project": {"id": project_id},
            "summary": summary,
            # "description": description,
            "issuetype": {"name": issuetype},
            "reporter": {"id": reporter},
        }
        if assignee_id:
            fields["assignee"] = {"id": assignee_id}
            # if story_points is not None:
            fields["customfield_10034"] = (
                story_points  # Replace with your actual story points field ID
            )
        if sprint_id:
            fields["customfield_10020"] = sprint_id
        payload = {"fields": fields}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload)
            logger.info("response is" + json.dumps(resp.json(), indent=4))
            resp.raise_for_status()
            new_issue = resp.json()
            return new_issue

    async def assign_issue(self, issue_key: str, account_id: str):
        url = f"{self.base_url}/issue/{issue_key}/assignee"
        headers = {
            "Authorization": self.get_auth_header(),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        payload = {"accountId": account_id}
        async with httpx.AsyncClient() as client:
            resp = await client.put(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.status_code == 204  # Returns True if assignment was successful
