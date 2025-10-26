from textual.widget import Widget
from textual.widgets import Input, Button, Static
from textual.containers import Vertical
from textual.app import ComposeResult


class CommentInput(Widget):
    def __init__(self, issue_key, jira_client):
        super().__init__()
        self.issue_key = issue_key
        self.jira_client = jira_client

    def compose(self) -> ComposeResult:
        yield Static("Add a comment:")
        yield Input(placeholder="Type your comment...", id="comment-input")
        yield Button("Submit", id="submit-comment")

    async def on_button_pressed(self, event):
        if event.button.id == "submit-comment":
            input_widget = self.query_one("#comment-input", Input)
            comment = input_widget.value
            if comment.strip():
                await self.jira_client.add_issue_comment(self.issue_key, comment)
                # Optionally clear input or show a success message
                input_widget.value = ""
                # Optionally pop the widget/screen or refresh comments

    async def on_input_submitted(self, event):
        input_widget = event.input
        comment = input_widget.value
        if comment.strip():
            await self.jira_client.add_issue_comment(self.issue_key, comment)
            input_widget.value = ""
            self.remove()
            # Optionally refresh comments or show a message
