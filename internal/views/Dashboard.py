import json
from textual.app import ComposeResult
from textual.screen import Screen
from textual.reactive import reactive
from textual.containers import Horizontal, Container

from .IssueDetail import IssueDetail
from .IssueList import IssueList

import logging

logger = logging.getLogger(__name__)


class Dashboard(Screen):
    selected = reactive(0)
    issues = reactive([])

    def __init__(self):
        super().__init__()
        self.issue_list = IssueList(self.on_select_callback, self.on_enter_issue)
        self.issue_detail = IssueDetail(None, self.on_exit_issue)

    async def on_mount(self):
        self.issues = await self.app.jira_client.fetch_issues()
        logger.info(json.dumps(self.issues, indent=4))
        self.issue_list.issues_list = self.issues
        self.issue_list.focus()
        await self.recompose()

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Container(self.issue_list, classes="issue-list-container"),
            Container(self.issue_detail, classes="issue-detail-container"),
        )

    async def on_key(self, event):
        if self.issue_list.has_focus:
            return
        elif event.key == "r":
            self.issues = await self.app.jira_client.fetch_issues()
            self.selected = 0
            self.app.refresh()

    async def watch_selected(self, old, new):
        await self.recompose()
        self.refresh()

    def on_select_callback(self, issue):
        self.issue_detail.issue = issue
        self.issue_detail.refresh()

    def on_enter_issue(self):
        self.issue_list.blur()
        self.issue_detail.focus()

    def on_exit_issue(self):
        self.issue_detail.blur()
        self.issue_list.focus()
