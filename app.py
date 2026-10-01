"""
app.py
-------
Visionary Loop — MochaTrade Flash-Crash Incident Response Desk
Main entry point. Streamlit auto-discovers pages/ for sidebar navigation:
    1_Live_Crisis_Monitor.py
    2_Triage_Ledger.py
    3_Communications.py

Run locally:    streamlit run app.py
Deploy:         Streamlit Community Cloud (see README.md)
"""

import streamlit as st

from engine.data_simulator import generate_market_data, generate_liquidation_events, generate_ticket_flood
from engine.risk_engine import compute_mark_price, summary_metrics, breaker_events
from engine.ui_theme import inject_css, page_header, NAVY, MUTED

st.set_page_config(
    page_title="Visionary Loop | MochaTrade Incident Desk",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()


@st.cache_data(show_spinner=False)
def load_all_data():
    market = generate_market_data()
    mark = compute_mark_price(market)
    liquidations = generate_liquidation_events(market, mark, n_events=100)
    tickets = generate_ticket_flood(market)
    breakers = breaker_events(mark)
    metrics = summary_metrics(liquidations)
    return market, mark, liquidations, tickets, breakers, metrics


market_df, mark_df, liq_df, ticket_df, breaker_df, metrics = load_all_data()

with st.sidebar:
    st.markdown(
        f"<div style='font-weight:800; font-size:1.15rem; color:{NAVY};'>🛡️ Visionary Loop</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='color:{MUTED}; font-size:0.82rem; margin-bottom:14px;'>"
        "MochaTrade Flash-Crash Simulation · ACM MarketSphere 2026 · Track 3</div>",
        unsafe_allow_html=True,
    )
    st.caption("Navigate using the pages above ⬆️")
    st.divider()
    st.markdown("**Incident window**")
    st.caption("Dec 5, 2024 · 13:45 – 15:15 UTC (synthetic replay)")
    st.markdown("**Fund**")
    st.caption(f"Insurance Fund start: ${metrics['insurance_fund_start_usd']:,.0f}")

page_header(
    "Incident Response Command Center",
    "A single desk to detect, triage, and communicate through a venue-level flash crash — "
    "built for the Dec 2024 BTC dislocation scenario.",
)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric(
        "Forced-Liquidation Reduction",
        f"{metrics['forced_liquidation_reduction_pct']:.0f}%",
        help="Liquidation attempts blocked by the median mark-price engine vs. a naive last-price-only engine.",
    )
with col2:
    st.metric(
        "Avg Detection Latency",
        f"{metrics['avg_detection_latency_ms']:.0f} ms",
        help=f"Max observed: {metrics['max_detection_latency_ms']:.0f} ms — target sub-900ms.",
    )
with col3:
    st.metric(
        "Insurance Fund Remaining",
        f"${metrics['insurance_fund_remaining_usd']:,.0f}",
        delta=f"-${metrics['total_insurance_payout_usd']:,.0f}",
        delta_color="inverse",
    )
with col4:
    st.metric("Liquidation Attempts", f"{metrics['total_liquidation_attempts']}")
with col5:
    st.metric(
        "Circuit Breaker Trips",
        f"{(breaker_df['event'] == 'CIRCUIT BREAKER TRIPPED').sum()}",
        help="Number of distinct times the 5% band was breached during the incident window.",
    )

st.write("")
st.markdown("---")

left, right = st.columns([1.3, 1])
with left:
    st.markdown("<div class='vl-section-title'>What this desk proves</div>", unsafe_allow_html=True)
    st.markdown(
        """
- **Mark Price Engine** — `Median(Index, Index + 5-min Basis MA, Last Traded)` absorbs single-venue
  glitches instead of liquidating users off a corrupted last-traded print.
- **Circuit Breaker** — auto-freezes new leverage the instant `|Mark − Index| / Index` exceeds **5%**.
- **Triage Ledger** — every liquidation attempt is tagged **NORMAL** (real move, user absorbs it) or
  **ABNORMAL** (glitch/slippage, paid from the **$250,000 Insurance Fund**) — no discretion, no delay.
- **Communications Console** — status page, founder statement, and support macros are pre-drafted and
  fire the moment the breaker trips, collapsing the response window from 60 minutes to under 2.
        """
    )
with right:
    st.markdown("<div class='vl-section-title'>Where to go next</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="vl-card">
        <b>1. Live Crisis Monitor</b><br><span class="vl-caption">Index vs. Last vs. Mark price, deviation band, breaker trips, ticket flood.</span>
        <hr style="margin:10px 0; border-color:#E3E7EE;">
        <b>2. Triage Ledger</b><br><span class="vl-caption">Every liquidation attempt, Normal vs. Abnormal, Insurance Fund balance over time.</span>
        <hr style="margin:10px 0; border-color:#E3E7EE;">
        <b>3. Communications</b><br><span class="vl-caption">One-click status page, founder statement, and support macro dispatch.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
st.caption(
    "All market, liquidation, and ticket data on this desk is synthetically generated to reproduce the "
    "shape and headline metrics of the Dec 2024 BTC flash-crash scenario for demo purposes."
)
