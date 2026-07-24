import pandas as pd
import os

# Paths
base = "D:/school programs/TennisStrategyProject/mydata"
stats = pd.read_csv(os.path.join(base, "aggregated_player_stats.csv"))
clusters = pd.read_csv(os.path.join(base, "player_rse_clusters_k7.csv"))

# Clean merge
stats['player'] = stats['player'].str.strip().str.lower()
clusters['player_name'] = clusters['player_name'].str.strip().str.lower()
merged = stats.merge(clusters, left_on='player', right_on='player_name', how='left')

# Compute win %s
merged['return_win_pct'] = merged['return_pts_won'] / merged['return_pts']
merged['serve_win_pct'] = merged['serve_pts_won'] / merged['serve_pts']
merged['total_win_pct'] = (merged['return_pts_won'] + merged['serve_pts_won']) / (merged['return_pts'] + merged['serve_pts'])

# Final output
final = merged.drop(columns=['player_name']).rename(columns={'player': 'player_name'})
final = final[final['return_pts'] >= 1000]
final.to_csv(os.path.join(base, "cluster_comparison_stats_cleaned.csv"), index=False)
