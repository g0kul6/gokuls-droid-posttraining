"""Sphinx configuration for the public DROID post-training guide."""

from __future__ import annotations

import os

project = "Gokul's DROID Post-Training Setup"
author = "Gokul and contributors"
copyright = "2026, Gokul and contributors"  # noqa: A001 - Sphinx setting name
release = "0.1"

extensions = [
    "myst_parser",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx_design",
    "sphinxcontrib.mermaid",
]

source_suffix = {".md": "markdown"}
master_doc = "index"
exclude_patterns = ["_build", "_dist", ".venv", "README.md"]

myst_heading_anchors = 4
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "substitution",
    "tasklist",
]

html_theme = "furo"
html_title = project
html_baseurl = os.environ.get("DOCS_BASE_URL", "")
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_theme_options = {
    "navigation_with_keys": True,
    "sidebar_hide_name": False,
    "light_css_variables": {
        "color-brand-primary": "#245c4f",
        "color-brand-content": "#245c4f",
    },
    "dark_css_variables": {
        "color-brand-primary": "#8ee0c2",
        "color-brand-content": "#8ee0c2",
    },
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

extlinks = {
    "robometer": (
        "https://github.com/robometer/robometer/%s",
        "robometer/%s",
    ),
    "rpl": (
        "https://github.com/robometer/robometer-policy-learning/%s",
        "robometer-policy-learning/%s",
    ),
    "expo": (
        "https://github.com/pd-perry/expo-ft/%s",
        "expo-ft/%s",
    ),
}

mermaid_version = "11.4.1"
mermaid_init_js = "mermaid.initialize({startOnLoad:true, securityLevel:'strict'});"

nitpicky = True
suppress_warnings = [
    # External code links are intentionally ordinary URLs rather than Python
    # API references.
    "myst.xref_missing",
]
