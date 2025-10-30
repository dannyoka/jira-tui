import asyncio
from textual.widget import Widget
from textual.widgets import Input, Select, Button, Static


class AssignIssue(Widget):
    def __init__(self, issue_key, on_assigned=None):
        super().__init__()
        self.issue_key = issue_key
        self.on_assigned = on_assigned
        self.debounce_task = None
        self.select = Select(options=[], prompt="Select user", id="user-select")
        self.input = Input(placeholder="Search for user...", id="user-query")
        self.button = Button("Assign", id="assign-btn")

    def compose(self):
        yield Static(f"Assign issue: {self.issue_key}", classes="assign-title")
        yield self.input
        yield self.select
        yield self.button

    async def on_input_changed(self, event):
        query = event.input.value
        if self.debounce_task:
            self.debounce_task.cancel()
        self.debounce_task = asyncio.create_task(self.debounced_fetch(query))

    async def debounced_fetch(self, query):
        await asyncio.sleep(0.3)
        results = await self.app.jira_client.fetch_assignable_users(
            self.issue_key.split("-")[0], query
        )
        self.select.options = [
            (user["displayName"], user["accountId"]) for user in results
        ]
        self.select.refresh()

    async def on_button_pressed(self, event):
        if event.button.id == "assign-btn":
            account_id = self.select.value
            if account_id:
                success = await self.app.jira_client.assign_issue(
                    self.issue_key, account_id
                )
                if success:
                    await self.on_assigned(self.issue_key, account_id)
                    self.remove()
