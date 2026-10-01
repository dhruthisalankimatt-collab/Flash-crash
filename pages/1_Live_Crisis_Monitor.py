"""
pages/1_Live_Crisis_Monitor.py
--------------------------------
Live/simulated market feed + circuit breaker visualization.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from engine.data_simulator import generate_market_data, generate_liquidation_events, generate_ticket_flood
from engine.risk_engine import compute_mark_price, breaker_events, summary_metrics, CIRCUIT_BREAKER_THRESHOLD
from engine.ui_theme import inject_css, page_header, status_banner, NAVY, BLUE, RED, GREEN, AMBER, GRID, MUTED

st.set_page_config(page_title="Live Crisis Monitor | Visionary Loop", page_icon="📡", layout="wide")
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

page_header(
    "📡 Live Crisis Monitor",
    "Index Price vs. Last Traded Price vs. Mark Price — 5% circuit-breaker band, live deviation, and inbound-ticket flood.",
)

# ---------------------------------------------------------------------------
# Time-travel scrubber — lets the presenter "play" the incident live
# ---------------------------------------------------------------------------
max_minute = float(mark_df["t_minute"].max())
min_minute = float(mark_df["t_minute"].min())

scrub_col, btn_col = st.columns([5, 1])
with scrub_col:
    current_minute = st.slider(
        "⏱️ Scrub the incident timeline (minutes relative to crash trigger, T = 0)",
        min_value=min_minute,
        max_value=max_minute,
        value=6.0,
        step=0.5,
        format="T%+.1f min",
    )
with btn_col:
    st.write("")
    if st.button("⏮ Reset to T+0", use_container_width=True):
        st.rerun()

snapshot_idx = (mark_df["t_minute"] - current_minute).abs().idxmin()
snapshot = mark_df.loc[snapshot_idx]

status_banner(bool(snapshot["breaker_tripped"]), float(snapshot["deviation_pct"] * 100))

# ---------------------------------------------------------------------------
# KPI row at the scrubbed point in time
# ---------------------------------------------------------------------------
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric("Index Price", f"${snapshot['index_price']:,.0f}")
with k2:
    delta_last = snapshot["last_price"] - snapshot["index_price"]
    st.metric("Last Traded Price", f"${snapshot['last_price']:,.0f}", delta=f"{delta_last:,.0f} vs index", delta_color="inverse")
with k3:
    delta_mark = snapshot["mark_price"] - snapshot["index_price"]
    st.metric("Mark Price", f"${snapshot['mark_price']:,.0f}", delta=f"{delta_mark:,.0f} vs index", delta_color="inverse")
with k4:
    st.metric("Live Deviation", f"{snapshot['deviation_pct']*100:+.2f}%", help="(Mark − Index) / Index. Breaker trips beyond ±5%.")
with k5:
    liq_so_far = int((liq_df["t_minute"] <= current_minute).sum())
    st.metric("Liquidation Attempts So Far", f"{liq_so_far}")

st.write("")

# ---------------------------------------------------------------------------
# Chart 1: Price overlay with ±5% band around index
# ---------------------------------------------------------------------------
fig1 = go.Figure()

band_upper = market_df["index_price"] * (1 + CIRCUIT_BREAKER_THRESHOLD)
band_lower = market_df["index_price"] * (1 - CIRCUIT_BREAKER_THRESHOLD)

fig1.add_trace(go.Scatter(
    x=market_df["t_minute"], y=band_upper, line=dict(width=0), showlegend=False, hoverinfo="skip",
))
fig1.add_trace(go.Scatter(
    x=market_df["t_minute"], y=band_lower, fill="tonexty", fillcolor="rgba(11,95,255,0.08)",
    line=dict(width=0), name="±5% Circuit Breaker Band", hoverinfo="skip",
))
fig1.add_trace(go.Scatter(
    x=market_df["t_minute"], y=market_df["index_price"], name="Index Price",
    line=dict(color=NAVY, width=2.5, dash="dot"),
))
fig1.add_trace(go.Scatter(
    x=market_df["t_minute"], y=market_df["last_price"], name="Last Traded Price",
    line=dict(color=RED, width=2),
))
fig1.add_trace(go.Scatter(
    x=mark_df["t_minute"], y=mark_df["mark_price"], name="Mark Price (engine output)",
    line=dict(color=BLUE, width=3),
))

for _, ev in breaker_df.iterrows():
    if ev["event"] == "CIRCUIT BREAKER TRIPPED":
        fig1.add_vline(x=ev["t_minute"], line=dict(color=RED, width=1, dash="dash"))

fig1.add_vline(x=current_minute, line=dict(color=AMBER, width=2), annotation_text="you are here", annotation_position="top")

fig1.update_layout(
    title="Index vs. Last Traded vs. Mark Price",
    height=430,
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(color=NAVY),
    xaxis=dict(title="Minutes relative to crash trigger (T=0)", gridcolor=GRID, zeroline=False),
    yaxis=dict(title="Price (USD)", gridcolor=GRID, tickformat=",.0f"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    margin=dict(l=10, r=10, t=60, b=10),
)
st.plotly_chart(fig1, use_container_width=True)

# ---------------------------------------------------------------------------
# Chart 2: Deviation % with threshold lines + Chart 3: ticket flood, side by side
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    fig2 = go.Figure()
    colors = [RED if v else GREEN for v in mark_df["breaker_tripped"]]
    fig2.add_trace(go.Scatter(
        x=mark_df["t_minute"], y=mark_df["deviation_pct"] * 100,
        mode="lines", name="Deviation %",
        line=dict(color=BLUE, width=2),
    ))
    fig2.add_trace(go.Scatter(
        x=mark_df["t_minute"], y=mark_df["deviation_pct"] * 100,
        mode="markers", marker=dict(color=colors, size=3), showlegend=False, hoverinfo="skip",
    ))
    fig2.add_hline(y=5, line=dict(color=RED, width=1.5, dash="dash"), annotation_text="+5% trip")
    fig2.add_hline(y=-5, line=dict(color=RED, width=1.5, dash="dash"), annotation_text="-5% trip")
    fig2.add_hline(y=0, line=dict(color=GRID, width=1))
    fig2.add_vline(x=current_minute, line=dict(color=AMBER, width=2))
    fig2.update_layout(
        title="Mark-vs-Index Deviation % (Circuit Breaker Trigger)",
        height=360, plot_bgcolor="white", paper_bgcolor="white", font=dict(color=NAVY),
        xaxis=dict(title="Minutes relative to T=0", gridcolor=GRID, zeroline=False),
        yaxis=dict(title="Deviation %", gridcolor=GRID),
        showlegend=False, margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(fig2, use_container_width=True)

with c2:
    fig3 = make_subplots(specs=[[{"secondary_y": True}]])
    fig3.add_trace(
        go.Bar(x=ticket_df["t_minute"], y=ticket_df["tickets_per_5s"], name="Tickets / 5s", marker_color=AMBER, opacity=0.55),
        secondary_y=False,
    )
    fig3.add_trace(
        go.Scatter(x=ticket_df["t_minute"], y=ticket_df["cumulative_tickets"], name="Cumulative Tickets", line=dict(color=NAVY, width=2.5)),
        secondary_y=True,
    )
    fig3.add_vline(x=current_minute, line=dict(color=AMBER, width=2))
    fig3.update_layout(
        title="Signal #2 — Inbound Support Ticket Flood",
        height=360, plot_bgcolor="white", paper_bgcolor="white", font=dict(color=NAVY),
        xaxis=dict(title="Minutes relative to T=0", gridcolor=GRID, zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=10, r=10, t=60, b=10),
    )
    fig3.update_yaxes(title_text="Tickets / 5s", gridcolor=GRID, secondary_y=False)
    fig3.update_yaxes(title_text="Cumulative", gridcolor=GRID, secondary_y=True)
    st.plotly_chart(fig3, use_container_width=True)

st.write("")
st.markdown("<div class='vl-section-title'>Circuit Breaker Event Log</div>", unsafe_allow_html=True)
if len(breaker_df) == 0:
    st.info("No breaker events yet at this point in the timeline.")
else:
    display_log = breaker_df.copy()
    display_log["deviation_pct"] = display_log["deviation_pct"].map(lambda v: f"{v:+.2f}%")
    display_log["timestamp"] = display_log["timestamp"].dt.strftime("%H:%M:%S")
    st.dataframe(
        display_log.rename(columns={"timestamp": "Time (UTC)", "t_minute": "T (min)", "event": "Event", "deviation_pct": "Deviation"}),
        use_container_width=True,
        hide_index=True,
    )
