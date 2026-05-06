# OpenWebuiFunctions

Custom Functions/Plugins for Open WebUI.

## Tools

### MindMap Generator (`Tools/mindmap.py`)

Analyzes text content and generates interactive mind maps using Markmap.js.

**Features:**
- Extracts key concepts from long text and renders as an interactive SVG mind map
- Supports Chinese and English UI (configurable in Valves)
- Download mind map as SVG or Markdown
- Accumulates multiple mind maps in a single chat (or overwrite mode)
- Uses the current chat model or a user-specified model

**Configuration (Valves):**
| Field | Description |
|---|---|
| `SHOW_STATUS` | Show status updates in chat |
| `MODEL_ID` | Specify LLM model (empty = use current chat model) |
| `MIN_TEXT_LENGTH` | Minimum text length for analysis (default: 100) |
| `CLEAR_PREVIOUS_HTML` | Overwrite instead of merging multiple results |
| `LANGUAGE` | Display language: 中文 / English |

### Code Folding (`Tools/code_folding.py`)

A **Filter** plugin that automatically folds long code blocks in assistant responses with a click-to-expand `<details>` UI.

**Features:**
- Folds code blocks exceeding a configurable line threshold
- Shows a preview (first N lines) with language label and line count
- Click to expand the full code block
- Supports 50+ language labels for display
- Toggle on/off globally from the Functions panel

**Configuration (Valves):**
| Field | Default | Description |
|---|---|---|
| `MAX_LINES` | 30 | Fold code blocks exceeding this many lines |
| `SHOW_LINES` | 1 | Lines to show in preview before the fold |
