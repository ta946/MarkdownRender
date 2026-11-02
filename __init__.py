import os
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), "static")

STATIC_FILES_MAP = {
    "template": "template.html",
    "mermaidjs": "mermaid.min.js",
    "md_mermaid": "markdown_mermaid.js",
    "md_css": "markdown.css",
    "md_css_dark": "github-markdown-dark.css",
}

__all__ = [
    "STATIC_FOLDER",
    "STATIC_FILES_MAP",
]