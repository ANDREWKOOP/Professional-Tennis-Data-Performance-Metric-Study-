# Tennis Capstone Generated Summary

- Analysis window: 2017-2024
- Matches processed: 6,127
- Players in comparison dataset: 334
- Players with assigned RAAVBSS clusters: 255

## Speed Bins

| tour   | speed_bin   |   min_speed_mph |   max_speed_mph |   n_body_serves |
|:-------|:------------|----------------:|----------------:|----------------:|
| ATP    | slow        |              60 |              94 |           45600 |
| ATP    | medium      |              95 |             109 |           45261 |
| ATP    | fast        |             110 |             147 |           44909 |
| WTA    | slow        |              60 |              84 |           35096 |
| WTA    | medium      |              85 |              95 |           32765 |
| WTA    | fast        |              96 |             152 |           33570 |

## Cluster Profiles

|   cluster |   n_players |   ras_slow |   ras_medium |   ras_fast |   return_win_pct |   serve_win_pct |   total_win_pct | archetype                     |
|----------:|------------:|-----------:|-------------:|-----------:|-----------------:|----------------:|----------------:|:------------------------------|
|         0 |          21 |   0.912554 |     0.86241  |   0.836709 |         0.343378 |        0.652432 |        0.497549 | Strong slow-speed returners   |
|         1 |          42 |   0.971612 |     0.97016  |   0.962994 |         0.420948 |        0.58933  |        0.505121 | Elite adaptive returners      |
|         2 |           7 |   0.880373 |     0.907571 |   0.892229 |         0.33477  |        0.637724 |        0.488741 | Strong medium-speed returners |
|         3 |          64 |   0.977905 |     0.958359 |   0.922585 |         0.391915 |        0.621044 |        0.505961 | Elite adaptive returners      |
|         4 |          51 |   0.958092 |     0.91891  |   0.935051 |         0.395201 |        0.616049 |        0.505269 | Elite adaptive returners      |
|         5 |          10 |   0.966207 |     0.892453 |   0.807939 |         0.348276 |        0.640712 |        0.494851 | Strong slow-speed returners   |
|         6 |          60 |   0.944116 |     0.92861  |   0.876773 |         0.371912 |        0.627765 |        0.49988  | Elite adaptive returners      |

## Statistical Tests

| dataset   | test                            |   statistic |     p_value |
|:----------|:--------------------------------|------------:|------------:|
| ATP       | ANOVA return_win_pct by cluster |    2.34124  | 0.0345582   |
| ATP       | Cluster 0 vs other clusters     |   -1.75024  | 0.0936235   |
| WTA       | ANOVA return_win_pct by cluster |    0.394526 | 0.757217    |
| Combined  | ANOVA return_win_pct by cluster |   14.8794   | 1.59525e-14 |
| Combined  | Cluster 0 vs other clusters     |   -5.47278  | 9.82844e-06 |

## Key Artifacts

- `data/processed/player_rse_clusters_k7.csv`
- `data/processed/cluster_comparison_stats_cleaned.csv`
- `data/processed/cluster_profiles.csv`
- `data/processed/statistical_tests.csv`
- `data/processed/*.png`