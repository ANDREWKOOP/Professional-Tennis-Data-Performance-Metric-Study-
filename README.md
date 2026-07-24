# RAAVBSS Tennis Return Adaptability Dashboard

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://q7cjybmtckqnsqdh7rtouq.streamlit.app/)

**Live app:** https://q7cjybmtckqnsqdh7rtouq.streamlit.app/

## Project Summary

This capstone project introduces **RAAVBSS**: **Return Accuracy Across Varying Body Serve Speeds**.

In plain English, the project asks:

> When a tennis player receives a serve aimed at their body, can they still return the ball accurately as the serve gets faster?

The project turns Grand Slam point-level tennis data into scouting-style player profiles using feature engineering, K-Means clustering, PCA visualization, and outcome validation against return-point win percentage.

## Best Way to Explore

1. **Start with the live dashboard:**  
   https://q7cjybmtckqnsqdh7rtouq.streamlit.app/

2. **Read the guided notebook:**  
   [`notebooks/tennis_capstone_story.ipynb`](notebooks/tennis_capstone_story.ipynb)

3. **Review the compact result summary:**  
   [`reports/generated_summary.md`](reports/generated_summary.md)

## What the Dashboard Shows

- A tennis glossary for non-tennis readers.
- RAAVBSS speed bins for ATP and WTA data.
- Plain-English returner archetypes.
- Cluster-level return accuracy profiles.
- Return point win percentage by cluster.
- A player explorer table.
- A PCA similarity map of player return profiles.
- Evidence, caveats, and statistical test summaries.

## Key Result

The strongest profile, **All-Speed Return Anchors**, maintains high return accuracy across slow, medium, and fast body serves and also has the strongest average return-point win percentage.

That supports the practical value of RAAVBSS as a tactical return-analysis metric rather than just a clustering exercise.

## Data and Methods

- **Data source:** Jeff Sackmann Grand Slam point-by-point tennis data, 2017-2024 subset.
- **Metric:** RAAVBSS, derived from body serves with recorded serve speed and return-depth information.
- **Modeling:** K-Means clustering on `ras_slow`, `ras_medium`, and `ras_fast`.
- **Validation:** Cluster comparisons using return point win percentage, ANOVA, and t-tests.

See [`DATA_PROVENANCE.md`](DATA_PROVENANCE.md) for source and license details.

## Repository Guide

```text
dashboard/streamlit_app.py              Streamlit dashboard source
streamlit_app.py                        Streamlit Cloud entrypoint
notebooks/tennis_capstone_story.ipynb   Guided portfolio notebook
data/processed/                         Dashboard-ready CSVs and charts
scripts/tennis_capstone_pipeline.py     Reproducible data pipeline
reports/generated_summary.md            Generated result summary
DATA_PROVENANCE.md                      Data source and license notes
```

## Reproducibility

The live dashboard uses committed summary CSVs and image artifacts from `data/processed/`.

To rebuild the processed data locally from raw public files:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_tennis_project.ps1
```

`requirements.txt` is intentionally small for Streamlit Cloud. The full local pipeline environment is in `requirements-pipeline.txt`.
