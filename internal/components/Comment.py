from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Vertical


class Comment(Widget):
    def __init__(self, author: str, content: str, selected: bool):
        super().__init__()
        self.author = author
        self.content = content
        self.selected = selected

    def compose(self):
        yield Vertical(
            Static(f"[b]{self.author}[/b]", classes="comment-author"),
            Static(self.content, classes="comment-content"),
            classes="selected" if self.selected else "",
        )
