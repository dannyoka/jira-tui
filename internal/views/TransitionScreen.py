from textual.screen import Screen
from textual.app import ComposeResult
from ..components.TransitionSelector import TransitionSelector


class TransitionScreen(Screen):
    def __init__(self, transitions, issue_key, jira_client):
        super().__init__()
        self.transitions = transitions
        self.issue_key = issue_key
        self.jira_client = jira_client

    def compose(self) -> ComposeResult:
        yield TransitionSelector(self.transitions, self.issue_key, self.jira_client)

    def on_key(self, event):
        if event.key == "q":
            self.app.pop_screen()
