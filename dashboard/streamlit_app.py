from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"

st.set_page_config(page_title="RAAVBSS Tennis Capstone", layout="wide")

CLUSTER_STORIES = {
    0: {
        "name": "Slow-Serve Specialists, Pace Vulnerable",
        "plain": "These players are most comfortable when body serves are slower, but their return accuracy drops as pace rises.",
        "risk": "A scouting report would test them with faster body serves into the body.",
    },
    1: {
        "name": "All-Speed Return Anchors",
        "plain": "This is the strongest profile: high return accuracy across slow, medium, and fast body serves.",
        "risk": "They are harder to pressure with body-serve speed alone.",
    },
    2: {
        "name": "Medium-Speed Leaners",
        "plain": "A small group that looks best against medium-speed body serves, but does not translate that profile into strong return-point outcomes.",
        "risk": "Treat carefully because the group is small.",
    },
    3: {
        "name": "High Accuracy, Slight Fast-Serve Drop",
        "plain": "Strong overall returners whose accuracy falls most on fast body serves.",
        "risk": "Useful profile for players who remain reliable but can still be pressured with pace.",
    },
    4: {
        "name": "Fast-Serve Resilient Returners",
        "plain": "These players hold up relatively well against faster body serves compared with their medium-speed performance.",
        "risk": "The shape is useful tactically, even if the cluster is not the top return-win group.",
    },
    5: {
        "name": "Sharp Pace Drop-Off",
        "plain": "These players are excellent on slow body serves but lose substantial accuracy as speed increases.",
        "risk": "This is the clearest speed-sensitivity profile.",
    },
    6: {
        "name": "Solid but Pace Sensitive",
        "plain": "A large middle group with solid return accuracy but a visible decline against faster body serves.",
        "risk": "Good baseline returners, but not the most adaptable group.",
    },
}


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    comparison = pd.read_csv(DATA / "cluster_comparison_stats_cleaned.csv")
    players = pd.read_csv(DATA / "player_rse_clusters_k7.csv")
    profiles = pd.read_csv(DATA / "cluster_profiles.csv")
    thresholds = pd.read_csv(DATA / "speed_bin_thresholds.csv")
    tests = pd.read_csv(DATA / "statistical_tests.csv")

    for frame in (comparison, players, profiles):
        if "cluster" in frame.columns:
            frame["cluster"] = frame["cluster"].astype("Int64")
            frame["cluster_label"] = frame["cluster"].map(lambda value: CLUSTER_STORIES.get(int(value), {}).get("name") if pd.notna(value) else "Not clustered")

    return comparison, players, profiles, thresholds, tests


def pct(series: pd.Series | float) -> pd.Series | float:
    return series * 100


def format_pct(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value * 100:.1f}%"


def section_header(title: str, subtitle: str) -> None:
    st.subheader(title)
    st.caption(subtitle)


comparison, players, profiles, thresholds, tests = load_data()

st.title("RAAVBSS: Tennis Return Adaptability Dashboard")
st.markdown(
    """
    This dashboard explains a capstone project for people who may not know tennis analytics.

    **Plain-English idea:** when a server aims the ball at the returner's body, does the returner still get the ball back
    as serve speed changes? RAAVBSS measures that adaptability across slow, medium, and fast body serves.
    """
)

with st.expander("Tennis terms in 30 seconds", expanded=True):
    st.markdown(
        """
        - **Serve:** the shot that starts a point.
        - **Return:** the opponent's first shot after the serve.
        - **Body serve:** a serve aimed toward the returner's body, often used to jam their swing.
        - **Return accuracy:** whether the return was recorded as landing deep or not deep, meaning the return came back in play.
        - **Return point win percentage:** whether the returner actually won the point. This is harder than just getting the return in.
        - **Cluster:** a group of players with similarly shaped RAAVBSS profiles.
        """
    )

tour_options = ["Both"] + sorted(players["tour"].dropna().unique().tolist())
selected_tour = st.sidebar.selectbox("Tour", tour_options)
cluster_options = ["All"] + [f"{int(row.cluster)}: {row.cluster_label}" for row in profiles.sort_values("cluster").itertuples()]
selected_cluster_text = st.sidebar.selectbox("Cluster profile", cluster_options)

filtered_players = players.copy()
filtered_comparison = comparison.copy()
if selected_tour != "Both":
    filtered_players = filtered_players[filtered_players["tour"] == selected_tour]
    filtered_comparison = filtered_comparison[filtered_comparison["tour"] == selected_tour]
if selected_cluster_text != "All":
    selected_cluster = int(selected_cluster_text.split(":")[0])
    filtered_players = filtered_players[filtered_players["cluster"] == selected_cluster]
    filtered_comparison = filtered_comparison[filtered_comparison["cluster"] == selected_cluster]

clustered_comparison = comparison.dropna(subset=["cluster"]).copy()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Matches processed", "6,127")
col2.metric("Body-serve rows", "237,201")
col3.metric("Clustered players", f"{len(players):,}")
col4.metric("Final comparison players", f"{len(comparison):,}")

section_header(
    "1. What Problem Is This Solving?",
    "A single return percentage hides whether a player adapts when a body serve gets faster."
)

st.markdown(
    """
    A tennis coach could use this to ask: **Should we attack this player with faster body serves, or are they reliable
    across all body-serve speeds?** The model is not predicting winners by itself. It is turning point-level data into
    scouting-style return profiles.
    """
)

section_header(
    "2. How Serve Speeds Were Split",
    "The speed bins are tour-specific because ATP and WTA serve speeds have different distributions."
)
threshold_display = thresholds.copy()
threshold_display["speed_range_mph"] = threshold_display["min_speed_mph"].round(0).astype(int).astype(str) + "-" + threshold_display["max_speed_mph"].round(0).astype(int).astype(str)
fig_thresholds = px.bar(
    threshold_display,
    x="speed_bin",
    y="n_body_serves",
    color="tour",
    barmode="group",
    text="speed_range_mph",
    labels={"speed_bin": "Serve speed bin", "n_body_serves": "Body serves", "tour": "Tour"},
    title="Each tour is split into slow, medium, and fast body serves",
)
fig_thresholds.update_traces(textposition="outside")
fig_thresholds.update_layout(yaxis_tickformat=",")
st.plotly_chart(fig_thresholds, use_container_width=True)

section_header(
    "3. The Main Result: Returner Archetypes",
    "Each line shows average return accuracy for one cluster across slow, medium, and fast body serves."
)
profile_long = profiles.melt(
    id_vars=["cluster", "n_players", "return_win_pct", "serve_win_pct", "total_win_pct", "cluster_label"],
    value_vars=["ras_slow", "ras_medium", "ras_fast"],
    var_name="speed_bin",
    value_name="return_accuracy",
)
profile_long["speed_bin"] = profile_long["speed_bin"].str.replace("ras_", "", regex=False).str.title()
profile_long["return_accuracy_pct"] = pct(profile_long["return_accuracy"])
profile_long["cluster_story"] = profile_long["cluster"].astype(int).astype(str) + ": " + profile_long["cluster_label"]
fig_profiles = px.line(
    profile_long,
    x="speed_bin",
    y="return_accuracy_pct",
    color="cluster_story",
    markers=True,
    labels={"speed_bin": "Body-serve speed", "return_accuracy_pct": "Return accuracy (%)", "cluster_story": "Cluster"},
    title="RAAVBSS profile shapes",
)
fig_profiles.update_layout(yaxis_range=[75, 100])
st.plotly_chart(fig_profiles, use_container_width=True)

cluster_cards = profiles.sort_values("return_win_pct", ascending=False).copy()
st.markdown("#### Cluster guide")
for row in cluster_cards.itertuples():
    story = CLUSTER_STORIES[int(row.cluster)]
    with st.container(border=True):
        left, right = st.columns([2, 1])
        left.markdown(f"**Cluster {int(row.cluster)}: {story['name']}**")
        left.write(story["plain"])
        left.caption(story["risk"])
        right.metric("Players", f"{int(row.n_players)}")
        right.metric("Return point win %", format_pct(row.return_win_pct))

section_header(
    "4. Does the Return Profile Relate to Winning Return Points?",
    "Return accuracy is not the same as winning the point. This chart checks whether the profiles connect to outcomes."
)
outcome_df = profiles.copy()
outcome_df["return_win_pct_display"] = pct(outcome_df["return_win_pct"])
outcome_df["serve_win_pct_display"] = pct(outcome_df["serve_win_pct"])
outcome_df["cluster_story"] = outcome_df["cluster"].astype(int).astype(str) + ": " + outcome_df["cluster_label"]
fig_outcomes = px.bar(
    outcome_df.sort_values("return_win_pct", ascending=False),
    x="cluster_story",
    y="return_win_pct_display",
    color="cluster_story",
    labels={"cluster_story": "Cluster", "return_win_pct_display": "Return point win (%)"},
    title="Average return point win percentage by cluster",
)
fig_outcomes.update_layout(showlegend=False, xaxis_tickangle=-25)
st.plotly_chart(fig_outcomes, use_container_width=True)

best = outcome_df.sort_values("return_win_pct", ascending=False).iloc[0]
st.info(
    f"The strongest return-outcome group is Cluster {int(best.cluster)} ({best.cluster_label}), "
    f"with an average return point win rate of {format_pct(best.return_win_pct)}."
)

section_header(
    "5. Player Explorer",
    "Use this table to connect the model back to recognizable players and scouting notes."
)
player_table = filtered_comparison.dropna(subset=["cluster"]).copy()
player_table["return_win_pct"] = pct(player_table["return_win_pct"]).round(1)
player_table["serve_win_pct"] = pct(player_table["serve_win_pct"]).round(1)
for col in ["ras_slow", "ras_medium", "ras_fast"]:
    player_table[col] = pct(player_table[col]).round(1)
player_table = player_table[
    [
        "tour", "player_name", "cluster", "cluster_label", "ras_slow", "ras_medium", "ras_fast",
        "return_win_pct", "serve_win_pct", "body_return_pts",
    ]
].sort_values(["return_win_pct", "body_return_pts"], ascending=False)
st.dataframe(
    player_table,
    use_container_width=True,
    hide_index=True,
    column_config={
        "tour": "Tour",
        "player_name": "Player",
        "cluster": "Cluster",
        "cluster_label": "Scouting profile",
        "ras_slow": "Slow return accuracy %",
        "ras_medium": "Medium return accuracy %",
        "ras_fast": "Fast return accuracy %",
        "return_win_pct": "Return point win %",
        "serve_win_pct": "Serve point win %",
        "body_return_pts": "Body serves returned",
    },
)

section_header(
    "6. Model Map",
    "The PCA map compresses the three RAAVBSS scores into two dimensions so similar return profiles sit near each other."
)
fig_pca = px.scatter(
    filtered_players,
    x="PC1",
    y="PC2",
    color="cluster_label",
    symbol="tour",
    hover_name="player_name",
    hover_data={"ras_slow": ":.2f", "ras_medium": ":.2f", "ras_fast": ":.2f", "body_return_pts": True, "PC1": False, "PC2": False},
    labels={"cluster_label": "Scouting profile"},
    title="Player similarity map based on RAAVBSS",
)
st.plotly_chart(fig_pca, use_container_width=True)

section_header(
    "7. Evidence and Caveats",
    "This is the part portfolio reviewers care about: what is supported, and what is not."
)
left, right = st.columns(2)
with left:
    st.markdown("**Supported by the project**")
    st.markdown(
        """
        - Body-serve return profiles differ across players.
        - The best all-speed profile also has the strongest average return-point outcome.
        - ATP clusters show clearer outcome separation than WTA clusters under the current settings.
        """
    )
with right:
    st.markdown("**Important caveats**")
    st.markdown(
        """
        - This is descriptive, not causal.
        - Return accuracy is proxied from recorded return depth.
        - Player names from the source can have inconsistent formatting, so name cleaning is a future improvement.
        """
    )

st.markdown("#### Statistical test summary")
tests_display = tests.copy()
tests_display["p_value"] = tests_display["p_value"].map(lambda value: f"{value:.4g}")
tests_display["statistic"] = tests_display["statistic"].round(3)
st.dataframe(tests_display, use_container_width=True, hide_index=True)

st.caption("Data source: Jeff Sackmann Grand Slam point-by-point tennis data, 2017-2024 subset used by this project.")
