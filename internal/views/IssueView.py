from internal.views.TransitionScreen import TransitionScreen
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Static
from textual.reactive import reactive
import logging

logger = logging.getLogger(__name__)


class IssueView(Screen):
    comments = reactive([])
    transitions = reactive([])

    async def on_mount(self):
        issue_key = self.issue["key"]
        self.transitions = await self.app.jira_client.fetch_issue_transitions(issue_key)
        self.comments = await self.app.jira_client.fetch_issue_comments(issue_key)
        await self.recompose()

    def __init__(self, issue):
        super().__init__()
        self.issue = issue

    def compose(self) -> ComposeResult:
        yield Static(
            f"Issue: {self.issue['key']}\nSummary: {self.issue['summary']}\n\nPress h to go back.",
            id="issue-detail",
        )
        for idx, comment in enumerate(self.comments):
            yield Static(
                f"{comment['body']['content'][0]['content'][0]['text']}\nAuthor: {comment['author']['displayName']}",
                id=f"comment-{idx}",
            )
        for transitionIdx, transition in enumerate(self.transitions):
            yield Static(f"{transition}", id=f"transition-{transitionIdx}")

    def on_key(self, event):
        if event.key == "q":
            self.app.pop_screen()
        if event.key == "t":
            self.app.push_screen(
                TransitionScreen(
                    self.transitions, self.issue["key"], self.app.jira_client
                )
            )
