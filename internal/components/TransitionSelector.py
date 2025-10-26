from textual.widget import Widget
from textual.reactive import reactive
from textual import events

import logging

logger = logging.getLogger(__name__)


class TransitionSelector(Widget):
    transitions = reactive([])
    selected = reactive(0)
    can_focus = True

    async def on_mount(self):
        self.focus()

    def __init__(self, transitions, issue_key, jira_client):
        super().__init__()
        self.transitions = transitions
        self.issue_key = issue_key
        self.jira_client = jira_client

    def render(self):
        lines = []
        for idx, t in enumerate(self.transitions):
            prefix = "➤ " if idx == self.selected else "  "
            lines.append(f"{prefix}{t['name']}")
        return "\n".join(lines)

    async def key_press(self, event: events.Key):
        if event.key == "j":
            self.selected = min(self.selected + 1, len(self.transitions) - 1)
            self.refresh()
        elif event.key == "k":
            self.selected = max(self.selected - 1, 0)
            self.refresh()
        elif event.key == "x":
            logger.info("Pushed the space key")
            transition_id = self.transitions[self.selected]["id"]
            try:
                await self.jira_client.transition_issue(self.issue_key, transition_id)
            except Exception as e:
                # Optionally, display an error message to the user

                logger.error(f"Transition failed: {e}")
            else:
                self.app.pop_screen()

    async def on_key(self, event):
        await self.key_press(event)
