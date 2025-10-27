from textual.widget import Widget
from textual.widgets import Input, Static
from textual.app import ComposeResult
from textual import events
import logging

logger = logging.getLogger(__name__)


class CommentInput(Widget):
    def __init__(self, issue_key, jira_client, add_comment_callback):
        super().__init__()
        self.issue_key = issue_key
        self.jira_client = jira_client
        self.add_comment_callback = add_comment_callback

    def compose(self) -> ComposeResult:
        yield Static("Add a comment:")
        yield Input(placeholder="Type your comment...", id="comment-input")

    async def on_input_submitted(self, event):
        input_widget = event.input
        comment = input_widget.value
        if comment.strip():
            new_comment = await self.jira_client.add_issue_comment(
                self.issue_key, comment
            )
            await self.add_comment_callback(new_comment)
            input_widget.value = ""
            self.remove()

    async def key_press(self, event: events.Key):
        input_widget = self.query_one("#comment-input")
        # I don't like this, I think I'd prefer it to be I, but that's not working properly
        if event.key == "i":
            comment_input = self.query_one("#comment-input")
            input_widget = comment_input.query_one("#comment-input")
            input_widget.focus()
        if event.key == "tab":
            input_widget.focus()
        if event.key == "escape":
            input_widget.blur()

    async def on_key(self, event):
        await self.key_press(event)
