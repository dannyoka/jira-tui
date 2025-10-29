from textual.screen import Screen
from textual.reactive import reactive
from textual.app import ComposeResult
from ..components.TransitionSelector import TransitionSelector


class TransitionScreen(Screen):
    issue_key = reactive("")

    def __init__(self, issue_key):
        super().__init__()
        self.issue_key = issue_key
        self.transitions = []

    async def on_mount(self):
        if self.issue_key:
            self.transitions = await self.app.jira_client.fetch_issue_transitions(
                self.issue_key
            )

    def compose(self) -> ComposeResult:
        yield TransitionSelector(self.transitions, self.issue_key, self.app.jira_client)

    def on_key(self, event):
        if event.key == "q":
            self.app.pop_screen()

    async def watch_issue_key(self, old, new):
        self.transitions = await self.app.jira_client.fetch_issue_transitions(
            self.issue_key
        )
        await self.recompose()
        self.refresh()
