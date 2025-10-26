from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Static
import logging

logger = logging.getLogger(__name__)


class IssueView(Screen):
    async def on_mount(self):
        self.transitions = self.app.jira_client.fetch_issue_transitions(
            self.issue["key"]
        )
        logger.info(self.transitions)

    def __init__(self, issue):
        super().__init__()
        self.issue = issue

    def compose(self) -> ComposeResult:
        yield Static(
            f"Issue: {self.issue['key']}\nSummary: {self.issue['summary']}\n\nPress h to go back.",
            id="issue-detail",
        )

    def on_key(self, event):
        if event.key == "h":
            self.app.pop_screen()
