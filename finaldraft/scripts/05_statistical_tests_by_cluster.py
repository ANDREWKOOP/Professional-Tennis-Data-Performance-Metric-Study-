# 04_statistical_tests_by_cluster_gendered.py

import pandas as pd
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
import seaborn as sns
import os

data_path = r"D:/school programs/TennisStrategyProject/mydata"

def run_ttest_and_plot(file_path, label):
    df = pd.read_csv(file_path)

    cluster_0 = df[df['cluster'] == 0]['return_win_pct']
    other_clusters = df[(df['cluster'].notna()) & (df['cluster'] != 0)]['return_win_pct']
    non_clustered = df[df['cluster'].isna()]['return_win_pct']

    ttest_vs_other = ttest_ind(cluster_0, other_clusters, equal_var=False)
    ttest_vs_non = ttest_ind(cluster_0, non_clustered, equal_var=False)

    print(f"\n{label.upper()} T-Test Results")
    print("Cluster 0 vs. Other Clusters:", ttest_vs_other)
    print("Cluster 0 vs. Non-Clustered:", ttest_vs_non)

    # Visualization
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='cluster', y='return_win_pct', ci=95, palette='viridis')
    plt.axhline(y=cluster_0.mean(), color='r', linestyle='--', label='Cluster 0 Avg')
    plt.title(f"{label.upper()}: Return Point Win % by Cluster (95% CI)")
    plt.ylabel("Return Win %")
    plt.xlabel("Cluster (NaN = Not Clustered)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(data_path, f"{label.lower()}_return_winrate_by_cluster_barplot.png"))
    plt.show()

# === Run on both ATP and WTA
run_ttest_and_plot(os.path.join(data_path, "cluster_comparison_atp.csv"), "ATP")
run_ttest_and_plot(os.path.join(data_path, "cluster_comparison_wta.csv"), "WTA")
