from textual.reactive import reactive
from textual.widgets import Static
from textual.widget import Widget


class IssueList(Widget):
    issues_list = reactive([])
    selected = reactive(0)
    can_focus = True

    def __init__(self, on_select_callback, on_enter_issue):
        super().__init__()
        self.on_select = on_select_callback
        self.on_enter_issue = on_enter_issue

    def on_mount(self):
        self.focus()

    def compose(self):
        if not len(self.issues_list):
            yield Static("No issues yet")
        for idx, issue in enumerate(self.issues_list):
            prefix = "->" if idx == self.selected else ""
            yield Static(f"{prefix}{issue['key']}: {issue['summary']}")

    def on_key(self, event):
        if event.key == "j":
            self.selected = min(self.selected + 1, len(self.issues_list) - 1)
            self.on_select(self.issues_list[self.selected])
            self.refresh()
        elif event.key == "k":
            self.selected = max(self.selected - 1, 0)
            self.on_select(self.issues_list[self.selected])
            self.refresh()
        elif event.key == "enter":
            self.on_enter_issue()
        elif event.key == "q" or event.key == "escape":
            self.app.exit()

    async def watch_selected(self, old, new):
        await self.recompose()
        self.refresh()
