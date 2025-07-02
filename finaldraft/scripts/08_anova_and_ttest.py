
# 07_anova_and_ttest_by_gender.py

import pandas as pd
from scipy.stats import ttest_ind, f_oneway
import matplotlib.pyplot as plt
import seaborn as sns
import os

data_path = r"D:/school programs/TennisStrategyProject/mydata"

def run_anova_tests(file_path, label):
    df = pd.read_csv(file_path)

    cluster_0 = df[df['cluster'] == 0]['return_win_pct']
    non_clustered = df[df['cluster'].isna()]['return_win_pct']

    # T-Test
    t_stat, p_val = ttest_ind(cluster_0, non_clustered, equal_var=False)
    print(f"\n{label.upper()} T-Test: Cluster 0 vs Non-Clustered")
    print(f"T = {t_stat:.3f}, P = {p_val:.5f}")

    # ANOVA
    clustered = df[df['cluster'].notna()]
    groups = [g['return_win_pct'].dropna() for _, g in clustered.groupby('cluster')]
    f_stat, p_anova = f_oneway(*groups)
    print(f"{label.upper()} ANOVA: Return Win % by Cluster → F = {f_stat:.3f}, P = {p_anova:.5f}")

    # Boxplot
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=clustered, x='cluster', y='return_win_pct')
    plt.title(f"{label} Return Point Win % by Cluster")
    plt.ylabel("Return Win Percentage")
    plt.xlabel("Cluster")
    plt.tight_layout()
    plt.savefig(os.path.join(data_path, f"{label.lower()}_return_win_by_cluster_boxplot.png"))
    plt.show()

# === Run for ATP & WTA
run_anova_tests(os.path.join(data_path, "cluster_comparison_atp.csv"), "ATP")
run_anova_tests(os.path.join(data_path, "cluster_comparison_wta.csv"), "WTA")
