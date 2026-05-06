"""
title: Code Folding
icon_url: data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0xOCAxNWwtNi02LTYgNiIvPjwvc3ZnPg==
version: 0.2.0
description: Automatically folds long code blocks in chat responses with a click-to-expand UI.
"""

import re
import asyncio
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

LANG_LABELS = {
    "py": "Python", "python": "Python",
    "js": "JavaScript", "javascript": "JavaScript",
    "ts": "TypeScript", "typescript": "TypeScript",
    "html": "HTML", "css": "CSS",
    "json": "JSON", "xml": "XML", "yaml": "YAML", "yml": "YAML", "toml": "TOML",
    "sh": "Shell", "bash": "Bash", "zsh": "Shell", "powershell": "PowerShell",
    "sql": "SQL",
    "rust": "Rust", "rs": "Rust",
    "go": "Go", "golang": "Go",
    "java": "Java",
    "cpp": "C++", "c": "C", "csharp": "C#", "cs": "C#",
    "ruby": "Ruby", "rb": "Ruby",
    "php": "PHP", "swift": "Swift",
    "kotlin": "Kotlin", "kt": "Kotlin",
    "dart": "Dart", "r": "R", "lua": "Lua",
    "perl": "Perl", "pl": "Perl", "scala": "Scala",
    "haskell": "Haskell", "hs": "Haskell",
    "elixir": "Elixir", "clojure": "Clojure",
    "makefile": "Makefile", "make": "Makefile",
    "dockerfile": "Dockerfile", "docker": "Dockerfile",
    "diff": "Diff",
    "graphql": "GraphQL", "gql": "GraphQL",
    "markdown": "Markdown", "md": "Markdown",
    "text": "Text", "plaintext": "Text", "txt": "Text",
    "ini": "INI", "cfg": "INI",
    "bat": "Batch", "cmd": "Batch",
}

toggle = True


class Filter:
    class Valves(BaseModel):
        MAX_LINES: int = Field(
            default=30,
            description="Fold code blocks exceeding this many lines. | 代码行数超过此值自动折叠。",
        )
        SHOW_LINES: int = Field(
            default=1,
            description="Lines to show in preview before the fold. | 折叠前预览显示的行数。",
        )

    class UserValves(BaseModel):
        pass

    def __init__(self):
        self.valves = self.Valves()

    @staticmethod
    def _escape_html(text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

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
            preview_lines = lines[:show]
            preview_items = [l.strip()[:80] for l in preview_lines if l.strip()]
            preview_text = " | ".join(preview_items)
            if not preview_text:
                preview_text = f"{total} lines"

            lang_label = LANG_LABELS.get(lang, lang if lang else "Code")
            escaped = self._escape_html(code)

            return (
                f'<details class="owui-code-fold" style="margin:8px 0;">\n'
                f'<summary style="cursor:pointer;padding:8px 14px;background:var(--code-bg,#f4f4f4);border:1px solid var(--border-color,#e0e0e0);border-radius:6px;font-family:monospace;font-size:0.85em;user-select:none;">\n'
                f'  <strong>{lang_label}</strong> \u2014 {total} lines'
                f'{" | " + preview_text if preview_text else ""}\n'
                f'  <span style="float:right;color:#888;">\u25bc</span>\n'
                f'</summary>\n'
                f'<pre style="margin:0;border:1px solid var(--border-color,#e0e0e0);border-top:none;border-radius:0 0 6px 6px;padding:12px;overflow-x:auto;background:var(--code-bg,#f4f4f4);"><code class="language-{lang}">{escaped}</code></pre>\n'
                f'</details>'
            )

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