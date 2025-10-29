def extract_comment_content(body):
    if not body or "content" not in body:
        return ["No content."]
    result = []
    for block in body["content"]:
        block_type = block.get("type")
        # Paragraphs
        if block_type == "paragraph":
            line = ""
            for item in block.get("content", []):
                if item["type"] == "text":
                    text = item.get("text", "")
                    # Bold
                    if "marks" in item:
                        for mark in item["marks"]:
                            if mark["type"] == "strong":
                                text = f"[b]{text}[/b]"
                            if mark["type"] == "code":
                                text = f"`{text}`"
                            if mark["type"] == "link":
                                href = mark["attrs"]["href"]
                                text = f"{text} ({href})"
                    line += text
                elif item["type"] == "mention":
                    line += item["attrs"].get("text", "")
                elif item["type"] == "hardBreak":
                    line += "\n"
                elif item["type"] == "inlineCard":
                    url = item["attrs"]["url"]
                    line += f"{url}"
            if line.strip():
                result.append(line)
        # Tables
        elif block_type == "table":
            table_rows = []
            for row in block.get("content", []):
                row_cells = []
                for cell in row.get("content", []):
                    # TableHeader or TableCell
                    cell_text = ""
                    for para in cell.get("content", []):
                        if para.get("type") == "paragraph":
                            for item in para.get("content", []):
                                if item.get("type") == "text":
                                    cell_text += item.get("text", "")
                    row_cells.append(cell_text)
                table_rows.append(row_cells)
            # Format table for Textual
            if table_rows:
                # Header
                header = " | ".join(table_rows[0])
                result.append(header)
                result.append("-" * len(header))
                # Rows
                for row in table_rows[1:]:
                    result.append(" | ".join(row))
        # Headings
        elif block_type == "heading":
            level = block.get("attrs", {}).get("level", 1)
            heading_text = ""
            for item in block.get("content", []):
                if item["type"] == "text":
                    heading_text += item.get("text", "")
            result.append(f"{'#' * level} {heading_text}")
        # Ordered List
        elif block_type == "orderedList":
            order = block.get("attrs", {}).get("order", 1)
            for idx, li in enumerate(block.get("content", []), start=order):
                for para in li.get("content", []):
                    if para["type"] == "paragraph":
                        line = ""
                        for item in para.get("content", []):
                            if item["type"] == "text":
                                line += item.get("text", "")
                        result.append(f"{idx}. {line}")
        # Bullet List
        elif block_type == "bulletList":
            for li in block.get("content", []):
                for para in li.get("content", []):
                    if para["type"] == "paragraph":
                        line = ""
                        for item in para.get("content", []):
                            if item["type"] == "text":
                                line += item.get("text", "")
                        result.append(f"- {line}")
        # Media
        elif block_type == "mediaSingle":
            for media in block.get("content", []):
                if media["type"] == "media":
                    alt = media["attrs"].get("alt", "media")
                    result.append(f"[media: {alt}]")
    return result
