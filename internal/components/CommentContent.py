from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class CommentContent:
    content: List[Dict[str, Any]]

    def get_content(self) -> str:
        val = ""
        for item in self.content:
            item_type = item.get("type")
            if item_type == "text":
                val += item.get("text", "")
            elif item_type == "mention":
                attrs = item.get("attrs", {})
                val += attrs.get("text", "")
            elif item_type in ("hardBreak", "hardbreak"):
                val += "\n"
        return val
