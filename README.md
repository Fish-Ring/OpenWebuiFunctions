# OpenWebuiFunctions

Custom Functions/Plugins for [Open WebUI](https://docs.openwebui.com).

## Tools

### MindMap Generator `Tools/mindmap.py`

Analyzes text → interactive SVG mind map (Markmap.js). Bilingual UI (configurable).

| Valve | Default | Description |
|---|---|---|
| `SHOW_STATUS` | true | Show status updates |
| `MODEL_ID` | "" | LLM model (empty = chat model) |
| `MIN_TEXT_LENGTH` | 100 | Min chars to analyze |
| `CLEAR_PREVIOUS_HTML` | false | Overwrite vs merge |
| `LANGUAGE` | zh-CN | 中文 / English |
