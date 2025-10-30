import asyncio
import logging
from textual.widgets import Input, Static, Select, Button
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.reactive import reactive
from textual.widget import Widget

logger = logging.getLogger(__name__)


class QuerySelect(Widget):
    options = reactive([])

    def __init__(self, on_set_assignee):
        super().__init__()
        self.on_set_assignee = on_set_assignee
        self.debounce_task = None
        # self.select = Select(options=self.options, prompt="Results", id="results")
        self.input = Input(placeholder="Type to search...", id="query")

    def compose(self):
        yield self.input
        # yield self.select
        # if len(self.options):
        #     for user in self.options:
        #         yield Static(user[0])

    async def on_select_changed(self, event):
        self.on_set_assignee(event.select.value)
        logger.info(f"selected value {event.select.value}")

    async def on_input_changed(self, event):
        query = event.input.value
        # Debounce logic
        if self.debounce_task:
            self.debounce_task.cancel()
        self.debounce_task = asyncio.create_task(self.debounced_fetch(query))

    async def debounced_fetch(self, query):
        await asyncio.sleep(0.3)  # debounce delay
        results = await self.app.jira_client.fetch_assignable_users("QANS", query)
        # select = self.query_one("#results")
        options = [(item["displayName"], item["accountId"]) for item in results]
        # logger.info(f"options are {select.options}")
        self.options = options
        await self.recompose()

    async def watch_options(self, old, new):
        if len(new):
            try:
                select = self.query_one(Select)
                await select.remove()
                self.mount(
                    Select(options=self.options, prompt="Results", id="results"),
                    after="#query",
                )
            except Exception:
                self.mount(
                    Select(options=self.options, prompt="Results", id="results"),
                    after="#query",
                )


class MyModal(ModalScreen):
    assignees = reactive([])

    def __init__(self, default_project_id, sprints, on_submit, current_user):
        super().__init__()
        self.project_id = default_project_id
        self.sprints = sprints
        self.on_submit = on_submit
        self.current_user = current_user
        self.assignee = current_user

    def compose(self):
        yield Static("Create New Issue", classes="form-title")
        yield Select(
            options=[(s["name"], s["id"]) for s in self.sprints["values"]],
            prompt="Sprint",
            id="sprint",
        )
        yield QuerySelect(on_set_assignee=self.on_set_assignee)
        yield Input(placeholder="Summary", id="summary")
        yield Input(placeholder="Description", id="description")
        yield Input(placeholder="Story Points", id="story-points")
        yield Button("Create Issue", id="submit")

    async def on_button_pressed(self, event):
        if event.button.id == "submit":
            sprint_id = self.query_one("#sprint").value
            summary = self.query_one("#summary").value
            description = self.query_one("#description").value
            story_points = self.query_one("#story-points").value
            await self.on_submit(
                {
                    "project_id": self.project_id,
                    "sprint_id": sprint_id,
                    "summary": summary,
                    "description": description,
                    "story_points": int(story_points),
                    "assignee": self.assignee,
                    "reporter": self.current_user["accountId"],
                }
            )

    def on_set_assignee(self, assignee):
        self.assignee = assignee
        logger.info("set assignee has been called with value of " + self.assignee)
