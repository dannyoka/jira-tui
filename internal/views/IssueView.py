from internal.components.CommentInput import CommentInput
from internal.views.TransitionScreen import TransitionScreen
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Static
from textual.reactive import reactive
import logging
import json

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
        super().__init__(id="issue_view")
        self.issue = issue

    def compose(self) -> ComposeResult:
        yield Static(
            f"Issue: {self.issue['key']}\nStatus: {self.issue['status']}\nSummary: {self.issue['summary']}\n\nPress q to go back.",
            id="issue-detail",
        )
        for idx, comment in enumerate(self.comments):
            yield Static(
                f"{json.dumps(comment, indent=4)}",
                id=f"comment-{idx}",
                # f"{comment['body']['content'][0]['content'][0]['text']}\nAuthor: {comment['author']['displayName']}",
                # id=f"comment-{idx}",
            )

    def on_key(self, event):
        if event.key == "q":
            self.app.pop_screen()
        if event.key == "t":
            self.app.push_screen(
                TransitionScreen(
                    self.transitions, self.issue["key"], self.app.jira_client
                )
            )
        if event.key == "c":
            try:
                comment_widget = self.query_one(CommentInput)
                comment_widget.remove()
            except Exception:
                self.mount(
                    CommentInput(
                        self.issue["key"],
                        self.app.jira_client,
                        self.add_comment_callback,
                    )
                )

        if event.key == "i":
            try:
                comment_input = self.query_one(CommentInput)
                input_widget = comment_input.query_one("#comment-input")
                input_widget.focus()
            except Exception:
                pass

    async def add_comment_callback(self, new_comment):
        self.comments.append(new_comment)
        logger.info("adding in a new comment")
        logger.info(self.comments)
        await self.recompose()
