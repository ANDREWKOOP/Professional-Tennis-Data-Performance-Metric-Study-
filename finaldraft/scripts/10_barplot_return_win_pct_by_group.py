import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Reload the dataset
file_path = "D:/school programs/TennisStrategyProject/mydata/cluster_comparison_stats_cleaned.csv"
df = pd.read_csv(file_path)

# Drop missing values and ensure proper data types
df = df.dropna(subset=["return_win_pct", "serve_win_pct", "cluster"])
df["cluster"] = df["cluster"].astype(int)

# Setup figure for side-by-side violin-boxplots
fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)

# Violin + Boxplot for Return Win %
sns.violinplot(data=df, x="cluster", y="return_win_pct", inner=None, ax=axes[0], palette="Blues", linewidth=0.8)
sns.boxplot(data=df, x="cluster", y="return_win_pct", ax=axes[0], width=0.2, color="black", showcaps=True, boxprops={'facecolor':'none'})
axes[0].set_title("Return Win Percentage by Cluster")
axes[0].set_xlabel("Cluster")
axes[0].set_ylabel("Win Percentage")
axes[0].grid(True)

# Violin + Boxplot for Serve Win %
sns.violinplot(data=df, x="cluster", y="serve_win_pct", inner=None, ax=axes[1], palette="Oranges", linewidth=0.8)
sns.boxplot(data=df, x="cluster", y="serve_win_pct", ax=axes[1], width=0.2, color="black", showcaps=True, boxprops={'facecolor':'none'})
axes[1].set_title("Serve Win Percentage by Cluster")
axes[1].set_xlabel("Cluster")
axes[1].set_ylabel("")  # No redundant y-label
axes[1].grid(True)

plt.suptitle("Return and Serve Win % by Cluster (Violin-Boxplot)", fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.95])

# Save the combined violin-boxplot
violin_boxplot_path = "D:/school programs/TennisStrategyProject/mydata/violinbox_return_serve_by_cluster.png"
plt.savefig(violin_boxplot_path)
violin_boxplot_path
