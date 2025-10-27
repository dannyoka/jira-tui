from textual.widgets import Static


class IssueDetail(Static):
    def update_issue(self, issue):
        self.update(
            f"Issue: {issue['key']}\nStatus: {issue['status']}\nSummary: {issue['summary']}\n\nComments:\n"
            + "\n".join(
                [
                    f"{c['author']['displayName']}: {c['body']['content'][0]['content'][0]['text']}"
                    for c in issue["comments"]
                ]
            )
        )
