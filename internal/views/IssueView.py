from internal.components.Comment import Comment
from internal.components.CommentContent import CommentContent
from internal.components.CommentInput import CommentInput
from internal.views.TransitionScreen import TransitionScreen
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Static
from textual.reactive import reactive
from textual.containers import VerticalScroll
import logging

logger = logging.getLogger(__name__)


class IssueView(Screen):
    comments = reactive([])
    transitions = reactive([])
    selectedComment = reactive(0)

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
            yield VerticalScroll(
                *[
                    Comment(
                        author=comment["author"]["displayName"],
                        content=CommentContent(
                            comment["body"]["content"][0]["content"]
                        ).get_content(),
                        selected=self.selectedComment == idx,
                    )
                    for comment in self.comments
                ],
            )
            # yield Static(json.dumps(comment, indent=4), id=f"comment-{idx}")

    def on_key(self, event):
        if event.key == "q":
            self.app.pop_screen()
        if event.key == "t":
            self.app.push_screen(
                TransitionScreen(
                    self.issue["key"],
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
        if event.key == "j":
            self.selectedComment = min(self.selectedComment + 1, len(self.comments) - 1)
            self.refresh()
        if event.key == "k":
            self.selectedComment = max(self.selectedComment - 1, 0)
            self.refresh()

    async def add_comment_callback(self, new_comment):
        self.comments.append(new_comment)
        await self.recompose()
