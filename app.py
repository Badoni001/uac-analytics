"""
app.py  —  UAC Care Transition Efficiency & Placement Outcome Analytics
Streamlit dashboard for HHS Unified Mentor project.

Run: streamlit run app.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from analysis import load_data, compute_kpis, get_summary

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UAC Pipeline Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Colour palette ───────────────────────────────────────────────────────────
C_CORAL   = "#E8593C"
C_TEAL    = "#1D9E75"
C_PURPLE  = "#7F77DD"
C_AMBER   = "#EF9F27"
C_BLUE    = "#378ADD"
C_GRAY    = "#888780"

# ── Custom theme / CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
/* Main app background */
.stApp {
    background: linear-gradient(180deg, #F7F8FC 0%, #EEF1F8 100%);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1B2A4A 0%, #16203A 100%);
}
section[data-testid="stSidebar"] * {
    color: #E9EDF7 !important;
}
section[data-testid="stSidebar"] .stSlider, 
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15) !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.08) !important;
}

/* Fix: date input / text input boxes must show DARK text on their WHITE background */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] [data-baseweb="input"] input,
section[data-testid="stSidebar"] [data-baseweb="datepicker"] input {
    color: #1B2A4A !important;
    background-color: #FFFFFF !important;
}
section[data-testid="stSidebar"] [data-baseweb="input"] > div {
    background-color: #FFFFFF !important;
}
/* Calendar popup (date picker dropdown) needs dark text too */
div[data-baseweb="calendar"] {
    color: #1B2A4A !important;
}
div[data-baseweb="calendar"] * {
    color: #1B2A4A !important;
}

/* Header banner */
.hero-banner {
    background: linear-gradient(120deg, #1B2A4A 0%, #2C4270 50%, #3B5998 100%);
    padding: 28px 32px;
    border-radius: 16px;
    margin-bottom: 18px;
    box-shadow: 0 4px 18px rgba(27,42,74,0.25);
}
.hero-banner h1 {
    color: #FFFFFF !important;
    margin: 0 0 6px 0;
    font-size: 2.1rem;
}
.hero-banner p {
    color: #C7D3F0 !important;
    margin: 0;
    font-size: 0.95rem;
}

/* KPI cards */
div[data-testid="stMetric"] {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 14px 16px 10px 16px;
    border: 1px solid #E4E8F2;
    box-shadow: 0 2px 8px rgba(27,42,74,0.06);
}
div[data-testid="stMetric"] label {
    color: #5B6B8C !important;
    font-weight: 600;
}
div[data-testid="stMetricValue"] {
    color: #1B2A4A !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-weight: 600;
    border-radius: 8px 8px 0 0;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background-color: #FFFFFF;
    border-bottom: 3px solid #E8593C;
}

/* Subheaders */
h3 {
    color: #1B2A4A;
}

/* Section containers around charts */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    df_raw = load_data()
    df     = compute_kpis(df_raw)
    return df

df_full = get_data()
summary = get_summary(df_full)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 UAC Analytics")
    st.caption("HHS Office of Refugee Resettlement")
    st.divider()

    # Date range
    st.subheader("📅 Date range")
    min_d = df_full["Date"].min().date()
    max_d = df_full["Date"].max().date()
    date_range = st.date_input(
        "Select range",
        value=(min_d, max_d),
        min_value=min_d,
        max_value=max_d,
    )

    st.divider()
    st.subheader("⚙️ Settings")
    threshold = st.slider(
        "Backlog alert threshold (children/day)",
        min_value=0, max_value=300, value=50, step=10,
    )
    rolling_window = st.selectbox(
        "Trend smoothing window",
        options=[7, 14, 30],
        index=2,
        format_func=lambda x: f"{x}-day rolling avg",
    )
    show_raw = st.toggle("Overlay raw data on trend charts", value=False)

    st.divider()
    st.caption("Data: HHS UAC Program · Jan 2023 – Dec 2025")

# ── Apply date filter ────────────────────────────────────────────────────────
if len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start, end = df_full["Date"].min(), df_full["Date"].max()

df = df_full[(df_full["Date"] >= start) & (df_full["Date"] <= end)].copy()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-banner">
    <h1>Care Transition Efficiency & Placement Outcome Analytics</h1>
    <p>U.S. Department of Health and Human Services &nbsp;·&nbsp;
    {start.strftime('%b %d, %Y')} – {end.strftime('%b %d, %Y')} &nbsp;·&nbsp;
    {len(df):,} reporting days</p>
</div>
""", unsafe_allow_html=True)

# ── KPI cards ────────────────────────────────────────────────────────────────
k = get_summary(df)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(
    "Avg transfer efficiency",
    f"{k['avg_transfer_efficiency']:.1%}",
    help="Transfers ÷ CBP custody load. Ideal ≈ 1.0",
)
col2.metric(
    "Avg discharge effectiveness",
    f"{k['avg_discharge_effectiveness']:.2%}",
    help="Discharges ÷ HHS care load. Measures daily reunification rate.",
)
col3.metric(
    "Avg pipeline throughput",
    f"{k['avg_pipeline_throughput']:.2f}x",
    help="Total exits ÷ Total entries. >1 means system is clearing faster than intake.",
)
col4.metric(
    "Avg daily backlog",
    f"{k['avg_backlog_rate']:+.0f}",
    help="CBP intake − HHS discharges. Negative = discharges outpace intake (good).",
)
col5.metric(
    "Outcome stability (σ)",
    f"{k['avg_outcome_stability']:.4f}",
    help="7-day rolling std of discharge effectiveness. Lower = more consistent.",
)

st.divider()

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Pipeline Flow",
    "⚡  Efficiency Metrics",
    "🚨  Bottleneck Detection",
    "📈  Outcome Trends",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Pipeline Flow
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Daily care pipeline volumes")
    st.caption(
        "Three concurrent time series showing active custody at each pipeline stage. "
        "HHS care load is measured in thousands. Divergence between intake and discharges "
        "signals accumulating backlog."
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["cbp_load"],
        name="CBP custody (active)", mode="lines",
        line=dict(color=C_CORAL, width=1.5),
    ))
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["hhs_load"],
        name="HHS care (active)", mode="lines",
        line=dict(color=C_TEAL, width=2),
    ))
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["hhs_discharges"],
        name="Daily discharges (sponsor placements)", mode="lines",
        line=dict(color=C_PURPLE, width=1.5),
    ))
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["cbp_intake"],
        name="Daily CBP intake (apprehensions)", mode="lines",
        line=dict(color=C_AMBER, width=1, dash="dot"),
    ))
    fig.update_layout(
        xaxis_title="Date", yaxis_title="Number of children",
        legend=dict(orientation="h", y=-0.2),
        hovermode="x unified", height=420,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Monthly aggregate
    st.subheader("Monthly average — CBP vs HHS vs discharges")
    monthly = (
        df.groupby("month")[["cbp_load", "hhs_load", "hhs_discharges"]]
        .mean()
        .reset_index()
    )
    fig_m = px.bar(
        monthly, x="month", y=["cbp_load", "hhs_load", "hhs_discharges"],
        barmode="group",
        labels={"value": "Avg children", "month": "Month", "variable": "Stage"},
        color_discrete_map={
            "cbp_load": C_CORAL, "hhs_load": C_TEAL, "hhs_discharges": C_PURPLE,
        },
    )
    fig_m.update_xaxes(tickangle=45)
    fig_m.update_layout(height=380, legend=dict(orientation="h", y=-0.3))
    st.plotly_chart(fig_m, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Efficiency Metrics
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Transfer efficiency & discharge effectiveness over time")
    st.caption(
        "Transfer efficiency = daily CBP transfers ÷ CBP custody load.  "
        "Values >1 indicate a catch-up burst; values near 0 signal a bottleneck."
    )

    fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                         subplot_titles=("Transfer efficiency ratio",
                                         "Discharge effectiveness ratio"))

    roll_te = df["transfer_efficiency"].rolling(rolling_window).mean()
    roll_de = df["discharge_effectiveness"].rolling(rolling_window).mean()

    if show_raw:
        fig2.add_trace(go.Scatter(x=df["Date"], y=df["transfer_efficiency"],
                                  name="Transfer eff. (raw)", opacity=0.3,
                                  line=dict(color=C_CORAL, width=1)), row=1, col=1)
        fig2.add_trace(go.Scatter(x=df["Date"], y=df["discharge_effectiveness"],
                                  name="Discharge eff. (raw)", opacity=0.3,
                                  line=dict(color=C_PURPLE, width=1)), row=2, col=1)

    fig2.add_trace(go.Scatter(x=df["Date"], y=roll_te,
                              name=f"Transfer eff. ({rolling_window}-day avg)",
                              line=dict(color=C_CORAL, width=2)), row=1, col=1)
    fig2.add_trace(go.Scatter(x=df["Date"], y=roll_de,
                              name=f"Discharge eff. ({rolling_window}-day avg)",
                              line=dict(color=C_PURPLE, width=2)), row=2, col=1)

    # Ideal reference lines
    fig2.add_hline(y=1.0, row=1, col=1, line_dash="dash", line_color=C_GRAY,
                   annotation_text="Ideal = 1.0")
    fig2.update_layout(height=500, hovermode="x unified",
                       legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig2, use_container_width=True)

    # Weekday vs Weekend
    st.subheader("Weekday vs weekend — average KPIs")
    col_a, col_b = st.columns(2)

    we_te = df.groupby("is_weekend")["transfer_efficiency"].mean().reset_index()
    we_te["Day type"] = we_te["is_weekend"].map({True: "Weekend", False: "Weekday"})
    fig_we = px.bar(
        we_te, x="Day type", y="transfer_efficiency",
        color="Day type",
        color_discrete_map={"Weekday": C_TEAL, "Weekend": C_CORAL},
        labels={"transfer_efficiency": "Avg transfer efficiency"},
        title="Transfer efficiency",
    )
    col_a.plotly_chart(fig_we, use_container_width=True)

    we_de = df.groupby("is_weekend")["discharge_effectiveness"].mean().reset_index()
    we_de["Day type"] = we_de["is_weekend"].map({True: "Weekend", False: "Weekday"})
    fig_we2 = px.bar(
        we_de, x="Day type", y="discharge_effectiveness",
        color="Day type",
        color_discrete_map={"Weekday": C_TEAL, "Weekend": C_CORAL},
        labels={"discharge_effectiveness": "Avg discharge effectiveness"},
        title="Discharge effectiveness",
    )
    col_b.plotly_chart(fig_we2, use_container_width=True)

    # Quarterly trend
    st.subheader("Quarterly pipeline throughput")
    q_df = df.groupby("quarter")["pipeline_throughput"].mean().reset_index()
    fig_q = px.line(
        q_df, x="quarter", y="pipeline_throughput",
        markers=True, color_discrete_sequence=[C_BLUE],
        labels={"pipeline_throughput": "Avg throughput ratio", "quarter": "Quarter"},
    )
    fig_q.add_hline(y=1.0, line_dash="dash", line_color=C_GRAY,
                    annotation_text="Breakeven = 1.0")
    st.plotly_chart(fig_q, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Bottleneck Detection
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Backlog accumulation — daily net load")
    st.caption(
        f"Backlog = CBP intake − HHS discharges. "
        f"Red markers = days exceeding alert threshold of {threshold} children. "
        f"Sustained positive values indicate a growing system backlog."
    )

    df_bt = df.copy()
    df_bt["alert"] = df_bt["backlog_rate"] > threshold
    alert_days = df_bt[df_bt["alert"]]

    fig_b = go.Figure()
    fig_b.add_trace(go.Scatter(
        x=df_bt["Date"], y=df_bt["backlog_rate"].clip(lower=0),
        fill="tozeroy", name="Positive backlog",
        line=dict(color=C_AMBER, width=0), fillcolor=f"rgba(239,159,39,0.35)",
    ))
    fig_b.add_trace(go.Scatter(
        x=df_bt["Date"], y=df_bt["backlog_rate"].clip(upper=0),
        fill="tozeroy", name="Negative backlog (clearance)",
        line=dict(color=C_TEAL, width=0), fillcolor=f"rgba(29,158,117,0.25)",
    ))
    fig_b.add_trace(go.Scatter(
        x=df_bt["Date"], y=df_bt["backlog_rate"],
        name="Backlog rate", mode="lines",
        line=dict(color=C_GRAY, width=1),
    ))
    fig_b.add_scatter(
        x=alert_days["Date"], y=alert_days["backlog_rate"],
        mode="markers", name=f"⚠ Above threshold ({threshold})",
        marker=dict(color=C_CORAL, size=7, symbol="circle"),
    )
    fig_b.add_hline(y=threshold, line_dash="dot", line_color=C_CORAL,
                    annotation_text=f"Alert: {threshold}")
    fig_b.add_hline(y=0, line_color=C_GRAY, line_width=0.5)
    fig_b.update_layout(height=400, yaxis_title="Net children (intake − discharges)",
                        hovermode="x unified", legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig_b, use_container_width=True)

    # Alert summary
    n_alerts = len(alert_days)
    pct_alerts = n_alerts / len(df_bt) * 100 if len(df_bt) > 0 else 0
    colx, coly, colz = st.columns(3)
    colx.metric("Days above threshold", n_alerts)
    coly.metric("% of reporting days", f"{pct_alerts:.1f}%")
    colz.metric("Peak backlog day",
                alert_days.loc[alert_days["backlog_rate"].idxmax(), "Date"].strftime("%b %d, %Y")
                if not alert_days.empty else "None")

    # Monthly backlog heatmap
    st.subheader("Month-over-month average backlog")
    monthly_bl = df.groupby("month")["backlog_rate"].mean().reset_index()
    fig_mb = px.bar(
        monthly_bl, x="month", y="backlog_rate",
        color="backlog_rate",
        color_continuous_scale=["#1D9E75", "#EF9F27", "#E8593C"],
        labels={"backlog_rate": "Avg daily backlog", "month": "Month"},
    )
    fig_mb.update_xaxes(tickangle=45)
    fig_mb.update_layout(height=380)
    st.plotly_chart(fig_mb, use_container_width=True)

    # Correlation: intake vs discharges scatter
    st.subheader("Intake vs discharges — are they correlated?")
    fig_sc = px.scatter(
        df, x="cbp_intake", y="hhs_discharges",
        color="year", opacity=0.6,
        color_continuous_scale="Viridis",
        labels={"cbp_intake": "Daily CBP intake", "hhs_discharges": "Daily HHS discharges"},
        trendline="ols",
    )
    fig_sc.update_layout(height=380)
    st.plotly_chart(fig_sc, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — Outcome Trends
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("Sponsor placement outcomes — discharge effectiveness trend")
    st.caption(
        "Discharge effectiveness = daily HHS discharges ÷ HHS care load. "
        "Tracks how efficiently children in HHS care are reunited with sponsors on any given day."
    )

    fig_ot = go.Figure()
    if show_raw:
        fig_ot.add_trace(go.Scatter(
            x=df["Date"], y=df["discharge_effectiveness"],
            name="Daily (raw)", opacity=0.25,
            line=dict(color=C_PURPLE, width=1),
        ))
    roll = df["discharge_effectiveness"].rolling(rolling_window).mean()
    fig_ot.add_trace(go.Scatter(
        x=df["Date"], y=roll,
        name=f"{rolling_window}-day rolling avg",
        line=dict(color=C_PURPLE, width=2.5),
    ))
    fig_ot.update_layout(height=400, yaxis_title="Discharge effectiveness ratio",
                         hovermode="x unified", legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig_ot, use_container_width=True)

    col_c, col_d = st.columns(2)

    # Outcome stability
    with col_c:
        st.subheader("Outcome stability — rolling 7-day std dev")
        st.caption("Higher values = more volatile daily placement rates.")
        fig_os = px.area(
            df, x="Date", y="outcome_stability",
            color_discrete_sequence=[C_AMBER],
            labels={"outcome_stability": "Std deviation (7-day)"},
        )
        fig_os.update_layout(height=320)
        st.plotly_chart(fig_os, use_container_width=True)

    # Year-over-year discharge box
    with col_d:
        st.subheader("Year-over-year discharge distribution")
        fig_box = px.box(
            df, x="year", y="hhs_discharges",
            color="year",
            color_discrete_sequence=[C_TEAL, C_BLUE, C_PURPLE],
            labels={"hhs_discharges": "Daily discharges", "year": "Year"},
        )
        fig_box.update_layout(height=320, showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

    # Monthly discharge heatmap by year
    st.subheader("Discharge effectiveness — monthly heatmap")
    df["month_num"] = df["Date"].dt.month
    hm = df.groupby(["year", "month_num"])["discharge_effectiveness"].mean().reset_index()
    hm_pivot = hm.pivot(index="year", columns="month_num", values="discharge_effectiveness")
    month_labels = ["Jan","Feb","Mar","Apr","May","Jun",
                    "Jul","Aug","Sep","Oct","Nov","Dec"]
    fig_hm = px.imshow(
        hm_pivot,
        x=month_labels[:hm_pivot.shape[1]],
        y=hm_pivot.index.astype(str),
        color_continuous_scale="Teal",
        labels={"color": "Discharge effectiveness"},
        aspect="auto",
    )
    fig_hm.update_layout(height=260)
    st.plotly_chart(fig_hm, use_container_width=True)

st.divider()
st.caption(
    "UAC Care Transition Efficiency & Placement Outcome Analytics  ·  "
    "Unified Mentor Project  ·  U.S. Department of Health and Human Services"
)
