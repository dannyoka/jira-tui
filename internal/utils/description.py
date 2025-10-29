def extract_description_content(description):
    if not description or "content" not in description:
        return ["No description."]
    result = []
    for block in description["content"]:
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
                elif item["type"] == "hardBreak":
                    line += "\n"
                elif item["type"] == "inlineCard":
                    url = item["attrs"]["url"]
                    line += f"{url}"
            if line.strip():
                result.append(line)
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
