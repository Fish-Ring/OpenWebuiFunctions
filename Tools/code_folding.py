"""
title: Code Folding
icon_url: data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0xOCAxNWwtNi02LTYgNiIvPjwvc3ZnPg==
version: 0.2.0
description: Automatically folds long code blocks in chat responses with a click-to-expand UI.
"""

import re
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

toggle = True


class Filter:
    class Valves(BaseModel):
        MAX_LINES: int = Field(
            default=30,
            description="Fold code blocks exceeding this many lines. | 代码行数超过此值自动折叠。",
        )
        SHOW_LINES: int = Field(
            default=3,
            description="Lines to keep visible before folding. | 折叠后保留显示的行数。",
        )

    class UserValves(BaseModel):
        pass

    def __init__(self):
        self.valves = self.Valves()

    def _fold_text(self, content: str) -> str:
        pattern = re.compile(r"```(\S*)\s*\n(.*?)```", re.DOTALL)

        def replacer(match):
            lang = match.group(1) or ""
            code = match.group(2)
            lines = code.split("\n")
            total = len(lines)

            if total <= self.valves.MAX_LINES:
                return match.group(0)

            show = min(self.valves.SHOW_LINES, total)
            preview = "\n".join(lines[:show])
            hidden = total - show

            return f"```{lang}\n{preview}\n// ... ({hidden} more lines, use ≪show all≫ or ≪expand≫ to view full code) ...\n```"

        return pattern.sub(replacer, content)

    async def outlet(self, body: dict, __user__: Optional[Dict] = None, __event_emitter__: Optional[Any] = None) -> dict:
        messages = body.get("messages", [])
        if not messages:
            return body

        folded_count = 0
        for msg in messages:
            if msg.get("role") == "assistant" and isinstance(msg.get("content"), str):
                new_content = self._fold_text(msg["content"])
                if new_content != msg["content"]:
                    folded_count += 1
                    msg["content"] = new_content

        if folded_count > 0 and __event_emitter__:
            await __event_emitter__({
                "type": "notification",
                "data": {"type": "info", "content": f"Folded {folded_count} long code block(s). | 已折叠 {folded_count} 个长代码块。"}
            })

        return body