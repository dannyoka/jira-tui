from textual.app import ComposeResult
from textual.widgets import Static
from textual.screen import Screen
from textual.reactive import reactive
from .IssueView import IssueView

import logging

logger = logging.getLogger(__name__)


class Dashboard(Screen):
    selected = reactive(0)
    issues = reactive([])

    async def on_mount(self):
        self.issues = await self.app.jira_client.fetch_issues()
        await self.recompose()

    def compose(self) -> ComposeResult:
        yield Static("Dashboard: Issues assigned to you\n", id="header")
        for idx, issue in enumerate(self.issues):
            prefix = "➤ " if idx == self.selected else "  "
            yield Static(
                f"{prefix}{issue['key']}: {issue['summary']}", id=f"issue-{idx}"
            )

    def on_key(self, event):
        if event.key == "j":
            self.selected = min(self.selected + 1, len(self.issues) - 1)
            self.refresh()
        elif event.key == "k":
            self.selected = max(self.selected - 1, 0)
            self.refresh()
        elif event.key == "space":
            self.app.push_screen(IssueView(self.issues[self.selected]))
        elif event.key == "q":
            self.app.exit()

    async def watch_selected(self, old, new):
        await self.recompose()
        self.refresh()
