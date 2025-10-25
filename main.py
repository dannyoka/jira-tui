from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.screen import Screen
from textual.widget import Widget
from textual.reactive import reactive
from internal.api.issues import fetch_issues
import logging

logging.basicConfig(filename="app.log", level=logging.DEBUG)
logger = logging.getLogger(__name__)
# Mock issues data
# ISSUES = [
#     {"key": "JIRA-1", "summary": "Fix login bug"},
#     {"key": "JIRA-2", "summary": "Update documentation"},
#     {"key": "JIRA-3", "summary": "Refactor API endpoints"},
# ]


class Dashboard(Screen):
    selected = reactive(0)
    issues = reactive([])

    async def on_mount(self):
        self.issues = await fetch_issues()
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
        elif event.key == "l":
            self.app.push_screen(IssueView(self.issues[self.selected]))
        elif event.key == "q":
            self.app.exit()

    async def watch_selected(self, old, new):
        logger.debug("updating")
        await self.recompose()
        self.refresh()


class IssueView(Screen):
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


class JiraTUI(App):
    def on_mount(self):
        self.push_screen(Dashboard())


if __name__ == "__main__":
    JiraTUI().run()
