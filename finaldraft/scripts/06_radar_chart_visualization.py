import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Load data
df = pd.read_csv("D:/school programs/TennisStrategyProject/mydata/cluster_comparison_stats_cleaned.csv")

# Define radar chart labels and axis setup
labels = ['ras_slow', 'ras_medium', 'ras_fast']
num_vars = len(labels)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]

# Cluster labels for titling
cluster_titles = {
    0: "Cluster 0: Balanced Returners",
    1: "Cluster 1: Speed-Sensitive Returners",
    2: "Cluster 2: Medium-Reliant Returners",
    3: "Cluster 3: Serve-Dominant Players",
    4: "Cluster 4: All-Around Returners",
    5: "Cluster 5: Elite Adaptive Returners",
    6: "Cluster 6: Low Efficiency Returners"
}

# Create subplots
fig, axes = plt.subplots(nrows=2, ncols=4, figsize=(22, 12), subplot_kw=dict(polar=True))
axes = axes.flatten()

# Plot each cluster
for i in range(7):
    ax = axes[i]
    cluster_data = df[df['cluster'] == i]
    means = cluster_data[labels].mean().tolist()
    values = means + means[:1]

    # Plot individual player data
    for _, row in cluster_data[labels].iterrows():
        individual = row.tolist() + row.tolist()[:1]
        ax.plot(angles, individual, color='gray', alpha=0.3, linewidth=0.8)

    # Plot average line
    ax.plot(angles, values, color='blue', linewidth=2)
    ax.fill(angles, values, color='blue', alpha=0.25)
    
    # Axis setup
    ax.set_ylim(0, 1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(['Slow (RAS)', 'Medium (RAS)', 'Fast (RAS)'], fontsize=10)
    ax.set_yticklabels([])
    ax.spines['polar'].set_visible(False)
    ax.set_title(cluster_titles[i], fontsize=12, y=1.1 if i < 4 else -0.35)

    # Annotate means
    for angle, val in zip(angles[:-1], values[:-1]):
        ax.text(angle, val + 0.05, f"{val:.2f}", ha='center', va='center', fontsize=9, color='black')

# Remove the unused subplot
fig.delaxes(axes[7])

# Super title and save
fig.suptitle("Radar Plots of Average Return Accuracy Scores (RAS) by Cluster with Individual Players", fontsize=18, y=1.08)
plt.tight_layout()
output_path = "D:/school programs/TennisStrategyProject/mydata/annotated_radar_plot_with_individuals.png"
plt.savefig(output_path, bbox_inches='tight')
plt.show()
