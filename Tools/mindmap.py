"""
title: MindMap Generator
icon_url: data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+CiAgPGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMyIgZmlsbD0iY3VycmVudENvbG9yIi8+CiAgPGxpbmUgeDE9IjEyIiB5MT0iOSIgeDI9IjEyIiB5Mj0iNCIvPgogIDxjaXJjbGUgY3g9IjEyIiBjeT0iMyIgcj0iMS41Ii8+CiAgPGxpbmUgeDE9IjEyIiB5MT0iMTUiIHgyPSIxMiIgeTI9IjIwIi8+CiAgPGNpcmNsZSBjeD0iMTIiIGN5PSIyMSIgcj0iMS41Ii8+CiAgPGxpbmUgeDE9IjkiIHkxPSIxMiIgeDI9IjQiIHkyPSIxMiIvPgogIDxjaXJjbGUgY3g9IjMiIGN5PSIxMiIgcj0iMS41Ii8+CiAgPGxpbmUgeDE9IjE1IiB5MT0iMTIiIHgyPSIyMCIgeTI9IjEyIi8+CiAgPGNpcmNsZSBjeD0iMjEiIGN5PSIxMiIgcj0iMS41Ii8+CiAgPGxpbmUgeDE9IjEwLjUiIHkxPSIxMC41IiB4Mj0iNiIgeTI9IjYiLz4KICA8Y2lyY2xlIGN4PSI1IiBjeT0iNSIgcj0iMS41Ii8+CiAgPGxpbmUgeDE9IjEzLjUiIHkxPSIxMC41IiB4Mj0iMTgiIHkyPSI2Ii8+CiAgPGNpcmNsZSBjeD0iMTkiIGN5PSI1IiByPSIxLjUiLz4KICA8bGluZSB4MT0iMTAuNSIgeTE9IjEzLjUiIHgyPSI2IiB5Mj0iMTgiLz4KICA8Y2lyY2xlIGN4PSI1IiBjeT0iMTkiIHI9IjEuNSIvPgogIDxsaW5lIHgxPSIxMy41IiB5MT0iMTMuNSIgeDI9IjE4IiB5Mj0iMTgiLz4KICA8Y2lyY2xlIGN4PSIxOSIgY3k9IjE5IiByPSIxLjUiLz4KPC9zdmc+
version: 0.8.0
description: Analyzes text and generates interactive mind maps to help visualize knowledge structures.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging
import time
import re
from fastapi import Request
from datetime import datetime
import pytz

from open_webui.utils.chat import generate_chat_completion
from open_webui.models.users import Users

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

LANG_ZH = "zh-CN"
LANG_EN = "en"

I18N = {
    LANG_ZH: {
        "prompt_system": """你是一个专业的思维导图生成助手,能够高效地分析用户提供的长篇文本,并将其核心主题、关键概念、分支和子分支结构化为标准的Markdown列表语法,以便Markmap.js进行渲染。

请严格遵循以下指导原则:
-   **语言**: 所有输出必须使用用户指定的语言。
-   **格式**: 你的输出必须严格为Markdown列表格式,并用```markdown 和 ``` 包裹。
    -   使用 `#` 定义中心主题(根节点)。
    -   使用 `-` 和两个空格的缩进表示分支和子分支。
-   **内容**:
    -   识别文本的中心主题作为 `#` 标题。
    -   识别主要概念作为一级列表项。
    -   识别支持性细节或子概念作为嵌套的列表项。
    -   节点内容应简洁明了,避免冗长。
-   **只输出Markdown语法**: 不要包含任何额外的寒暄、解释或引导性文字。
-   **如果文本过短或无法生成有效导图**: 请输出一个简单的Markdown列表,表示无法生成,例如:
    ```markdown
    # 无法生成思维导图
    - 原因: 文本内容不足或不明确
    ```""",
        "prompt_user": """请分析以下长篇文本,并将其核心主题、关键概念、分支和子分支结构化为标准的Markdown列表语法,以供Markmap.js渲染。

---
**用户上下文信息:**
用户姓名: {user_name}
当前日期时间: {current_date_time_str}
当前星期: {current_weekday}
当前时区: {current_timezone_str}
用户语言: {user_locale}
---

**长篇文本内容:**
{long_text_content}""",
        "ui_title": "思维导图",
        "ui_user": "用户",
        "ui_time": "时间",
        "ui_btn_locate": "定位",
        "ui_btn_svg": "SVG",
        "ui_btn_md": "Markdown",
        "ui_footer": "智能思维导图",
        "notify_start": "正在为您生成思维导图...",
        "notify_success": "思维导图已生成, {user_name}！",
        "notify_error": "生成失败, {user_name}！",
        "status_analyzing": "深入分析文本结构...",
        "status_done": "绘制完成！",
        "status_failed": "处理失败。",
        "error_no_message": "无法获取有效的用户消息内容。",
        "error_short_text": "文本内容过短({len}字符)，无法进行有效分析。请提供至少{min}字符的文本。",
        "error_user_not_found": "无法获取用户对象，用户ID: {user_id}",
        "error_llm_response": "LLM响应格式不正确或为空。",
        "error_generic": "抱歉，处理时遇到错误: {error}。\n请检查Open WebUI后端日志获取更多详情。",
        "error_action": "处理失败: {error}",
        "log_started": "Action: MindMap started",
        "log_completed": "Action: MindMap completed successfully",
        "log_llm_unexpected": "LLM输出未严格遵循预期Markdown格式，将整个输出作为摘要处理。",
        "log_timezone_fail": "获取时区信息失败: {error}，使用默认值。",
        "js_timeout": "库加载超时，请刷新重试。",
        "js_no_content": "无法加载思维导图：缺少有效内容。",
        "js_render_fail": "思维导图渲染失败！",
        "js_render_reason": "原因",
        "date_format": "%Y年%m月%d日 %H:%M:%S",
        "unknown_weekday": "未知星期",
        "unknown_tz": "未知时区",
    },
    LANG_EN: {
        "prompt_system": """You are a professional mind map generation assistant. Analyze the user's long text and structure its core themes, key concepts, branches, and sub-branches into standard Markdown list syntax for Markmap.js rendering.

Follow these guidelines strictly:
- **Language**: All output must use the language specified by the user.
- **Format**: Your output must be strictly Markdown list format, wrapped with ```markdown and ```.
    - Use `#` for the central topic (root node).
    - Use `-` with two-space indentation for branches and sub-branches.
- **Content**:
    - Identify the central topic as the `#` heading.
    - Identify main concepts as top-level list items.
    - Identify supporting details or sub-concepts as nested list items.
    - Node content should be concise and clear, avoid verbosity.
- **Output Markdown only**: Do not include any extra greetings, explanations, or introductory text.
- **If the text is too short or cannot produce a valid map**: Output a simple Markdown list indicating failure, for example:
    ```markdown
    # Unable to generate mind map
    - Reason: Text content is insufficient or unclear
    ```""",
        "prompt_user": """Please analyze the following long text and structure its core themes, key concepts, branches, and sub-branches into standard Markdown list syntax for Markmap.js rendering.

---
**User Context:**
User Name: {user_name}
Current Date/Time: {current_date_time_str}
Current Weekday: {current_weekday}
Current Timezone: {current_timezone_str}
User Language: {user_locale}
---

**Long Text Content:**
{long_text_content}""",
        "ui_title": "Mind Map",
        "ui_user": "User",
        "ui_time": "Time",
        "ui_btn_locate": "Fit",
        "ui_btn_svg": "SVG",
        "ui_btn_md": "Markdown",
        "ui_footer": "Mind Map Generator",
        "notify_start": "Generating your mind map...",
        "notify_success": "Mind map generated, {user_name}!",
        "notify_error": "Generation failed, {user_name}!",
        "status_analyzing": "Analyzing text structure...",
        "status_done": "Rendering complete!",
        "status_failed": "Processing failed.",
        "error_no_message": "Could not get valid user message content.",
        "error_short_text": "Text too short ({len} chars). Please provide at least {min} characters.",
        "error_user_not_found": "Could not get user object, user ID: {user_id}",
        "error_llm_response": "LLM response format is incorrect or empty.",
        "error_generic": "Sorry, an error occurred: {error}.\nCheck Open WebUI backend logs for details.",
        "error_action": "Processing failed: {error}",
        "log_started": "Action: MindMap started",
        "log_completed": "Action: MindMap completed successfully",
        "log_llm_unexpected": "LLM output did not follow expected Markdown format, using entire output as summary.",
        "log_timezone_fail": "Failed to get timezone info: {error}, using defaults.",
        "js_timeout": "Library load timeout, please refresh.",
        "js_no_content": "Cannot load mind map: missing valid content.",
        "js_render_fail": "Mind map rendering failed!",
        "js_render_reason": "Reason",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "unknown_weekday": "Unknown",
        "unknown_tz": "Unknown",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    text = I18N.get(lang, I18N[LANG_ZH]).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text


HTML_WRAPPER_TEMPLATE = """
<!-- OPENWEBUI_PLUGIN_OUTPUT -->
<!DOCTYPE html>
<html lang="{user_locale}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        html, body {
            height: 100%;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
            background-color: #f8fafc; 
        }
        #main-container { 
            display: flex; 
            flex-direction: column;
            width: 100%;
            height: 100%;
        }
        .plugin-item { 
            flex: 1;
            display: flex;
            flex-direction: column;
            background: white; 
            overflow: hidden; 
            transition: all 0.3s ease;
            height: 100%;
        }
        /* STYLES_INSERTION_POINT */
    </style>
</head>
<body>
    <div id="main-container">
        <!-- CONTENT_INSERTION_POINT -->
    </div>
    <!-- SCRIPTS_INSERTION_POINT -->
</body>
</html>
"""

CSS_TEMPLATE_MINDMAP = """
        :root {
            --primary-color: #1e88e5;
            --secondary-color: #43a047;
            --background-color: #f4f6f8;
            --card-bg-color: #ffffff;
            --text-color: #263238;
            --muted-text-color: #546e7a;
            --border-color: #e0e0e0;
            --header-gradient: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
            --shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
            --border-radius: 12px;
            --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }
        .mindmap-container-wrapper {
            font-family: var(--font-family);
            line-height: 1.7;
            color: var(--text-color);
            margin: 0;
            padding: 0;
            background-color: var(--card-bg-color);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        .mindmap-container-wrapper * {
            box-sizing: border-box;
        }
        .user-context {
            font-size: 0.9em;
            color: var(--muted-text-color);
            background-color: #f8fafc;
            padding: 12px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            border-bottom: 1px solid var(--border-color);
        }
        .user-context .title {
            color: var(--text-color);
            font-weight: 700;
            font-size: 1.1em;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .user-context .info-group {
            display: flex;
            gap: 16px;
        }
        .user-context span { margin: 2px 8px; }
        .content-area { 
            padding: 20px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .markmap-container {
            position: relative;
            background-color: #fff;
            background-image: radial-gradient(var(--border-color) 0.5px, transparent 0.5px);
            background-size: 20px 20px;
            padding: 10px;
            flex-grow: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            border: 1px solid var(--border-color);
            box-shadow: inset 0 2px 6px rgba(0,0,0,0.03);
            overflow: hidden;
            border-radius: 4px;
        }
        .download-area {
            text-align: center;
            padding: 20px 0;
            display: flex;
            justify-content: center;
            gap: 12px;
            background: white;
            border-top: 1px solid var(--border-color);
        }
        .download-btn {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 0.9em;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease-in-out;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .download-btn.secondary {
            background-color: var(--secondary-color);
        }
        .download-btn.locate {
            background-color: #546e7a;
        }
        .download-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .download-btn.copied {
            background-color: #2e7d32;
        }
        .footer {
            text-align: center;
            padding: 12px;
            font-size: 0.75em;
            color: #90a4ae;
            background-color: #f8fafc;
            border-top: 1px solid var(--border-color);
        }
        .footer a {
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 500;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        .error-message {
            color: #c62828;
            background-color: #ffcdd2;
            border: 1px solid #ef9a9a;
            padding: 16px;
            border-radius: 8px;
            font-weight: 500;
            font-size: 1em;
        }
"""

CONTENT_TEMPLATE_MINDMAP = """
        <div class="mindmap-container-wrapper">
            <div class="user-context">
                <div class="title">{ui_title}</div>
                <div class="info-group">
                    <span><strong>{ui_user_label}:</strong> {user_name}</span>
                    <span><strong>{ui_time_label}:</strong> {current_date_time_str}</span>
                </div>
            </div>
            <div class="content-area">
                <div class="markmap-container" id="markmap-container-{unique_id}"></div>
                <div class="download-area">
                    <button id="locate-btn-{unique_id}" class="download-btn locate">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/></svg>
                        <span class="btn-text">{btn_locate}</span>
                    </button>
                    <button id="download-svg-btn-{unique_id}" class="download-btn">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                        <span class="btn-text">{btn_svg}</span>
                    </button>
                    <button id="download-md-btn-{unique_id}" class="download-btn secondary">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                        <span class="btn-text">{btn_md}</span>
                    </button>
                </div>
            </div>
            <div class="footer">
                <p>&copy; {current_year} {footer_text} &bull; <a href="https://markmap.js.org/" target="_blank">Markmap</a></p>
            </div>
        </div>
        
        <script type="text/template" id="markdown-source-{unique_id}">{markdown_syntax}</script>
"""

SCRIPT_TEMPLATE_MINDMAP = """
    <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
    <script src="https://cdn.jsdelivr.net/npm/markmap-lib@0.18"></script>
    <script src="https://cdn.jsdelivr.net/npm/markmap-view@0.18"></script>
    <script>
      (function() {
        const uniqueId = "{unique_id}";
        const maxRetries = 200;
        let retries = 0;
        const timeoutMsg = "{js_timeout}";
        const noContentMsg = "{js_no_content}";
        const renderFailMsg = "{js_render_fail}";
        const renderReasonLabel = "{js_render_reason}";

        const checkAndRender = () => {
            if (window.markmap && window.d3) {
                renderMindmap();
            } else if (retries < maxRetries) {
                retries++;
                setTimeout(checkAndRender, 150);
            } else {
                const containerEl = document.getElementById('markmap-container-' + uniqueId);
                if (containerEl) containerEl.innerHTML = '<div class="error-message">&#9888;&#65039; ' + timeoutMsg + '</div>';
            }
        };

        const renderMindmap = () => {
            const containerEl = document.getElementById('markmap-container-' + uniqueId);
            if (!containerEl || containerEl.dataset.markmapRendered) return;

            const sourceEl = document.getElementById('markdown-source-' + uniqueId);
            if (!sourceEl) return;

            const markdownContent = sourceEl.textContent.trim();
            if (!markdownContent) {
                containerEl.innerHTML = '<div class="error-message">&#9888;&#65039; ' + noContentMsg + '</div>';
                return;
            }

            try {
                const svgEl = document.createElementNS("http://www.w3.org/2000/svg", "svg");
                svgEl.style.width = '100%';
                svgEl.style.height = '100%'; 
                containerEl.innerHTML = ''; 
                containerEl.appendChild(svgEl);

                const { Transformer, Markmap } = window.markmap;
                const transformer = new Transformer();
                const { root } = transformer.transform(markdownContent);
                
                const style = (id) => `${id} text { font-size: 14px !important; }`;

                const options = { 
                    autoFit: false,
                    fitRatio: 0.85,
                    style: style,
                    duration: 300
                };
                const mm = Markmap.create(svgEl, options, root);
                
                d3.select(svgEl).on("dblclick.zoom", null);

                setTimeout(() => mm.fit(), 100);
                
                containerEl.dataset.markmapRendered = 'true';
                
                attachHandlers(uniqueId, mm);

            } catch (error) {
                console.error('Markmap rendering error:', error);
                containerEl.innerHTML = '<div class="error-message">&#9888;&#65039; ' + renderFailMsg + '<br>' + renderReasonLabel + ': ' + error.message + '</div>';
            }
        };

        const attachHandlers = (uniqueId, mm) => {
            const locateBtn = document.getElementById('locate-btn-' + uniqueId);
            const downloadSvgBtn = document.getElementById('download-svg-btn-' + uniqueId);
            const downloadMdBtn = document.getElementById('download-md-btn-' + uniqueId);
            const containerEl = document.getElementById('markmap-container-' + uniqueId);

            if (locateBtn) {
                locateBtn.addEventListener('click', (event) => {
                    event.stopPropagation();
                    mm.fit();
                });
            }

            const showFeedback = (button, isSuccess) => {
                const buttonText = button.querySelector('.btn-text');
                const originalText = buttonText.textContent;
                
                button.disabled = true;
                if (isSuccess) {
                    buttonText.textContent = '\u2705';
                    button.classList.add('copied');
                } else {
                    buttonText.textContent = '\u274c';
                }

                setTimeout(() => {
                    buttonText.textContent = originalText;
                    button.disabled = false;
                    button.classList.remove('copied');
                }, 2500);
            };

            const downloadFile = (content, filename, mimeType) => {
                try {
                    const dataUrl = 'data:' + mimeType + ';charset=utf-8,' + encodeURIComponent(content);
                    const a = document.createElement('a');
                    a.href = dataUrl;
                    a.download = filename;
                    a.style.display = 'none';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    return true;
                } catch (e) {
                    console.error('Download failed:', e);
                    return false;
                }
            };

            if (downloadSvgBtn) {
                downloadSvgBtn.addEventListener('click', (event) => {
                    event.stopPropagation();
                    const svgEl = containerEl.querySelector('svg');
                    if (svgEl) {
                        const svgData = new XMLSerializer().serializeToString(svgEl);
                        const success = downloadFile(svgData, 'mindmap.svg', 'image/svg+xml');
                        showFeedback(downloadSvgBtn, success);
                    }
                });
            }

            if (downloadMdBtn) {
                downloadMdBtn.addEventListener('click', (event) => {
                    event.stopPropagation();
                    const markdownContent = document.getElementById('markdown-source-' + uniqueId).textContent;
                    const success = downloadFile(markdownContent, 'mindmap.md', 'text/markdown');
                    showFeedback(downloadMdBtn, success);
                });
            }
        };

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', checkAndRender);
        } else {
            checkAndRender();
        }
      })();
    </script>
"""


class Action:
    class Valves(BaseModel):
        SHOW_STATUS: bool = Field(
            default=True,
            description="Show status updates in the chat interface. | 在聊天界面显示操作状态更新。",
        )
        MODEL_ID: str = Field(
            default="",
            description="LLM model ID for text analysis. Leave empty to use the current chat model. | 用于文本分析的LLM模型ID，为空则使用当前对话模型。",
        )
        MIN_TEXT_LENGTH: int = Field(
            default=100,
            description="Minimum text length (characters) required for mind map analysis. | 思维导图分析所需的最小文本长度（字符数）。",
        )
        CLEAR_PREVIOUS_HTML: bool = Field(
            default=False,
            description="Force clear previous plugin results (overwrite instead of merge). | 强制清除旧的结果，不合并直接覆盖。",
        )
        LANGUAGE: str = Field(
            default=LANG_ZH,
            description="Display language for the plugin UI and prompts. | 插件界面和提示语显示语言。",
            json_schema_extra={
                "input": {
                    "type": "select",
                    "options": [
                        {"value": LANG_ZH, "label": "中文"},
                        {"value": LANG_EN, "label": "English"},
                    ],
                }
            },
        )

    def __init__(self):
        self.valves = self.Valves()
        self.weekday_map_zh = {
            "Monday": "星期一", "Tuesday": "星期二", "Wednesday": "星期三",
            "Thursday": "星期四", "Friday": "星期五", "Saturday": "星期六", "Sunday": "星期日",
        }
        self.weekday_map_en = {
            "Monday": "Monday", "Tuesday": "Tuesday", "Wednesday": "Wednesday",
            "Thursday": "Thursday", "Friday": "Friday", "Saturday": "Saturday", "Sunday": "Sunday",
        }

    def _lang(self) -> str:
        lang = self.valves.LANGUAGE
        return lang if lang in I18N else LANG_ZH

    def _t(self, key: str, **kwargs) -> str:
        return t(self._lang(), key, **kwargs)

    def _extract_markdown_syntax(self, llm_output: str) -> str:
        match = re.search(r"```markdown\s*(.*?)\s*```", llm_output, re.DOTALL)
        if match:
            extracted_content = match.group(1).strip()
        else:
            logger.warning(self._t("log_llm_unexpected"))
            extracted_content = llm_output.strip()
        return extracted_content.replace("</script>", "<\\/script>")

    async def _emit_status(self, emitter, description: str, done: bool = False):
        if self.valves.SHOW_STATUS and emitter:
            await emitter(
                {"type": "status", "data": {"description": description, "done": done}}
            )

    async def _emit_notification(self, emitter, content: str, ntype: str = "info"):
        if emitter:
            await emitter(
                {"type": "notification", "data": {"type": ntype, "content": content}}
            )

    def _remove_existing_html(self, content: str) -> str:
        pattern = r"```html\s*<!-- OPENWEBUI_PLUGIN_OUTPUT -->[\s\S]*?```"
        return re.sub(pattern, "", content).strip()

    def _merge_html(
        self,
        existing_html_code: str,
        new_content: str,
        new_styles: str = "",
        new_scripts: str = "",
        user_locale: str = LANG_ZH,
    ) -> str:
        if (
            "<!-- OPENWEBUI_PLUGIN_OUTPUT -->" in existing_html_code
            and "<!-- CONTENT_INSERTION_POINT -->" in existing_html_code
        ):
            base_html = existing_html_code
            base_html = re.sub(r"^```html\s*", "", base_html)
            base_html = re.sub(r"\s*```$", "", base_html)
        else:
            base_html = HTML_WRAPPER_TEMPLATE.replace("{user_locale}", user_locale)

        wrapped_content = f'<div class="plugin-item">\n{new_content}\n</div>'

        if new_styles:
            base_html = base_html.replace(
                "/* STYLES_INSERTION_POINT */",
                f"{new_styles}\n/* STYLES_INSERTION_POINT */",
            )

        base_html = base_html.replace(
            "<!-- CONTENT_INSERTION_POINT -->",
            f"{wrapped_content}\n<!-- CONTENT_INSERTION_POINT -->",
        )

        if new_scripts:
            base_html = base_html.replace(
                "<!-- SCRIPTS_INSERTION_POINT -->",
                f"{new_scripts}\n<!-- SCRIPTS_INSERTION_POINT -->",
            )

        return base_html.strip()

    async def action(
        self,
        body: dict,
        __user__: Optional[Dict[str, Any]] = None,
        __event_emitter__: Optional[Any] = None,
        __request__: Optional[Request] = None,
    ) -> Optional[dict]:
        logger.info(self._t("log_started"))
        lang = self._lang()

        if isinstance(__user__, dict):
            user_locale = __user__.get("language", LANG_ZH)
            user_name = __user__.get("name", "User")
            user_id = __user__.get("id", "unknown_user")
        else:
            user_locale = LANG_ZH
            user_name = "User"
            user_id = "unknown_user"

        try:
            tz = pytz.timezone("Asia/Shanghai")
            now_tz = datetime.now(tz)
            current_date_time_str = now_tz.strftime(self._t("date_format"))
            current_weekday_en = now_tz.strftime("%A")
            weekday_map = self.weekday_map_zh if lang == LANG_ZH else self.weekday_map_en
            current_weekday = weekday_map.get(current_weekday_en, self._t("unknown_weekday"))
            current_year = now_tz.strftime("%Y")
            current_timezone_str = "Asia/Shanghai"
        except Exception as e:
            logger.warning(self._t("log_timezone_fail", error=str(e)))
            now = datetime.now()
            current_date_time_str = now.strftime(self._t("date_format"))
            current_weekday = self._t("unknown_weekday")
            current_year = now.strftime("%Y")
            current_timezone_str = self._t("unknown_tz")

        await self._emit_notification(
            __event_emitter__, self._t("notify_start"), "info"
        )

        messages = body.get("messages")
        if (
            not messages
            or not isinstance(messages, list)
            or not messages[-1].get("content")
        ):
            error_message = self._t("error_no_message")
            await self._emit_notification(__event_emitter__, error_message, "error")
            return {
                "messages": [{"role": "assistant", "content": f"\u274c {error_message}"}]
            }

        parts = re.split(r"```html.*?```", messages[-1]["content"], flags=re.DOTALL)
        long_text_content = ""
        if parts:
            for part in reversed(parts):
                if part.strip():
                    long_text_content = part.strip()
                    break

        if not long_text_content:
            long_text_content = messages[-1]["content"].strip()

        if len(long_text_content) < self.valves.MIN_TEXT_LENGTH:
            short_text_message = self._t(
                "error_short_text",
                len=str(len(long_text_content)),
                min=str(self.valves.MIN_TEXT_LENGTH),
            )
            await self._emit_notification(
                __event_emitter__, short_text_message, "warning"
            )
            return {
                "messages": [
                    {"role": "assistant", "content": f"\u26a0\ufe0f {short_text_message}"}
                ]
            }

        await self._emit_status(
            __event_emitter__, self._t("status_analyzing"), False
        )

        try:
            unique_id = f"id_{int(time.time() * 1000)}"

            prompt_system = self._t("prompt_system")
            prompt_user_template = self._t("prompt_user")

            formatted_user_prompt = prompt_user_template.format(
                user_name=user_name,
                current_date_time_str=current_date_time_str,
                current_weekday=current_weekday,
                current_timezone_str=current_timezone_str,
                user_locale=user_locale,
                long_text_content=long_text_content,
            )

            target_model = self.valves.MODEL_ID
            if not target_model:
                target_model = body.get("model")

            llm_payload = {
                "model": target_model,
                "messages": [
                    {"role": "system", "content": prompt_system},
                    {"role": "user", "content": formatted_user_prompt},
                ],
                "stream": False,
            }
            user_obj = await Users.get_user_by_id(user_id)
            if not user_obj:
                raise ValueError(self._t("error_user_not_found", user_id=user_id))

            llm_response = await generate_chat_completion(
                __request__, llm_payload, user_obj
            )

            if (
                not llm_response
                or "choices" not in llm_response
                or not llm_response["choices"]
            ):
                raise ValueError(self._t("error_llm_response"))

            assistant_response_content = llm_response["choices"][0]["message"][
                "content"
            ]
            markdown_syntax = self._extract_markdown_syntax(assistant_response_content)

            content_html = (
                CONTENT_TEMPLATE_MINDMAP
                .replace("{unique_id}", unique_id)
                .replace("{ui_title}", self._t("ui_title"))
                .replace("{ui_user_label}", self._t("ui_user"))
                .replace("{ui_time_label}", self._t("ui_time"))
                .replace("{user_name}", user_name)
                .replace("{current_date_time_str}", current_date_time_str)
                .replace("{current_year}", current_year)
                .replace("{btn_locate}", self._t("ui_btn_locate"))
                .replace("{btn_svg}", self._t("ui_btn_svg"))
                .replace("{btn_md}", self._t("ui_btn_md"))
                .replace("{footer_text}", self._t("ui_footer"))
                .replace("{markdown_syntax}", markdown_syntax)
            )

            script_html = (
                SCRIPT_TEMPLATE_MINDMAP
                .replace("{unique_id}", unique_id)
                .replace("{js_timeout}", self._t("js_timeout"))
                .replace("{js_no_content}", self._t("js_no_content"))
                .replace("{js_render_fail}", self._t("js_render_fail"))
                .replace("{js_render_reason}", self._t("js_render_reason"))
            )

            existing_html_block = ""
            match = re.search(
                r"```html\s*(<!-- OPENWEBUI_PLUGIN_OUTPUT -->[\s\S]*?)```",
                long_text_content,
            )
            if match:
                existing_html_block = match.group(1)

            if self.valves.CLEAR_PREVIOUS_HTML:
                long_text_content = self._remove_existing_html(long_text_content)
                final_html = self._merge_html(
                    "", content_html, CSS_TEMPLATE_MINDMAP, script_html, lang
                )
            else:
                if existing_html_block:
                    long_text_content = self._remove_existing_html(long_text_content)
                    final_html = self._merge_html(
                        existing_html_block,
                        content_html,
                        CSS_TEMPLATE_MINDMAP,
                        script_html,
                        lang,
                    )
                else:
                    final_html = self._merge_html(
                        "",
                        content_html,
                        CSS_TEMPLATE_MINDMAP,
                        script_html,
                        lang,
                    )

            html_embed_tag = f"```html\n{final_html}\n```"
            body["messages"][-1]["content"] = f"{long_text_content}\n\n{html_embed_tag}"

            await self._emit_status(__event_emitter__, self._t("status_done"), True)
            await self._emit_notification(
                __event_emitter__, self._t("notify_success", user_name=user_name), "success"
            )
            logger.info(self._t("log_completed"))

        except Exception as e:
            error_message = self._t("error_action", error=str(e))
            logger.error(error_message, exc_info=True)
            user_facing_error = self._t("error_generic", error=str(e))
            body["messages"][-1][
                "content"
            ] = f"{long_text_content}\n\n\u274c **Error:** {user_facing_error}"

            await self._emit_status(__event_emitter__, self._t("status_failed"), True)
            await self._emit_notification(
                __event_emitter__, self._t("notify_error", user_name=user_name), "error"
            )

        return body
