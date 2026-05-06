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

### Code Folding `Tools/code_folding.py`

Filter (outlet hook). Auto-folds long code blocks in assistant responses.

| Valve | Default | Description |
|---|---|---|
| `MAX_LINES` | 30 | Fold blocks exceeding this |
| `SHOW_LINES` | 1 | Preview lines before fold |
