from __future__ import annotations

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "tennis_capstone_story.ipynb"


def markdown(text: str):
    return nbf.v4.new_markdown_cell(text.strip() + "\n")


def code(text: str):
    return nbf.v4.new_code_cell(text.strip() + "\n")


def build_notebook() -> None:
    NOTEBOOK.parent.mkdir(parents=True, exist_ok=True)
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    }

    cells = [
        markdown(
            """
            # Quantifying Return Adaptability in Professional Tennis

            ## A plain-English capstone walkthrough for portfolio reviewers

            This notebook explains the project from the point of view of someone who may know data analytics but **does not know tennis**.

            **Project in one sentence:** I created a metric called **RAAVBSS** to measure whether tennis players can return body serves accurately when the serve is slow, medium, or fast, then used clustering to turn those patterns into scouting-style player profiles.

            **What to look for as you read:**

            1. What tennis problem is being measured?
            2. How does the metric turn point-level data into player features?
            3. What do the clusters mean in human language?
            4. Do those profiles connect to return-point outcomes?
            5. What are the limitations?
            """
        ),
        markdown(
            """
            ---

            # 1. Tennis Context for Non-Tennis Readers

            A tennis point starts with a **serve**. The opponent's first shot after the serve is the **return**.

            A **body serve** is a serve aimed toward the returner's body. It can be tactically valuable because it gives the returner less room to swing freely. This project asks whether some players are better than others at handling those body serves as the speed changes.

            | Term | Plain-English meaning | Why it matters here |
            |---|---|---|
            | Serve | The shot that starts the point | The server controls the first tactical choice |
            | Return | The opponent's first shot after the serve | The returner is under immediate pressure |
            | Body serve | Serve aimed into the returner's body | It can jam the returner's swing |
            | Return accuracy | Whether the return was recorded as coming back in play | This is the direct RAAVBSS input |
            | Return point win % | Whether the returner ultimately won the point | This checks whether the profile connects to outcomes |
            | Cluster | A group of players with similar metric shapes | Converts numbers into scouting archetypes |
            """
        ),
        code(
            """
            from pathlib import Path
            import pandas as pd
            import numpy as np
            import plotly.express as px
            import plotly.graph_objects as go

            ROOT = Path.cwd()
            if ROOT.name == "notebooks":
                ROOT = ROOT.parent
            DATA = ROOT / "data" / "processed"

            comparison = pd.read_csv(DATA / "cluster_comparison_stats_cleaned.csv")
            players = pd.read_csv(DATA / "player_rse_clusters_k7.csv")
            profiles = pd.read_csv(DATA / "cluster_profiles.csv")
            thresholds = pd.read_csv(DATA / "speed_bin_thresholds.csv")
            tests = pd.read_csv(DATA / "statistical_tests.csv")
            silhouette = pd.read_csv(DATA / "k_selection_silhouette.csv")

            for frame in [comparison, players, profiles]:
                if "cluster" in frame.columns:
                    frame["cluster"] = frame["cluster"].astype("Int64")

            print("Data loaded from:", DATA)
            print("Clustered players:", len(players))
            print("Players in comparison dataset:", len(comparison))
            """
        ),
        markdown(
            """
            ---

            # 2. The Project Question

            The project is not trying to answer "who is the best tennis player?" That would be too broad.

            The narrower and better portfolio question is:

            > **Can return accuracy against body serves, separated by serve-speed zone, reveal meaningful player archetypes that relate to return-point performance?**

            That question works well because it has a clear stakeholder: a coach, scout, player-development analyst, or opponent-preparation analyst.
            """
        ),
        markdown(
            """
            ---

            # 3. Data Pipeline at a Glance

            The pipeline converts raw Grand Slam point-level data into player-level scouting profiles.

            ```text
            Raw point data
               -> keep body serves with speed and return-depth information
               -> split body serves into slow / medium / fast speed bins
               -> compute each player's return accuracy in each bin
               -> cluster players with similar three-bin profiles
               -> compare clusters to return-point win percentage
            ```

            The pipeline uses the 2017-2024 subset by default. This keeps the project aligned with the original capstone scripts and avoids mixing in earlier files with less consistent coverage.
            """
        ),
        code(
            """
            summary = pd.DataFrame({
                "Item": [
                    "Analysis window",
                    "Matches processed",
                    "Body-serve rows used for RAAVBSS",
                    "Clustered player profiles",
                    "Players in final comparison table",
                    "Final number of clusters",
                ],
                "Value": ["2017-2024", "6,127", "237,201", f"{len(players):,}", f"{len(comparison):,}", "7"],
            })
            summary
            """
        ),
        markdown(
            """
            ---

            # 4. What RAAVBSS Measures

            **RAAVBSS** stands for **Return Accuracy Across Varying Body Serve Speeds**.

            For each player, the metric stores three numbers:

            - `ras_slow`: return accuracy against slower body serves
            - `ras_medium`: return accuracy against medium-speed body serves
            - `ras_fast`: return accuracy against faster body serves

            The important idea is the **shape** across those three values. A player who is strong at all three speeds is different from a player who is strong against slow body serves but drops sharply against fast ones.
            """
        ),
        code(
            """
            thresholds_display = thresholds.copy()
            thresholds_display["speed_range_mph"] = (
                thresholds_display["min_speed_mph"].round(0).astype(int).astype(str)
                + "-"
                + thresholds_display["max_speed_mph"].round(0).astype(int).astype(str)
            )
            thresholds_display
            """
        ),
        code(
            """
            fig = px.bar(
                thresholds_display,
                x="speed_bin",
                y="n_body_serves",
                color="tour",
                barmode="group",
                text="speed_range_mph",
                labels={"speed_bin": "Serve speed bin", "n_body_serves": "Body serves", "tour": "Tour"},
                title="Body-serve speed bins are defined separately for ATP and WTA",
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(yaxis_tickformat=",")
            fig.show()
            """
        ),
        markdown(
            """
            **How to read the chart above:** each bar is the number of body serves in that speed group. The label on the bar shows the miles-per-hour range. The speed bins are separate for ATP and WTA because serve speed distributions differ by tour.
            """
        ),
        markdown(
            """
            ---

            # 5. From Model Clusters to Scouting Profiles

            The clustering model groups players who have similar RAAVBSS shapes. A portfolio reader should not have to remember "Cluster 1" or "Cluster 6," so this notebook adds plain-English labels.
            """
        ),
        code(
            """
            CLUSTER_STORIES = {
                0: ("Slow-Serve Specialists, Pace Vulnerable", "Most comfortable when body serves are slower, with accuracy dropping as pace rises."),
                1: ("All-Speed Return Anchors", "The strongest profile: high return accuracy across slow, medium, and fast body serves."),
                2: ("Medium-Speed Leaners", "A small group that looks best against medium-speed body serves, but has weaker outcome translation."),
                3: ("High Accuracy, Slight Fast-Serve Drop", "Strong overall returners whose accuracy falls most on fast body serves."),
                4: ("Fast-Serve Resilient Returners", "Players who hold up relatively well against faster body serves."),
                5: ("Sharp Pace Drop-Off", "Excellent on slow body serves but substantially weaker as speed increases."),
                6: ("Solid but Pace Sensitive", "A large middle group with solid accuracy and a visible decline against faster body serves."),
            }

            def story_name(cluster):
                if pd.isna(cluster):
                    return "Not clustered"
                return CLUSTER_STORIES[int(cluster)][0]

            def story_note(cluster):
                if pd.isna(cluster):
                    return "Did not meet clustering thresholds"
                return CLUSTER_STORIES[int(cluster)][1]

            profiles["story_label"] = profiles["cluster"].map(story_name)
            profiles["story_note"] = profiles["cluster"].map(story_note)
            players["story_label"] = players["cluster"].map(story_name)
            comparison["story_label"] = comparison["cluster"].map(story_name)

            profile_table = profiles[["cluster", "story_label", "n_players", "ras_slow", "ras_medium", "ras_fast", "return_win_pct", "story_note"]].copy()
            for col in ["ras_slow", "ras_medium", "ras_fast", "return_win_pct"]:
                profile_table[col] = (profile_table[col] * 100).round(1)
            profile_table.rename(columns={
                "cluster": "Cluster",
                "story_label": "Plain-English profile",
                "n_players": "Players",
                "ras_slow": "Slow return accuracy %",
                "ras_medium": "Medium return accuracy %",
                "ras_fast": "Fast return accuracy %",
                "return_win_pct": "Return point win %",
                "story_note": "How to interpret it",
            })
            """
        ),
        code(
            """
            profile_long = profiles.melt(
                id_vars=["cluster", "story_label", "n_players", "return_win_pct"],
                value_vars=["ras_slow", "ras_medium", "ras_fast"],
                var_name="speed_bin",
                value_name="return_accuracy",
            )
            profile_long["speed_bin"] = profile_long["speed_bin"].str.replace("ras_", "", regex=False).str.title()
            profile_long["return_accuracy_pct"] = profile_long["return_accuracy"] * 100
            profile_long["cluster_story"] = profile_long["cluster"].astype(int).astype(str) + ": " + profile_long["story_label"]

            fig = px.line(
                profile_long,
                x="speed_bin",
                y="return_accuracy_pct",
                color="cluster_story",
                markers=True,
                labels={"speed_bin": "Body-serve speed", "return_accuracy_pct": "Return accuracy (%)", "cluster_story": "Cluster profile"},
                title="RAAVBSS profile shapes: how return accuracy changes as body serves get faster",
            )
            fig.update_layout(yaxis_range=[75, 100])
            fig.show()
            """
        ),
        markdown(
            """
            **How to read the chart above:** a flatter line means a player group is more adaptable across speeds. A steep downward line means the group becomes less accurate as body serves get faster.
            """
        ),
        markdown(
            """
            ---

            # 6. The Most Important Portfolio Result

            The strongest profile is not just a chart pattern. It also connects to a better return-point outcome.

            That matters because **return accuracy** and **winning the point** are related but not identical. Getting the return back is the first job; winning the point is the bigger result.
            """
        ),
        code(
            """
            outcomes = profiles.copy()
            outcomes["story_label"] = outcomes["cluster"].map(story_name)
            outcomes["cluster_story"] = outcomes["cluster"].astype(int).astype(str) + ": " + outcomes["story_label"]
            outcomes["return_win_pct_display"] = outcomes["return_win_pct"] * 100
            outcomes = outcomes.sort_values("return_win_pct", ascending=False)

            fig = px.bar(
                outcomes,
                x="cluster_story",
                y="return_win_pct_display",
                color="cluster_story",
                labels={"cluster_story": "Cluster profile", "return_win_pct_display": "Return point win (%)"},
                title="Do RAAVBSS profiles connect to return-point outcomes?",
            )
            fig.update_layout(showlegend=False, xaxis_tickangle=-25)
            fig.show()

            best = outcomes.iloc[0]
            print(f"Best return-outcome profile: Cluster {int(best.cluster)} - {best.story_label}")
            print(f"Average return point win percentage: {best.return_win_pct * 100:.1f}%")
            """
        ),
        markdown(
            """
            **Interpretation:** Cluster 1, the all-speed return group, has the best average return point win percentage. That supports the practical value of RAAVBSS: the metric is not just creating arbitrary shapes; the strongest all-speed profile also shows the strongest return outcome.
            """
        ),
        markdown(
            """
            ---

            # 7. Player-Level Examples

            The model becomes easier to understand when we connect it back to players. The table below shows players with cluster assignments and enough return points for outcome comparison.
            """
        ),
        code(
            """
            player_examples = comparison.dropna(subset=["cluster"]).copy()
            for col in ["ras_slow", "ras_medium", "ras_fast", "return_win_pct", "serve_win_pct"]:
                player_examples[col] = (player_examples[col] * 100).round(1)
            player_examples = player_examples.sort_values(["return_win_pct", "body_return_pts"], ascending=False)
            player_examples[[
                "tour", "player_name", "cluster", "story_label", "ras_slow", "ras_medium", "ras_fast",
                "return_win_pct", "serve_win_pct", "body_return_pts",
            ]].head(25).rename(columns={
                "tour": "Tour",
                "player_name": "Player",
                "cluster": "Cluster",
                "story_label": "Scouting profile",
                "ras_slow": "Slow return accuracy %",
                "ras_medium": "Medium return accuracy %",
                "ras_fast": "Fast return accuracy %",
                "return_win_pct": "Return point win %",
                "serve_win_pct": "Serve point win %",
                "body_return_pts": "Body serves returned",
            })
            """
        ),
        markdown(
            """
            ---

            # 8. Player Similarity Map

            This PCA chart compresses the three RAAVBSS values into a two-dimensional map.

            Players near each other have similar body-serve return profiles. The colors are clusters, and the marker shapes separate ATP and WTA.
            """
        ),
        code(
            """
            fig = px.scatter(
                players,
                x="PC1",
                y="PC2",
                color="story_label",
                symbol="tour",
                hover_name="player_name",
                hover_data={"ras_slow": ":.2f", "ras_medium": ":.2f", "ras_fast": ":.2f", "body_return_pts": True, "PC1": False, "PC2": False},
                labels={"story_label": "Scouting profile"},
                title="Player similarity map based on RAAVBSS",
            )
            fig.show()
            """
        ),
        markdown(
            """
            If you are viewing this notebook on GitHub and the interactive Plotly chart does not render, the static version below shows the same idea.

            ![PCA view of returner archetypes](../data/processed/pca_returner_archetypes.png)
            """
        ),
        markdown(
            """
            ---

            # 9. Why Seven Clusters?

            The original capstone framed the final model around `k=7`. The pipeline still computes silhouette scores for several possible values of `k` so the choice is visible.

            A higher silhouette score usually means cleaner separation. In this project, `k=2` separates the data most cleanly, but `k=7` gives a more detailed scouting taxonomy. This is a tradeoff between **statistical simplicity** and **interpretive detail**.
            """
        ),
        code(
            """
            fig = px.line(
                silhouette,
                x="k",
                y="silhouette",
                markers=True,
                labels={"k": "Number of clusters", "silhouette": "Silhouette score"},
                title="Cluster selection check: simpler models separate more cleanly, k=7 gives more scouting detail",
            )
            fig.show()
            """
        ),
        markdown("![K selection silhouette plot](../data/processed/k_selection_silhouette.png)"),
        markdown(
            """
            ---

            # 10. Statistical Evidence

            The statistical tests compare whether return point win percentage differs across clusters.

            The important portfolio-friendly interpretation:

            - The combined dataset shows clear return-outcome differences across clusters.
            - ATP shows some separation across clusters.
            - WTA does not show the same separation under the current thresholds.

            That does **not** mean the metric is invalid for WTA. It means the current feature definition, thresholds, or sample composition may need further tuning for that subset.
            """
        ),
        code(
            """
            tests_display = tests.copy()
            tests_display["statistic"] = tests_display["statistic"].round(3)
            tests_display["p_value"] = tests_display["p_value"].map(lambda x: f"{x:.4g}")
            tests_display.rename(columns={"dataset": "Dataset", "test": "Test", "statistic": "Statistic", "p_value": "p-value"})
            """
        ),
        markdown(
            """
            ---

            # 11. What the Project Shows

            ## Strongest evidence

            RAAVBSS creates interpretable player profiles from point-level data, and the best all-speed return profile also has the strongest return-point win percentage.

            ## Why this is a good portfolio project

            This is more than a notebook of charts. It demonstrates:

            - domain-specific feature engineering
            - data cleaning from raw sports event files
            - unsupervised learning
            - model interpretation
            - outcome validation
            - communication for nontechnical or non-tennis audiences

            ## Honest limitations

            - The analysis is descriptive, not causal.
            - Return accuracy is proxied from recorded return-depth data.
            - Player names from the source data are not perfectly standardized, which creates duplicate-looking names in some cases.
            - The `k=7` clustering choice favors scouting detail over maximum silhouette score.
            - The metric should be framed as a return-tactics tool, not an all-purpose player ranking.
            """
        ),
        markdown(
            """
            ---

            # 12. Final Portfolio Takeaway

            **Best public-facing takeaway:**

            > I built RAAVBSS, a tennis return-adaptability metric that turns Grand Slam point-level data into scouting-style player profiles. The project uses feature engineering, K-Means clustering, PCA, statistical testing, and an interactive dashboard to show which returner archetypes handle body serves across speed zones and whether those profiles connect to return-point outcomes.

            That is the story a recruiter or portfolio reviewer should leave with.
            """
        ),
    ]

    nb.cells = cells
    nbf.write(nb, NOTEBOOK)


if __name__ == "__main__":
    build_notebook()
    print(NOTEBOOK)
