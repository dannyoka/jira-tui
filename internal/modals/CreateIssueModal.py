import logging
from textual.widgets import Input, Static, Select, Button
from textual.screen import ModalScreen
from textual.reactive import reactive
from ..components.QuerySelect import QuerySelect

logger = logging.getLogger(__name__)


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
