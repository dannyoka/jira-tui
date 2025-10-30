import json
from .config.config import config_data
from internal.api.jira_client import JiraClient
from textual.app import App
from internal.views.Dashboard import Dashboard
from internal.modals.CreateIssueModal import MyModal
import logging

logger = logging.getLogger(__name__)


class JiraTUI(App):
    CSS_PATH = "styles.tcss"

    def __init__(self):
        super().__init__()
        self.dashboard = Dashboard()

    async def on_mount(self):
        self.push_screen(self.dashboard)
        self.jira_client = JiraClient()
        self.projects = []
        self.sprints = await self.jira_client.fetch_sprints(
            config_data.get("sprintBoard")
        )
        self.current_user = await self.jira_client.fetch_current_user()

    def on_key(self, event):
        if event.key == "c":
            self.push_screen(
                MyModal(
                    default_project_id=config_data.get("projectId"),
                    sprints=self.sprints,
                    on_submit=self.on_submit_new_issue,
                    current_user=self.current_user,
                )
            )

    async def on_submit_new_issue(self, payload: dict):
        created = await self.jira_client.create_issue(
            summary=payload.get("summary", ""),
            description=payload.get("description", {}),
            project_id=payload.get("project_id", ""),
            assignee_id=payload.get("assignee", ""),
            story_points=payload.get("story_points", 1),
            reporter=payload.get("reporter", ""),
            sprint_id=payload.get("sprint_id", ""),
        )
        new_issue = await self.jira_client.fetch_issue(created["key"])
        self.dashboard.issues.append(new_issue)
        await self.dashboard.issue_list.recompose()
        self.pop_screen()
