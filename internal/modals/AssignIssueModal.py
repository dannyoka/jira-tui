from internal.components.AssignIssue import AssignIssue
from textual.screen import ModalScreen


class AssignIssueModal(ModalScreen):
    def __init__(self, issue_key, on_assigned):
        super().__init__()
        self.issue_key = issue_key
        self.on_assigned = on_assigned

    def compose(self):
        yield AssignIssue(self.issue_key, self.on_assigned)

    def on_key(self, event):
        if event.key == "q":
            self.remove()
