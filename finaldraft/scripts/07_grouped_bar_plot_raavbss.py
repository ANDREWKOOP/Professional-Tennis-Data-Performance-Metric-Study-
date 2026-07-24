# 06_grouped_bar_plot_raavbss.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

data_path = r"D:/school programs/TennisStrategyProject/mydata"

def plot_raavbss_bar(data_file, label):
    df = pd.read_csv(data_file)

    df_melted = df.melt(
        id_vars=['player_name', 'cluster'],
        value_vars=['ras_slow', 'ras_medium', 'ras_fast'],
        var_name='Serve Speed Bin',
        value_name='Return Accuracy Score'
    )

    df_melted['Serve Speed Bin'] = df_melted['Serve Speed Bin'].str.replace('ras_', '').str.title()

    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=df_melted,
        x='cluster',
        y='Return Accuracy Score',
        hue='Serve Speed Bin',
        palette='Set2'
    )
    plt.title(f"{label} RAAVBSS by Cluster")
    plt.ylim(0, 1.0)
    plt.xlabel("Cluster (Returner Archetype)")
    plt.ylabel("Return Accuracy Score")
    plt.legend(title="Serve Speed Bin")
    plt.tight_layout()
    plt.savefig(os.path.join(data_path, f"{label.lower()}_raavbss_barplot.png"))
    plt.show()

# === RUN FOR ATP & WTA
plot_raavbss_bar(os.path.join(data_path, "clustered_atp.csv"), "ATP")
plot_raavbss_bar(os.path.join(data_path, "clustered_wta.csv"), "WTA")
