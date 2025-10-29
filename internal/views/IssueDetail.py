from textual.widgets import Static
from textual.widget import Widget
from textual.reactive import reactive
from ..utils.description import extract_description_content
from textual.containers import Vertical, VerticalScroll
from ..components.Comment import Comment
from ..components.CommentContent import CommentContent
from ..components.CommentInput import CommentInput
from ..views.TransitionScreen import TransitionScreen


class IssueDetail(Widget):
    issue = reactive(None)
    can_focus = True
    comments = reactive([])
    selected_comment = reactive(0)

    async def on_mount(self):
        if self.issue:
            self.comments = await self.app.jira_client.fetch_issue_comments(
                self.issue["key"]
            )
        self.selected_comment = 0
        await self.recompose()
        self.refresh()

    def __init__(self, issue: dict | None, on_exit_issue):
        super().__init__()
        self.issue = issue
        self.on_exit_issue = on_exit_issue

    def compose(self):
        if not self.issue:
            yield Static("No issue selected", classes="no-issue")
        else:
            # Header section
            yield Vertical(
                Static(f"[b]{self.issue['key']}[/b]", classes="issue-key"),
                Static(self.issue["summary"], classes="issue-summary"),
                Static(f"Status: {self.issue['status']}"),
                Static(f"Assigned to: {self.issue['assignee']}"),
                Static(f"Reported by: {self.issue['reporter']}"),
                classes="issue-header",
            )
            # Description section
            yield Static("[b]Description[/b]", classes="section-title")
            for line in extract_description_content(self.issue["description"]):
                yield Static(line, classes="issue-description")
            # Comments section
            if self.comments:
                yield Static("[b]Comments[/b]", classes="section-title")
                yield VerticalScroll(
                    *[
                        Comment(
                            author=comment["author"]["displayName"],
                            content=CommentContent(
                                comment["body"]["content"][0]["content"]
                            ).get_content(),
                            selected=self.selected_comment == idx,
                        )
                        for idx, comment in enumerate(self.comments)
                    ],
                    classes="comments-list",
                )

    async def watch_issue(self, old, new):
        if self.issue:
            self.comments = await self.app.jira_client.fetch_issue_comments(
                self.issue["key"]
            )
        self.selected_comment = 0
        await self.recompose()
        self.refresh()

    def on_key(self, event):
        # if event.key == "q" or event.key == "escape":
        #     self.blur()
        if event.key == "j":
            self.selected_comment = min(
                self.selected_comment + 1, len(self.comments) - 1
            )
            self.refresh()
        elif event.key == "k":
            self.selected_comment = max(self.selected_comment - 1, 0)
            self.refresh()

        elif event.key == "q" or event.key == "escape":
            try:
                comment_input = self.query_one(CommentInput)
                input_widget = comment_input.query_one("#comment-input")
                if input_widget.has_focus:
                    input_widget.blur()
                else:
                    input_widget.remove()
            except Exception:
                self.on_exit_issue()
        if event.key == "t":
            if self.issue:
                self.app.push_screen(
                    TransitionScreen(
                        self.issue["key"],
                    )
                )
        if event.key == "c" and self.issue:
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

    async def watch_selected_comment(self):
        await self.recompose()
        self.refresh()

    async def add_comment_callback(self, new_comment):
        self.comments.append(new_comment)
        await self.recompose()
