import asyncio
from textual.widgets import Input, Select
from textual.reactive import reactive
from textual.widget import Widget

import logging

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
