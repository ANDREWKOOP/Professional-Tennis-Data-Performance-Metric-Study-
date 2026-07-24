import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

# Load RAAVBSS player dataset
ras = pd.read_csv("D:/school programs/TennisStrategyProject/mydata/player_rse_clusters.csv")
features = ['ras_slow', 'ras_medium', 'ras_fast']
X = StandardScaler().fit_transform(ras[features])

# Run k=2 to 12 and choose best silhouette
k_range = range(2, 13)
sil_scores, inertias = [], []
for k in k_range:
    km = KMeans(n_clusters=k, random_state=42)
    preds = km.fit_predict(X)
    sil_scores.append(silhouette_score(X, preds))
    inertias.append(km.inertia_)

optimal_k = k_range[np.argmax(sil_scores)]
print(f"Optimal k: {optimal_k}")

# Final clustering with k=7 (or optimal_k)
kmeans = KMeans(n_clusters=7, random_state=42)
ras['cluster'] = kmeans.fit_predict(X)
ras.to_csv("D:/school programs/TennisStrategyProject/mydata/player_rse_clusters_k7.csv", index=False)

# Visualizations (barplot and PCA)
cluster_avg = ras.groupby('cluster')[features].mean().reset_index()
melted = cluster_avg.melt(id_vars='cluster', var_name='Speed Bin', value_name='Return Accuracy')

plt.figure(figsize=(10, 6))
sns.barplot(data=melted, x='cluster', y='Return Accuracy', hue='Speed Bin')
plt.title("RAAVBSS Cluster Archetypes (k=7)")
plt.tight_layout()
plt.show()

pca = PCA(n_components=2)
coords = pca.fit_transform(X)
ras['PC1'], ras['PC2'] = coords[:, 0], coords[:, 1]

plt.figure(figsize=(10, 6))
sns.scatterplot(data=ras, x='PC1', y='PC2', hue='cluster', palette='tab10', s=100)
plt.title("PCA View of Returner Archetypes (k=7)")
plt.tight_layout()
plt.show()
