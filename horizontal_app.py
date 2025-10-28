from internal.api.jira_client import JiraClient
import asyncio
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import ListView, Static
from textual import events


class IssueList(ListView):
    def __init__(self, issues, on_select):
        super().__init__()
        self.issues = issues
        self.on_select = on_select
        for issue in issues:
            self.append(Static(issue["summary"], id=issue["key"]))

    async def on_list_view_selected(self, event):
        selected_key = event.item.id
        selected_issue = next(i for i in self.issues if i["key"] == selected_key)
        await self.on_select(selected_issue)


class MyApp(App):
    CSS_PATH = "styles.tcss"

    def __init__(self, issues):
        super().__init__()
        self.issues = issues
        self.issue_detail = IssueDetail()
        self.issue_list = IssueList(issues, self.on_issue_selected)
        self.focus_left = True

    def compose(self) -> ComposeResult:
        yield Horizontal(
            VerticalScroll(self.issue_list, id="left-pane"),
            VerticalScroll(self.issue_detail, id="right-pane"),
        )

    async def on_mount(self):
        self.issue_list.focus()

    async def on_key(self, event: events.Key):
        if event.key == "h":
            self.issue_list.focus()
            self.focus_left = True
        elif event.key == "l":
            self.issue_detail.focus()
            self.focus_left = False

    async def on_issue_selected(self, issue):
        self.issue_detail.update_issue(issue)


async def main():
    issues = await JiraClient().fetch_issues()
    MyApp(issues).run()


if __name__ == "__main__":
    asyncio.run(main())
