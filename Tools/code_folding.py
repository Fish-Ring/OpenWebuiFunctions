"""
title: Code Folding
icon_url: data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0xOCAxNWwtNi02LTYgNiIvPjwvc3ZnPg==
version: 0.4.0
description: Auto-fold code blocks exceeding N lines into click-to-expand HTML blocks.
"""

import re
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

toggle = True


class Filter:
    class Valves(BaseModel):
        MAX_LINES: int = Field(
            default=30,
            description="Auto-fold blocks over this many lines. | 超过此行数自动折叠。",
        )

    class UserValves(BaseModel):
        pass

    def __init__(self):
        self.valves = self.Valves()

    @staticmethod
    def _escape(text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _fold(self, content: str) -> str:
        def replace_block(m):
            lang = m.group(1).strip() or ""
            code = m.group(2)
            lines = code.split("\n")
            total = len(lines)

            if total <= self.valves.MAX_LINES:
                return m.group(0)

            first = lines[0][:80] if lines else ""
            label = lang if lang else "Code"
            escaped = self._escape(code)

            return (
                f'\n```html\n'
                f'<!-- OPENWEBUI_PLUGIN_OUTPUT -->\n'
                f'<details style="margin:4px 0;border:1px solid #444;border-radius:6px;overflow:hidden;">\n'
                f'<summary style="cursor:pointer;padding:6px 14px;background:#1e1e1e;'
                f'color:#d4d4d4;font-family:monospace;font-size:0.8em;user-select:none;">'
                f'\u25b6 {label} \u2502 {total} lines \u2502 {first}</summary>\n'
                f'<pre style="margin:0;padding:10px 14px;background:#1e1e1e;'
                f'color:#d4d4d4;overflow-x:auto;font-size:0.85em;line-height:1.5;">'
                f'<code class="language-{lang}">{escaped}</code></pre>\n'
                f'</details>\n'
                f'```'
            )

        return re.sub(r"```(\S*)\s*\n(.*?)```", replace_block, content, flags=re.DOTALL)

    async def outlet(self, body: dict, __user__: Optional[Dict] = None, __event_emitter__: Optional[Any] = None) -> dict:
        for msg in body.get("messages", []):
            if msg.get("role") == "assistant" and isinstance(msg.get("content"), str):
                msg["content"] = self._fold(msg["content"])
        return body
