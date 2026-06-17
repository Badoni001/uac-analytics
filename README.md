# Care Transition Efficiency & Placement Outcome Analytics

**Unified Mentor Project · U.S. Department of Health and Human Services (HHS)**

A process-efficiency analytics dashboard for the Unaccompanied Alien Children (UAC) Program — measuring how fast and reliably children move through the CBP → HHS → Sponsor reunification pipeline, instead of just counting how many are in custody at a given moment.

---

## 📋 Table of Contents

- [Background](#background)
- [Problem Statement](#problem-statement)
- [Objectives](#objectives)
- [Dataset](#dataset)
- [KPIs](#kpis)
- [Project Structure](#project-structure)
- [Setup & Run](#setup--run)
- [Dashboard Modules](#dashboard-modules)
- [Methodology](#methodology)
- [Deliverables](#deliverables)
- [Tech Stack](#tech-stack)

---

## Background

The UAC Program is a multi-stage care and reunification pipeline:

```
Apprehension & CBP custody → Transfer to HHS care →
Medical screening, sheltering & case management →
Discharge & reunification with a vetted sponsor
```

Speed, continuity, and reliability through this pipeline matter as much as raw capacity — a child stuck mid-pipeline is a child not yet safely home.

## Problem Statement

Aggregate headcounts (how many children are currently in custody) are tracked, but **process efficiency is not**. This leaves key questions unanswered:

- How efficiently are children transferred from CBP to HHS?
- Are discharges keeping pace with inflows?
- When and where do care backlogs accumulate?
- Are placement outcomes improving or deteriorating over time?

Without structured transition analytics, bottlenecks in the system stay invisible until they become a crisis.

## Objectives

**Primary**
- Measure efficiency of CBP → HHS transitions
- Evaluate discharge and sponsor placement outcomes
- Identify delays and process bottlenecks

**Secondary**
- Support faster reunification
- Improve case management workflows
- Inform policy-level process reforms

## Dataset

`data/HHS_Unaccompanied_Alien_Children_Program.csv`

720 reporting days · January 12, 2023 – December 21, 2025

| Column | Description |
|---|---|
| Date | Reporting date |
| Children apprehended and placed in CBP custody | Daily intake volume |
| Children in CBP custody | Active CBP care load |
| Children transferred out of CBP custody | Flow into HHS system |
| Children in HHS Care | Active HHS care load |
| Children discharged from HHS Care | Successful sponsor placements |

**Cleaning applied:** blank padding rows removed; `Children in HHS Care` parsed from comma-formatted strings (e.g. `"2,484"`) into numeric values; dates parsed and sorted chronologically.

## KPIs

| KPI | Formula | What it tells you |
|---|---|---|
| Transfer Efficiency Ratio | Transfers ÷ CBP Custody | Speed of the CBP → HHS handoff |
| Discharge Effectiveness Index | Discharges ÷ HHS Care | Daily reunification rate |
| Pipeline Throughput Rate | Total exits ÷ Total entries | Whether the system clears faster than it fills |
| Backlog Accumulation Rate | CBP intake − HHS discharges | Net daily pressure on the system |
| Outcome Stability Score | 7-day rolling std. dev. of discharge effectiveness | Consistency of placement outcomes |

## Project Structure

```
uac_analytics/
├── data/
│   └── HHS_Unaccompanied_Alien_Children_Program.csv   # raw dataset
├── utils/
│   └── analysis.py        # load_data(), compute_kpis(), get_summary()
├── app.py                 # Streamlit dashboard (entry point)
├── requirements.txt       # Python dependencies
└── README.md
```

## Setup & Run

```bash
# 1. Move into the project folder
cd uac_analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the dashboard
streamlit run app.py
```

Opens automatically at `http://localhost:8501`.

## Dashboard Modules

1. **Pipeline Flow** — Daily CBP/HHS/discharge volumes as a time series, plus monthly aggregates.
2. **Efficiency Metrics** — Transfer efficiency & discharge effectiveness trends, weekday vs weekend comparison, quarterly throughput.
3. **Bottleneck Detection** — Backlog area chart with a user-adjustable alert threshold, intake-vs-discharge correlation scatter.
4. **Outcome Trends** — Rolling discharge effectiveness, outcome stability score, year-over-year distribution, monthly heatmap.

**User controls:** date range filter, backlog alert threshold slider, rolling-average smoothing window, raw-data overlay toggle.

## Methodology

- **Care pipeline modeling** — system represented as a 3-stage flow (CBP custody → HHS care → sponsor placement); daily movement tracked between stages.
- **Transition efficiency metrics** — Transfer Efficiency Ratio, Discharge Effectiveness, Pipeline Throughput Rate computed per reporting day.
- **Backlog & delay identification** — inflow vs. exit comparison to flag sustained imbalance periods and case accumulation.
- **Temporal & pattern analysis** — weekday vs weekend transition speed, month-over-month trends, stagnation period detection.
- **Outcome stability analysis** — rolling variability in discharge performance to flag sudden drops in reunification success.

## Deliverables

- ✅ Streamlit dashboard (this repo)
- ⬜ Research paper (EDA, insights, recommendations)
- ⬜ Executive summary for government stakeholders

## Tech Stack

Python · Pandas · NumPy · Streamlit · Plotly

---

*This project reframes the UAC dataset from a capacity-monitoring lens to a process-efficiency and outcome-evaluation lens, surfacing actionable insights to reduce delays and strengthen reunification outcomes.*
