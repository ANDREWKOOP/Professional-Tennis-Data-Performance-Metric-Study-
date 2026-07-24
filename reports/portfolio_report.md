# Quantifying Return Adaptability in Professional Tennis

## Portfolio Summary

This capstone project introduces **RAAVBSS**: **Return Accuracy Across Varying Body Serve Speeds**. The metric evaluates how accurately professional tennis players return body serves across slow, medium, and fast serve-speed zones.

The project uses point-level and match-level tennis data, player-level feature engineering, K-Means clustering, PCA, statistical tests, and visual outputs to identify returner archetypes and evaluate whether those archetypes align with return-point and overall point-winning performance.

The clearest way to review the project is now:

1. Open `notebooks/tennis_capstone_story.ipynb` for the full guided walkthrough.
2. Run `run_dashboard.ps1` for the interactive Streamlit dashboard.
3. Use `reports/generated_summary.md` for a compact result summary.

## Suggested Profile Blurb

Developed RAAVBSS, a tennis return-adaptability metric using Grand Slam point-level data, K-Means clustering, PCA, and statistical testing to identify returner archetypes and evaluate whether those archetypes align with match-performance outcomes.

## Stakeholder Framing

The intended stakeholder is a tennis coach, scout, analyst, or player-development staff member who wants a more tactical view of return performance than aggregate return percentage alone.

The practical question is:

**Can return accuracy against body serves, separated by serve-speed zone, reveal meaningful player archetypes that relate to return-point and overall point-winning performance?**

## What RAAVBSS Measures

RAAVBSS separates return accuracy into three body-serve speed bins:

- `ras_slow`: return accuracy on slower body serves
- `ras_medium`: return accuracy on medium-speed body serves
- `ras_fast`: return accuracy on faster body serves

The project value comes from comparing the pattern across the three bins. A player can be balanced, speed-sensitive, medium-reliant, consistently strong, or consistently weak. That shape is more useful for tactical analysis than one blended return metric.

## Workflow

1. Merge Grand Slam point-level and match-level data.
2. Engineer player-level RAAVBSS features.
3. Standardize RAAVBSS features.
4. Use K-Means clustering to identify returner archetypes.
5. Use PCA and profile plots to inspect cluster separation.
6. Merge cluster labels with serve, return, and total point-win outcomes.
7. Compare clusters using Welch t-tests and ANOVA.
8. Present outputs through radar charts, grouped bar plots, boxplots, violin-boxplots, and the RMarkdown report.

## Expected Outputs

The runnable pipeline generated these artifacts in `data/processed/`:

- `raavbss_radar_charts.png`
- `annotated_radar_plot_with_individuals.png`
- `atp_raavbss_barplot.png`
- `wta_raavbss_barplot.png`
- `atp_return_winrate_by_cluster_barplot.png`
- `wta_return_winrate_by_cluster_barplot.png`
- `atp_return_win_by_cluster_boxplot.png`
- `wta_return_win_by_cluster_boxplot.png`
- `violinbox_return_serve_by_cluster.png`

It also generates `pca_returner_archetypes.png`, `k_selection_silhouette.png`, `cluster_profiles.csv`, `statistical_tests.csv`, and `generated_summary.md`.

## Generated Results

- Analysis window: 2017-2024.
- Matches processed: 6,127.
- Body-serve rows used for RAAVBSS derivation: 237,201.
- Player RAAVBSS profiles clustered: 510.
- Players in the comparison dataset after the return-point threshold: 334.
- Final clustering setting: k=7.

The strongest cluster by return point win percentage was Cluster 1, labeled **Elite adaptive returners**, with high return accuracy across slow, medium, and fast body-serve speed bins.

The combined ANOVA found that return point win percentage differed across clusters. ATP showed a smaller but still notable cluster difference, while the WTA subset did not show the same level of separation under the current thresholds. This should be framed as evidence that the metric is analytically useful, not as a causal claim.

## Remaining Public-Portfolio Cleanup

- Render `reports/tennis_capstone_report.Rmd` to HTML in RStudio once R/RMarkdown is available.
- Move or upload this local project structure into the GitHub repository.
- Keep `DATA_PROVENANCE.md` visible because the Jeff Sackmann data is CC BY-NC-SA 4.0.
- Consider adding a short README image preview using the PCA plot or radar chart.

## Limitations

RAAVBSS should be framed as a tactical return metric, not a causal claim about winning. If one cluster has a higher return win percentage, that association supports the metric's practical relevance, but it does not prove the RAAVBSS profile caused the result.

The analysis also depends on player inclusion thresholds, the selected year range, body-serve definitions, serve-speed binning, and the selected number of clusters. These assumptions should be visible in the final rendered report.

## Best Public-Facing Takeaway

RAAVBSS turns granular tennis point data into an interpretable scouting-style metric. The project demonstrates data cleaning, sports-specific feature engineering, unsupervised learning, model interpretation, statistical validation, and clear communication of limitations.

For a portfolio, the strongest story is not just "I clustered tennis players." It is:

**I created a sport-specific metric, used machine learning to discover player archetypes, and tested whether those archetypes connected to meaningful performance outcomes.**

## Reviewer-Friendly Entry Points

- `notebooks/tennis_capstone_story.ipynb`: start here if the reader does not know tennis.
- `dashboard/streamlit_app.py`: interactive version of the same story with filters and player exploration.
- `scripts/tennis_capstone_pipeline.py`: reproducible data pipeline from public raw files to final outputs.
- `DATA_PROVENANCE.md`: source, license, and metric derivation notes.
