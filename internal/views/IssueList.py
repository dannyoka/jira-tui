from textual.reactive import reactive
from textual.app import ComposeResult
from textual.widgets import ListView, ListItem, Label


class IssueList(ListView):
    selected = reactive(0)

    def __init__(self, issues, on_selected):
        super().__init__()
        self.issues = issues
        self.on_selected = on_selected

    def compose(self) -> ComposeResult:
        for idx, issue in enumerate(self.issues):
            prefix = "➤ " if idx == self.selected else "  "
            yield ListItem(
                Label(f"{prefix}{issue['key']}: {issue['summary']}", id=f"issue-{idx}")
            )

    async def on_list_view_selected(self, event):
        selected_key = event.item.id
        selected_issue = next(i for i in self.issues if i["key"] == selected_key)
        if callable(self.on_select):
            result = self.on_select(selected_issue)
            if hasattr(result, "__await__"):
                await result
            else:
                result

    async def on_key(self, event):
        if event.key == "j":
            self.action_cursor_down()
        if event.key == "k":
            self.action_cursor_up()
