import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df = pd.read_csv("D:/school programs/TennisStrategyProject/mydata/cluster_comparison_stats_cleaned.csv")
means = df.groupby('cluster')[['ras_slow', 'ras_medium', 'ras_fast']].mean()

labels = ['Slow', 'Medium', 'Fast']
angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
angles += angles[:1]

fig, axs = plt.subplots(nrows=2, ncols=4, figsize=(18, 10), subplot_kw=dict(polar=True))
axs = axs.flatten()

for i, cluster in enumerate(means.index):
    values = means.loc[cluster].tolist() + [means.loc[cluster].tolist()[0]]
    ax = axs[i]
    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_title(f"Cluster {cluster}")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_ylim(0.4, 0.8)

for j in range(len(means), len(axs)):
    fig.delaxes(axs[j])

plt.tight_layout()
plt.savefig("D:/school programs/TennisStrategyProject/mydata/raavbss_radar_charts.png")
