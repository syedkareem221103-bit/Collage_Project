import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="IPL 2022 Analytics Dashboard",
    page_icon="🏏",
    layout="wide"
)

# -----------------------------------
# LOAD DATA
# -----------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("data/ipl_2022_deliveries.csv")
    return df

df = load_data()

# -----------------------------------
# CREATE FEATURES
# -----------------------------------

df["total_runs"] = df["runs_of_bat"] + df["extras"]

df["is_wicket"] = np.where(
    df["player_dismissed"].notna(),
    1,
    0
)

# -----------------------------------
# HEADER
# -----------------------------------

st.title("🏏 IPL 2022 Analytics Dashboard")
st.markdown("### Deep Cricket Analytics using Ball-by-Ball Data")

st.markdown("---")

# -----------------------------------
# SIDEBAR FILTERS
# -----------------------------------

st.sidebar.header("Filters")

teams = sorted(df["batting_team"].unique())

selected_team = st.sidebar.selectbox(
    "Select Team",
    ["All Teams"] + teams
)

if selected_team != "All Teams":
    filtered_df = df[df["batting_team"] == selected_team]
else:
    filtered_df = df.copy()

# -----------------------------------
# KPI SECTION
# -----------------------------------

total_runs = filtered_df["total_runs"].sum()
total_wickets = filtered_df["is_wicket"].sum()

matches = filtered_df["match_id"].nunique()

players = filtered_df["striker"].nunique()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Runs", f"{total_runs:,}")
c2.metric("Total Wickets", f"{total_wickets:,}")
c3.metric("Matches", matches)
c4.metric("Batters", players)

st.markdown("---")

# ===================================
# TEAM RUNS ANALYSIS
# ===================================

st.subheader("📈 Team-wise Runs")

team_runs = (
    df.groupby("batting_team")["total_runs"]
    .sum()
    .reset_index()
    .sort_values("total_runs", ascending=False)
)

fig = px.bar(
    team_runs,
    x="batting_team",
    y="total_runs",
    color="total_runs",
    title="Total Runs by Team"
)

st.plotly_chart(fig, use_container_width=True)

# ===================================
# TOP BATSMEN
# ===================================

st.subheader("🏏 Top Run Scorers")

top_batsmen = (
    df.groupby("striker")["runs_of_bat"]
    .sum()
    .reset_index()
    .sort_values("runs_of_bat", ascending=False)
    .head(15)
)

fig = px.bar(
    top_batsmen,
    x="striker",
    y="runs_of_bat",
    color="runs_of_bat",
    title="Top 15 Batsmen"
)

st.plotly_chart(fig, use_container_width=True)

# ===================================
# TOP BOWLERS
# ===================================

st.subheader("🎯 Top Wicket Takers")

top_bowlers = (
    df[df["player_dismissed"].notna()]
    .groupby("bowler")
    .size()
    .reset_index(name="wickets")
    .sort_values("wickets", ascending=False)
    .head(15)
)

fig = px.bar(
    top_bowlers,
    x="bowler",
    y="wickets",
    color="wickets",
    title="Top Wicket Takers"
)

st.plotly_chart(fig, use_container_width=True)

# ===================================
# VENUE ANALYSIS
# ===================================

st.subheader("🏟 Venue Analysis")

venue_runs = (
    df.groupby("venue")["total_runs"]
    .sum()
    .reset_index()
    .sort_values("total_runs", ascending=False)
)

fig = px.bar(
    venue_runs,
    x="venue",
    y="total_runs",
    color="total_runs",
    title="Runs by Venue"
)

fig.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig, use_container_width=True)

# ===================================
# RUN DISTRIBUTION
# ===================================

st.subheader("🔥 Run Distribution")

run_dist = (
    df["runs_of_bat"]
    .value_counts()
    .sort_index()
    .reset_index()
)

run_dist.columns = ["Runs", "Frequency"]

fig = px.pie(
    run_dist,
    names="Runs",
    values="Frequency",
    title="Distribution of Scoring Shots"
)

st.plotly_chart(fig, use_container_width=True)

# ===================================
# OVER-WISE SCORING
# ===================================

st.subheader("📊 Over-wise Run Rate")

df["over_no"] = df["over"].astype(str).str.split(".").str[0]

over_runs = (
    df.groupby("over_no")["total_runs"]
    .sum()
    .reset_index()
)

fig = px.line(
    over_runs,
    x="over_no",
    y="total_runs",
    markers=True,
    title="Runs Scored by Over"
)

st.plotly_chart(fig, use_container_width=True)

# ===================================
# BATSMAN VS BOWLER ANALYSIS
# ===================================

st.subheader("⚔ Batter vs Bowler")

batter = st.selectbox(
    "Choose Batter",
    sorted(df["striker"].unique())
)

player_df = df[df["striker"] == batter]

bowler_stats = (
    player_df.groupby("bowler")["runs_of_bat"]
    .sum()
    .reset_index()
    .sort_values("runs_of_bat", ascending=False)
    .head(10)
)

fig = px.bar(
    bowler_stats,
    x="bowler",
    y="runs_of_bat",
    color="runs_of_bat",
    title=f"{batter} Against Bowlers"
)

st.plotly_chart(fig, use_container_width=True)

# ===================================
# INSIGHTS
# ===================================

st.subheader("💡 Auto Insights")

best_batsman = top_batsmen.iloc[0]["striker"]
best_batsman_runs = top_batsmen.iloc[0]["runs_of_bat"]

best_bowler = top_bowlers.iloc[0]["bowler"]
best_bowler_wickets = top_bowlers.iloc[0]["wickets"]

best_team = team_runs.iloc[0]["batting_team"]

st.success(
    f"""
🏆 Highest Scoring Team: {best_team}

🏏 Top Batsman: {best_batsman} ({best_batsman_runs} Runs)

🎯 Best Bowler: {best_bowler} ({best_bowler_wickets} Wickets)

📈 Dashboard generated from IPL 2022 Ball-by-Ball Data.
"""
)

# ===================================
# RAW DATA
# ===================================

with st.expander("View Dataset"):
    st.dataframe(df)
