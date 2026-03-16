"""
styles.py
Globalne style CSS dla aplikacji ScanMyDoc.
Wywołaj inject_styles() raz na początku app.py, po st.set_page_config().
"""

import streamlit as st

# Paleta kolorów KarmelCodeLab — zmień tutaj, zmiany propagują się wszędzie
COLORS = {
    "bg":       "#12131a",
    "surface":  "#1a1d2b",
    "surface2": "#21202e",
    "border":   "#3a2e1e",
    "accent":   "#f5960a",
    "accent2":  "#e8c27a",
    "success":  "#c8832a",
    "text":     "#f0e6d3",
    "muted":    "#8a7560",
}

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:        %(bg)s;
    --surface:   %(surface)s;
    --surface2:  %(surface2)s;
    --border:    %(border)s;
    --accent:    %(accent)s;
    --accent2:   %(accent2)s;
    --success:   %(success)s;
    --text:      %(text)s;
    --muted:     %(muted)s;
    --mono:      'Space Mono', monospace;
    --sans:      'DM Sans', sans-serif;
}

/* ── BASE ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
.main .block-container {
    padding: 2rem 3rem 4rem 3rem !important;
    max-width: 1200px !important;
}

/* ── HERO ── */
.hero-wrap {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding: 2rem 2.5rem;
    background: linear-gradient(135deg, #1a1d2b 0%%, #16141f 60%%, #110e18 100%%);
    border: 1px solid var(--border);
    border-radius: 16px;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-wrap::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 80%% 50%%, rgba(245,150,10,.10) 0%%, transparent 65%%);
    pointer-events: none;
}
.hero-badge {
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: .15em;
    color: var(--accent);
    background: rgba(245,150,10,.12);
    border: 1px solid rgba(245,150,10,.35);
    border-radius: 4px;
    padding: 3px 8px;
    display: inline-block;
    margin-bottom: .4rem;
    text-transform: uppercase;
}
.hero-title {
    font-family: var(--mono) !important;
    font-size: 2.8rem !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    letter-spacing: -.02em;
    line-height: 1.1;
    margin: 0 0 .25rem 0;
}
.hero-title span { color: var(--accent); }
.hero-sub {
    font-family: var(--sans);
    font-size: 1rem;
    font-weight: 300;
    color: var(--muted);
    margin: 0;
}
.hero-line {
    width: 2px;
    height: 70px;
    background: linear-gradient(180deg, transparent, var(--accent), transparent);
    border-radius: 2px;
    flex-shrink: 0;
}

/* ── TABS ── */
[data-testid="stTabs"] > div:first-child {
    border-bottom: 1px solid var(--border) !important;
    gap: .25rem;
    margin-bottom: 1.5rem;
}
button[data-baseweb="tab"] {
    font-family: var(--mono) !important;
    font-size: .78rem !important;
    letter-spacing: .08em !important;
    color: var(--muted) !important;
    background: transparent !important;
    border: none !important;
    padding: .6rem 1.2rem !important;
    text-transform: uppercase;
    transition: color .2s;
}
button[data-baseweb="tab"]:hover { color: var(--text) !important; }
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}

/* ── CARD LABEL ── */
.card-label {
    font-family: var(--mono);
    font-size: .68rem;
    letter-spacing: .12em;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: .75rem;
    display: flex;
    align-items: center;
    gap: .5rem;
}
.card-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── SLIDERS ── */
[data-testid="stSlider"] > div > div > div > div {
    background: var(--accent) !important;
}
[data-testid="stSlider"] label {
    font-family: var(--mono) !important;
    font-size: .72rem !important;
    color: var(--muted) !important;
    letter-spacing: .05em;
    text-transform: uppercase;
}

/* ── RADIO ── */
[data-testid="stRadio"] label {
    font-family: var(--sans) !important;
    color: var(--text) !important;
    font-size: .9rem !important;
}
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
    font-family: var(--mono) !important;
    font-size: .7rem !important;
    color: var(--muted) !important;
    letter-spacing: .08em;
    text-transform: uppercase;
    margin-bottom: .4rem;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    background: var(--surface2) !important;
    border: 1px dashed var(--border) !important;
    border-radius: 10px !important;
    transition: border-color .2s;
}
[data-testid="stFileUploader"]:hover { border-color: var(--accent) !important; }
[data-testid="stFileUploader"] label {
    font-family: var(--mono) !important;
    font-size: .72rem !important;
    color: var(--muted) !important;
    letter-spacing: .06em;
    text-transform: uppercase;
}
[data-testid="stFileUploaderDropzoneInstructions"] p {
    color: var(--muted) !important;
    font-family: var(--sans) !important;
}

/* ── BUTTONS ── */
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-secondary"] {
    font-family: var(--mono) !important;
    font-size: .75rem !important;
    letter-spacing: .1em !important;
    text-transform: uppercase !important;
    border-radius: 8px !important;
    padding: .55rem 1.4rem !important;
    transition: all .2s !important;
}
[data-testid="stBaseButton-primary"] {
    background: var(--accent) !important;
    color: #1a0f00 !important;
    border: none !important;
    box-shadow: 0 0 20px rgba(245,150,10,.25);
}
[data-testid="stBaseButton-primary"]:hover {
    background: var(--accent2) !important;
    box-shadow: 0 0 28px rgba(245,150,10,.45) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stBaseButton-secondary"] {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}
[data-testid="stBaseButton-secondary"]:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

/* ── DOWNLOAD BUTTON ── */
[data-testid="stDownloadButton"] button {
    font-family: var(--mono) !important;
    font-size: .75rem !important;
    letter-spacing: .1em !important;
    text-transform: uppercase !important;
    background: linear-gradient(135deg, #2a1a0a, #1e1008) !important;
    color: var(--accent) !important;
    border: 1px solid rgba(245,150,10,.35) !important;
    border-radius: 8px !important;
    padding: .6rem 1.6rem !important;
    box-shadow: 0 0 16px rgba(245,150,10,.12);
    transition: all .2s !important;
    width: 100%%;
}
[data-testid="stDownloadButton"] button:hover {
    border-color: var(--accent) !important;
    box-shadow: 0 0 24px rgba(245,150,10,.30) !important;
    transform: translateY(-1px) !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    background: var(--surface2) !important;
    border-radius: 10px !important;
    border-left: 3px solid var(--accent) !important;
    font-family: var(--sans) !important;
    font-size: .88rem !important;
}

/* ── CAPTION ── */
[data-testid="stCaptionContainer"] p {
    font-family: var(--mono) !important;
    font-size: .65rem !important;
    color: var(--muted) !important;
    letter-spacing: .05em;
}

/* ── TEXT INPUT ── */
[data-testid="stTextInput"] input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
    font-size: .82rem !important;
    transition: border-color .2s;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(245,150,10,.15) !important;
}
[data-testid="stTextInput"] label {
    font-family: var(--mono) !important;
    font-size: .68rem !important;
    color: var(--muted) !important;
    letter-spacing: .08em;
    text-transform: uppercase;
}

/* ── IMAGES ── */
[data-testid="stImage"] img {
    border-radius: 10px;
    border: 1px solid var(--border);
}

/* ── PREVIEW LABEL ── */
.preview-label {
    font-family: var(--mono);
    font-size: .65rem;
    letter-spacing: .12em;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: .4rem;
    padding: .2rem .6rem;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 4px;
    display: inline-block;
}

/* ── FILE LIST ── */
.file-list-item {
    display: flex;
    align-items: center;
    gap: .75rem;
    padding: .6rem 1rem;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: .4rem;
    font-family: var(--mono);
    font-size: .75rem;
    color: var(--text);
}
.file-idx {
    font-family: var(--mono);
    font-size: .65rem;
    color: var(--accent);
    background: rgba(245,150,10,.12);
    border: 1px solid rgba(245,150,10,.30);
    border-radius: 4px;
    padding: 1px 7px;
    min-width: 26px;
    text-align: center;
}

/* ── DIVIDER ── */
hr { border-color: var(--border) !important; margin: 1.25rem 0 !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }
"""


def inject_styles() -> None:
    """Wstrzykuje globalne style CSS do aplikacji Streamlit."""
    st.markdown(f"<style>{_CSS % COLORS}</style>", unsafe_allow_html=True)
