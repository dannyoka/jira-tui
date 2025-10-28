from textual.app import ComposeResult
from textual import events
from textual.widgets import Static, Label, ListItem, ListView
from textual.widget import Widget
from textual.screen import Screen
from textual.reactive import reactive
from textual.containers import VerticalScroll, HorizontalScroll
from .IssueView import IssueView

# from .IssueDetail import IssueDetail
# from .IssueList import IssueList

import logging

logger = logging.getLogger(__name__)


class IssueList(Widget):
    issues_list = reactive([])
    selected = reactive(0)
    can_focus = True

    def __init__(self, on_select_callback):
        super().__init__()
        self.on_select = on_select_callback

    def on_mount(self):
        self.focus()

    def compose(self):
        if not len(self.issues_list):
            yield Static("No issues yet")
        for idx, issue in enumerate(self.issues_list):
            prefix = "->" if idx == self.selected else ""
            yield Static(f"{prefix}{issue['key']}: {issue['summary']}")

    def on_key(self, event):
        if event.key == "j":
            self.selected = min(self.selected + 1, len(self.issues_list) - 1)
            self.on_select(self.issues_list[self.selected])
            self.refresh()
        elif event.key == "k":
            self.selected = max(self.selected - 1, 0)
            self.on_select(self.issues_list[self.selected])
            self.refresh()
        elif event.key == "q":
            self.blur()

    async def watch_selected(self, old, new):
        await self.recompose()
        self.refresh()


class IssueDetail(Widget):
    issue = reactive(None)

    def __init__(self, issue: dict | None):
        super().__init__()
        self.issue = issue

    def compose(self):
        if not self.issue:
            yield Static("No issue selected")
        else:
            yield Static(self.issue["key"], classes="half")

    async def watch_issue(self, old, new):
        await self.recompose()
        self.refresh()

    def on_key(self, event):
        if event.key == "q":
            self.blur()


class Dashboard(Screen):
    selected = reactive(0)
    issues = reactive([])

    def __init__(self):
        super().__init__()
        self.issue_list = IssueList(self.on_select_callback)
        self.issue_detail = IssueDetail(None)

    async def on_mount(self):
        self.issues = await self.app.jira_client.fetch_issues()
        self.issue_list.issues_list = self.issues
        self.issue_list.focus()
        await self.recompose()

    def compose(self) -> ComposeResult:
        yield HorizontalScroll(self.issue_list, self.issue_detail)

    async def on_key(self, event):
        if self.issue_list.has_focus:
            return
        elif event.key == "enter":
            self.app.push_screen(IssueView(self.issues[self.selected]))
        elif event.key == "q":
            self.app.exit()
        elif event.key == "r":
            self.issues = await self.app.jira_client.fetch_issues()
            self.selected = 0
            self.app.refresh()
        elif event.key == "l":
            self.issue_detail.focus()
        elif event.key == "h":
            self.issue_list.focus()

    async def watch_selected(self, old, new):
        await self.recompose()
        self.refresh()

    def on_select_callback(self, issue):
        self.issue_detail.issue = issue
        self.issue_detail.refresh()
