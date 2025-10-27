from internal.api.jira_client import JiraClient
from textual.app import App
from internal.views.Dashboard import Dashboard


class JiraTUI(App):
    CSS_PATH = "styles.tcss"

    def on_mount(self):
        self.push_screen(Dashboard())
        self.jira_client = JiraClient()
