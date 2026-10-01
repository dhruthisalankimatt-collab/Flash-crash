"""
engine/ui_theme.py
--------------------
Shared light-mode institutional styling + small helpers reused across
app.py and every page, so all three screens look like one coherent
terminal instead of three different Streamlit demos.
"""

import streamlit as st

NAVY = "#0B1F3A"
BLUE = "#0B5FFF"
LIGHT_BLUE = "#E8F0FE"
GREEN = "#1A8754"
LIGHT_GREEN = "#E7F6ED"
RED = "#D93025"
LIGHT_RED = "#FDECEA"
AMBER = "#B36B00"
LIGHT_AMBER = "#FFF4E0"
GRID = "#E3E7EE"
INK = "#12161C"
MUTED = "#5B6472"
CARD_BG = "#FFFFFF"
PAGE_BG = "#F7F9FC"

CUSTOM_CSS = f"""
<style>
    .stApp {{
        background-color: {PAGE_BG};
    }}
    div[data-testid="stMetric"] {{
        background-color: {CARD_BG};
        border: 1px solid {GRID};
        border-radius: 10px;
        padding: 14px 16px 10px 16px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
    }}
    div[data-testid="stMetricLabel"] {{
        color: {MUTED};
        font-weight: 600;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        font-size: 0.72rem;
    }}
    div[data-testid="stMetricValue"] {{
        color: {NAVY};
        font-weight: 700;
    }}
    .vl-banner {{
        border-radius: 10px;
        padding: 14px 18px;
        font-weight: 700;
        font-size: 1.05rem;
        border: 1px solid transparent;
        margin-bottom: 0.6rem;
    }}
    .vl-banner-ok {{
        background-color: {LIGHT_GREEN};
        color: {GREEN};
        border-color: #BFE6CC;
    }}
    .vl-banner-tripped {{
        background-color: {LIGHT_RED};
        color: {RED};
        border-color: #F5C2BE;
    }}
    .vl-pill {{
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }}
    .vl-pill-normal {{
        background-color: {LIGHT_GREEN};
        color: {GREEN};
    }}
    .vl-pill-abnormal {{
        background-color: {LIGHT_RED};
        color: {RED};
    }}
    .vl-section-title {{
        color: {NAVY};
        font-weight: 700;
        font-size: 1.15rem;
        margin-top: 0.4rem;
        margin-bottom: 0.2rem;
    }}
    .vl-caption {{
        color: {MUTED};
        font-size: 0.85rem;
    }}
    .vl-card {{
        background-color: {CARD_BG};
        border: 1px solid {GRID};
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
    }}
    section[data-testid="stSidebar"] {{
        background-color: #FFFFFF;
        border-right: 1px solid {GRID};
    }}
    footer {{visibility: hidden;}}
</style>
"""


def inject_css() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div style="display:flex; align-items:baseline; gap:12px; margin-bottom:2px;">
            <span style="font-size:1.55rem; font-weight:800; color:{NAVY};">{title}</span>
            <span style="font-size:0.85rem; color:{MUTED}; font-weight:600;">VISIONARY LOOP · MOCHATRADE FLASH-CRASH DESK</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(f"<div class='vl-caption'>{subtitle}</div>", unsafe_allow_html=True)
    st.write("")


def status_banner(tripped: bool, deviation_pct: float) -> None:
    if tripped:
        st.markdown(
            f"""<div class="vl-banner vl-banner-tripped">
                🔴 CIRCUIT BREAKER: TRIPPED — new leverage frozen · live deviation {deviation_pct:+.2f}%
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""<div class="vl-banner vl-banner-ok">
                🟢 CIRCUIT BREAKER: ARMED — market within 5% band · live deviation {deviation_pct:+.2f}%
            </div>""",
            unsafe_allow_html=True,
        )


def tag_pill(tag: str) -> str:
    cls = "vl-pill-abnormal" if tag == "ABNORMAL" else "vl-pill-normal"
    return f"<span class='vl-pill {cls}'>{tag}</span>"
