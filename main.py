from internal.api.jira_client import JiraClient
from textual.app import App
from internal.views.Dashboard import Dashboard
import logging

logging.basicConfig(filename="app.log", level=logging.DEBUG)
logger = logging.getLogger(__name__)


class JiraTUI(App):
    def on_mount(self):
        self.push_screen(Dashboard())
        self.jira_client = JiraClient()


if __name__ == "__main__":
    JiraTUI().run()
