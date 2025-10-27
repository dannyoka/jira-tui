from textual.app import ComposeResult
from textual import events
from textual.widgets import Static, Label, ListItem, ListView
from textual.screen import Screen
from textual.reactive import reactive
from textual.containers import VerticalScroll, Horizontal
from .IssueView import IssueView
from .IssueDetail import IssueDetail
from .IssueList import IssueList

import logging

logger = logging.getLogger(__name__)


class Dashboard(Screen):
    selected = reactive(0)
    issues = reactive([])

    def __init__(self):
        super().__init__()
        self.issue_detail = Static("loading")
        self.issue_list = Static("loading")
        self.focus_left = True

    async def on_mount(self):
        self.issues = await self.app.jira_client.fetch_issues()
        self.issue_list = IssueList(self.issues, self.on_issue_selected)
        self.issue_detail = IssueDetail()
        await self.recompose()

    def compose(self) -> ComposeResult:
        yield Static("Dashboard: Issues assigned to you\n", id="header")
        for idx, issue in enumerate(self.issues):
            prefix = "➤ " if idx == self.selected else "  "
            yield Static(
                f"{prefix}{issue['key']}: {issue['summary']}", id=f"issue-{idx}"
            )

    async def on_key(self, event):
        if event.key == "j":
            self.selected = min(self.selected + 1, len(self.issues) - 1)
            self.refresh()
        elif event.key == "k":
            self.selected = max(self.selected - 1, 0)
            self.refresh()
        elif event.key == "enter":
            self.app.push_screen(IssueView(self.issues[self.selected]))
        elif event.key == "q":
            self.app.exit()
        elif event.key == "r":
            self.issues = await self.app.jira_client.fetch_issues()
            self.selected = 0
            self.app.refresh()

    def on_issue_selected(self, issue):
        self.issue_detail.update_issue(issue)

    async def watch_selected(self, old, new):
        await self.recompose()
        self.refresh()
