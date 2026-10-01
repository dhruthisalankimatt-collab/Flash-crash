"""
pages/2_Triage_Ledger.py
---------------------------
Liquidation triage ledger: Normal vs. Abnormal tagging, Insurance Fund
balance over time, and the deterministic 41% forced-liquidation
reduction headline metric.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from engine.data_simulator import generate_market_data, generate_liquidation_events
from engine.risk_engine import compute_mark_price, summary_metrics, insurance_fund_ledger
from engine.ui_theme import inject_css, page_header, tag_pill, NAVY, BLUE, RED, GREEN, GRID, MUTED, LIGHT_RED, LIGHT_GREEN

st.set_page_config(page_title="Triage Ledger | Visionary Loop", page_icon="⚖️", layout="wide")
inject_css()


@st.cache_data(show_spinner=False)
def load_all_data():
    market = generate_market_data()
    mark = compute_mark_price(market)
    liquidations = generate_liquidation_events(market, mark, n_events=100)
    metrics = summary_metrics(liquidations)
    ledger = insurance_fund_ledger(liquidations)
    return market, mark, liquidations, metrics, ledger


market_df, mark_df, liq_df, metrics, ledger_df = load_all_data()

page_header(
    "⚖️ Triage & Insurance Ledger",
    "Every liquidation attempt classified NORMAL (user absorbs) or ABNORMAL (glitch — paid from the Insurance Fund).",
)

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric("Total Liquidation Attempts", metrics["total_liquidation_attempts"])
with k2:
    st.metric("Forced (NORMAL)", metrics["actual_forced_liquidations"], help="Real moves — liquidation stands, user absorbs the loss.")
with k3:
    st.metric("Blocked (ABNORMAL)", metrics["abnormal_blocked_count"], help="Glitch/slippage — liquidation blocked, user compensated.")
with k4:
    st.metric("Forced-Liquidation Reduction", f"{metrics['forced_liquidation_reduction_pct']:.0f}%",
               help="vs. a naive engine that liquidates purely off last-traded price.")
with k5:
    st.metric("Insurance Fund Remaining", f"${metrics['insurance_fund_remaining_usd']:,.0f}",
               delta=f"-${metrics['total_insurance_payout_usd']:,.0f} paid out", delta_color="inverse")

st.write("")
left, right = st.columns([1, 1])

with left:
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=["Naive engine\n(last-price only)", "Visionary Loop\n(mark-price engine)"],
        y=[metrics["naive_forced_liquidations"] + metrics["abnormal_blocked_count"], metrics["actual_forced_liquidations"]],
        marker_color=[RED, GREEN],
        text=[metrics["naive_forced_liquidations"] + metrics["abnormal_blocked_count"], metrics["actual_forced_liquidations"]],
        textposition="outside",
        width=[0.5, 0.5],
    ))
    fig_bar.update_layout(
        title=f"Forced Liquidations: Naive vs. Visionary Loop (−{metrics['forced_liquidation_reduction_pct']:.0f}%)",
        height=360, plot_bgcolor="white", paper_bgcolor="white", font=dict(color=NAVY),
        yaxis=dict(title="Forced liquidations", gridcolor=GRID), xaxis=dict(gridcolor=GRID),
        margin=dict(l=10, r=10, t=60, b=10), showlegend=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with right:
    fig_fund = go.Figure()
    fig_fund.add_trace(go.Scatter(
        x=ledger_df["t_minute"], y=ledger_df["fund_balance_after"],
        mode="lines+markers", line=dict(color=BLUE, width=2.5), marker=dict(size=5),
        name="Fund balance",
    ))
    fig_fund.add_hline(y=0, line=dict(color=RED, width=1.5, dash="dash"))
    fig_fund.update_layout(
        title="Insurance Fund Balance Over Time ($250,000 start)",
        height=360, plot_bgcolor="white", paper_bgcolor="white", font=dict(color=NAVY),
        xaxis=dict(title="Minutes relative to T=0", gridcolor=GRID),
        yaxis=dict(title="Balance (USD)", gridcolor=GRID, tickformat=",.0f"),
        margin=dict(l=10, r=10, t=60, b=10), showlegend=False,
    )
    st.plotly_chart(fig_fund, use_container_width=True)

st.write("")
st.markdown("<div class='vl-section-title'>Liquidation Event Ledger</div>", unsafe_allow_html=True)

filt_col1, filt_col2, filt_col3 = st.columns([1, 1, 2])
with filt_col1:
    tag_filter = st.multiselect("Filter by tag", options=["NORMAL", "ABNORMAL"], default=["NORMAL", "ABNORMAL"])
with filt_col2:
    side_filter = st.multiselect("Filter by side", options=["LONG", "SHORT"], default=["LONG", "SHORT"])
with filt_col3:
    search_uid = st.text_input("Search user ID (e.g. UID-20014)", value="")

filtered = liq_df[liq_df["tag"].isin(tag_filter) & liq_df["side"].isin(side_filter)]
if search_uid.strip():
    filtered = filtered[filtered["user_id"].str.contains(search_uid.strip(), case=False)]

display_df = filtered.copy()
display_df["timestamp"] = display_df["timestamp"].dt.strftime("%H:%M:%S")
display_df["position_size_usd"] = display_df["position_size_usd"].map(lambda v: f"${v:,.0f}")
display_df["liquidation_ref_price"] = display_df["liquidation_ref_price"].map(lambda v: f"${v:,.0f}")
display_df["index_price_at_event"] = display_df["index_price_at_event"].map(lambda v: f"${v:,.0f}")
display_df["mark_price_at_event"] = display_df["mark_price_at_event"].map(lambda v: f"${v:,.0f}")
display_df["deviation_pct"] = display_df["deviation_pct"].map(lambda v: f"{v:+.2f}%")
display_df["detection_latency_ms"] = display_df["detection_latency_ms"].map(lambda v: f"{v:.0f} ms")
display_df["insurance_payout_usd"] = display_df["insurance_payout_usd"].map(lambda v: f"${v:,.0f}" if v > 0 else "—")

display_df = display_df.rename(columns={
    "event_id": "Event",
    "timestamp": "Time (UTC)",
    "user_id": "User",
    "side": "Side",
    "position_size_usd": "Position Size",
    "liquidation_ref_price": "Ref Price",
    "index_price_at_event": "Index Price",
    "mark_price_at_event": "Mark Price",
    "deviation_pct": "Deviation",
    "tag": "Tag",
    "detection_latency_ms": "Detection Latency",
    "insurance_payout_usd": "Insurance Payout",
})[[
    "Event", "Time (UTC)", "User", "Side", "Position Size", "Ref Price", "Index Price",
    "Mark Price", "Deviation", "Tag", "Detection Latency", "Insurance Payout",
]]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    height=430,
    column_config={
        "Tag": st.column_config.TextColumn("Tag", help="NORMAL = user absorbs. ABNORMAL = insurance fund pays."),
    },
)
st.caption(f"Showing {len(display_df)} of {len(liq_df)} total liquidation attempts.")

st.write("")
st.markdown("<div class='vl-section-title'>Decision Checklist (per event)</div>", unsafe_allow_html=True)
st.markdown(
    """
    <div class="vl-card">
    <ol>
      <li>Compute <b>Mark Price</b> = Median(Index, Index + 5-min Basis MA, Last Traded) at time of liquidation trigger.</li>
      <li>Compute <b>Deviation %</b> = (Mark − Index) / Index.</li>
      <li>If |Deviation| ≤ 5% → tag <b>NORMAL</b>, liquidation proceeds, user absorbs the loss.</li>
      <li>If |Deviation| &gt; 5% → tag <b>ABNORMAL</b>, forced liquidation is <b>blocked</b>, position is held.</li>
      <li>Compute slippage vs. fair mark price → pay out from the <b>Insurance Fund</b> (capped at 35% of position size).</li>
      <li>Log event, latency, and fund balance to this ledger — no manual override, fully auditable.</li>
    </ol>
    </div>
    """,
    unsafe_allow_html=True,
)
