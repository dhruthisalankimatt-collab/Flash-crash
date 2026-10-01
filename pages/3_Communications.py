"""
pages/3_Communications.py
----------------------------
1-click communications console: status-page update, founder X/Twitter
statement, and templated support-macro dispatch. Simulated (no real
external APIs) but the full incident-response log and running timeline
are fully functional and stateful within the session.
"""

from datetime import datetime, timedelta

import streamlit as st

from engine.data_simulator import generate_market_data, generate_liquidation_events, generate_ticket_flood
from engine.risk_engine import compute_mark_price, summary_metrics
from engine.ui_theme import inject_css, page_header, NAVY, BLUE, GREEN, GRID, MUTED

st.set_page_config(page_title="Communications | Visionary Loop", page_icon="📣", layout="wide")
inject_css()


@st.cache_data(show_spinner=False)
def load_all_data():
    market = generate_market_data()
    mark = compute_mark_price(market)
    liquidations = generate_liquidation_events(market, mark, n_events=100)
    tickets = generate_ticket_flood(market)
    metrics = summary_metrics(liquidations)
    return metrics, int(tickets["cumulative_tickets"].max())


metrics, total_tickets = load_all_data()

if "incident_log" not in st.session_state:
    st.session_state.incident_log = []
if "status_published" not in st.session_state:
    st.session_state.status_published = False
if "founder_posted" not in st.session_state:
    st.session_state.founder_posted = False
if "macros_dispatched" not in st.session_state:
    st.session_state.macros_dispatched = False

INCIDENT_T0 = datetime(2024, 12, 5, 14, 0, 0)


def log_action(action: str):
    st.session_state.incident_log.append({"time": datetime.utcnow().strftime("%H:%M:%S"), "action": action})


page_header(
    "📣 1-Click Communications Console",
    "Pre-built templates surfaced the instant the breaker trips — collapsing the response window from 60 minutes to under 2.",
)

k1, k2, k3 = st.columns(3)
with k1:
    st.metric("T+20min PR Window (industry norm)", "60 min", help="Typical time-to-first-statement in a real venue flash crash.")
with k2:
    st.metric("Visionary Loop Time-to-Publish", "< 2 min", delta="-58 min", delta_color="normal")
with k3:
    st.metric("Inbound Tickets This Incident", f"{total_tickets:,}")

st.write("")
tab1, tab2, tab3 = st.tabs(["🌐 Status Page", "🐦 Founder Statement", "🎧 Support Macros"])

# ---------------------------------------------------------------------------
# TAB 1 — Status Page
# ---------------------------------------------------------------------------
with tab1:
    st.markdown("<div class='vl-section-title'>Status Page Update</div>", unsafe_allow_html=True)
    default_status = (
        f"**[Investigating] Elevated price deviation on BTC-PERP**\n\n"
        f"At {INCIDENT_T0.strftime('%H:%M UTC')} our monitoring systems detected a "
        f">5% deviation between the Last Traded Price and Index Price on BTC-PERP. "
        f"Our Circuit Breaker has automatically frozen new leveraged order entry on this pair.\n\n"
        f"- Existing positions are unaffected unless liquidation criteria under our Mark Price "
        f"methodology are met.\n"
        f"- Liquidations that occurred due to this dislocation are being reviewed under our "
        f"Abnormal Liquidation policy and may qualify for compensation from the Insurance Fund.\n"
        f"- We will post updates here every 10 minutes until resolved.\n\n"
        f"_Next update: {(INCIDENT_T0 + timedelta(minutes=10)).strftime('%H:%M UTC')}_"
    )
    status_text = st.text_area("Editable template", value=default_status, height=260, key="status_text")
    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("🚀 Publish Status Page", type="primary", use_container_width=True):
            st.session_state.status_published = True
            log_action("Status page published (Investigating)")
    with c2:
        if st.session_state.status_published:
            st.success(f"Published live at statuspage.mochatrade.io — {datetime.utcnow().strftime('%H:%M:%S')} UTC")

# ---------------------------------------------------------------------------
# TAB 2 — Founder Statement
# ---------------------------------------------------------------------------
with tab2:
    st.markdown("<div class='vl-section-title'>Founder X (Twitter) Post</div>", unsafe_allow_html=True)
    default_post = (
        "We saw the BTC-PERP price dislocation. Our Circuit Breaker tripped automatically and froze new "
        "leverage within seconds — no manual intervention needed.\n\n"
        "Every liquidation from this event is being triaged: real moves stand, glitch-driven ones are "
        "being reimbursed from our $250,000 Insurance Fund. Full breakdown incoming on our status page.\n\n"
        "We'll share the post-mortem within 24h. Appreciate the patience. 🛡️"
    )
    post_text = st.text_area("Editable draft", value=default_post, height=200, key="founder_text")
    st.caption(f"{len(post_text)} characters")
    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("🚀 Post Founder Statement", type="primary", use_container_width=True):
            st.session_state.founder_posted = True
            log_action("Founder statement posted publicly")
    with c2:
        if st.session_state.founder_posted:
            st.success(f"Posted — {datetime.utcnow().strftime('%H:%M:%S')} UTC")

# ---------------------------------------------------------------------------
# TAB 3 — Support Macros
# ---------------------------------------------------------------------------
with tab3:
    st.markdown("<div class='vl-section-title'>Templated Support Macros</div>", unsafe_allow_html=True)
    macro_choice = st.selectbox(
        "Select macro to preview / dispatch",
        [
            "Liquidation reviewed as NORMAL (loss stands)",
            "Liquidation reviewed as ABNORMAL (compensation issued)",
            "General inquiry — circuit breaker explainer",
        ],
    )
    macros = {
        "Liquidation reviewed as NORMAL (loss stands)": (
            "Hi {{user}}, thanks for reaching out. We reviewed your liquidation on BTC-PERP against our "
            "Mark Price methodology at the time of the event. The deviation was within our 5% threshold, "
            "meaning this reflected a genuine market move rather than a pricing glitch. Per our terms, "
            "this liquidation stands. You can view the full calculation on your Triage Ledger receipt."
        ),
        "Liquidation reviewed as ABNORMAL (compensation issued)": (
            "Hi {{user}}, good news — we reviewed your liquidation on BTC-PERP and confirmed it was "
            "triggered by a >5% deviation between Mark Price and Index Price during a temporary venue "
            "dislocation. This has been reclassified as an Abnormal Liquidation. A compensation payout "
            "has been issued from our Insurance Fund and will reflect in your account within minutes."
        ),
        "General inquiry — circuit breaker explainer": (
            "Hi {{user}}, you may have noticed new leveraged orders were briefly frozen on BTC-PERP. "
            "This was our automatic Circuit Breaker, which pauses new leverage whenever Mark Price "
            "deviates more than 5% from Index Price. It resets automatically once prices normalize — "
            "no action is needed on your end."
        ),
    }
    st.text_area("Macro preview", value=macros[macro_choice], height=160, key="macro_preview")
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        ticket_volume = st.number_input("Tickets to auto-tag with this macro", min_value=1, max_value=5000, value=250, step=50)
    with c2:
        st.write("")
        if st.button("🎧 Dispatch Macro", type="primary", use_container_width=True):
            st.session_state.macros_dispatched = True
            log_action(f"Dispatched macro '{macro_choice}' to {ticket_volume} tickets")
    with c3:
        if st.session_state.macros_dispatched:
            st.success(f"Auto-tagged and sent to {ticket_volume} matching tickets — {datetime.utcnow().strftime('%H:%M:%S')} UTC")

# ---------------------------------------------------------------------------
# Running incident log
# ---------------------------------------------------------------------------
st.write("")
st.markdown("<div class='vl-section-title'>Running Incident Log</div>", unsafe_allow_html=True)
if not st.session_state.incident_log:
    st.info("No communications actions taken yet this session. Publish the status page, founder statement, or dispatch a macro above.")
else:
    for entry in reversed(st.session_state.incident_log):
        st.markdown(
            f"<div class='vl-card' style='margin-bottom:8px; padding:10px 16px;'>"
            f"<span style='color:{MUTED}; font-weight:600;'>{entry['time']} UTC</span> — {entry['action']}"
            f"</div>",
            unsafe_allow_html=True,
        )
    if st.button("🗑️ Clear log"):
        st.session_state.incident_log = []
        st.rerun()
