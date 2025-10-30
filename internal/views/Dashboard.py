import json
from internal.modals.CreateIssueModal import MyModal
from textual.app import ComposeResult
from textual.widgets import Footer, Static
from textual.screen import Screen
from textual.reactive import reactive
from textual.containers import Horizontal, Container, Vertical

from .IssueDetail import IssueDetail
from .IssueList import IssueList

import logging

logger = logging.getLogger(__name__)


class Dashboard(Screen):
    selected = reactive(0)
    issues = reactive([])
    focused_element = reactive("list")

    def __init__(self):
        super().__init__()
        self.issue_list = IssueList(self.on_select_callback, self.on_enter_issue)
        self.issue_detail = IssueDetail(None, self.on_exit_issue)

    async def on_mount(self):
        self.issues = await self.app.jira_client.fetch_issues()
        self.issue_list.issues_list = self.issues
        self.issue_list.focus()
        await self.issue_list.recompose()

    def compose(self) -> ComposeResult:
        issue_list_classes = "issue-list-container"
        issue_detail_classes = "issue-detail-container"
        if self.focused_element == "list":
            issue_list_classes += " focused"
        elif self.focused_element == "detail":
            issue_detail_classes += " focused"
        yield Horizontal(
            Vertical(
                Static("Issues List"),
                Container(
                    self.issue_list,
                ),
                classes=issue_list_classes,
            ),
            Vertical(
                Static("Issues Detail"),
                Container(self.issue_detail),
                classes=issue_detail_classes,
            ),
        )
        yield Footer()

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

    async def watch_focused_element(self, old, new):
        await self.recompose()
        self.refresh()
        if new == "detail":
            self.issue_list.blur()
            self.issue_detail.focus()
        else:
            self.issue_detail.blur()
            self.issue_list.focus()

    def on_enter_issue(self):
        self.focused_element = "detail"

    def on_exit_issue(self):
        self.focused_element = "list"
