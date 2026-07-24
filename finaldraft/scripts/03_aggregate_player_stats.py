import pandas as pd
from scipy.stats import ttest_ind, f_oneway

df = pd.read_csv("D:/school programs/TennisStrategyProject/mydata/cluster_comparison_stats_cleaned.csv")
df = df.dropna(subset=['return_win_pct', 'serve_win_pct', 'total_win_pct', 'cluster'])

# Return %
ret_scores = df.groupby('cluster')['return_win_pct'].mean()
top_ret = ret_scores.idxmax()
ttest_ret = ttest_ind(df[df['cluster']==top_ret]['return_win_pct'], df[df['cluster']!=top_ret]['return_win_pct'], equal_var=False)
anova_ret = f_oneway(*[g['return_win_pct'] for _, g in df.groupby('cluster')])

# Serve %
srv_scores = df.groupby('cluster')['serve_win_pct'].mean()
top_srv = srv_scores.idxmax()
ttest_srv = ttest_ind(df[df['cluster']==top_srv]['serve_win_pct'], df[df['cluster']!=top_srv]['serve_win_pct'], equal_var=False)
anova_srv = f_oneway(*[g['serve_win_pct'] for _, g in df.groupby('cluster')])

# Total %
tot_scores = df.groupby('cluster')['total_win_pct'].mean()
top_tot = tot_scores.idxmax()
ttest_tot = ttest_ind(df[df['cluster']==top_tot]['total_win_pct'], df[df['cluster']!=top_tot]['total_win_pct'], equal_var=False)
anova_tot = f_oneway(*[g['total_win_pct'] for _, g in df.groupby('cluster')])

print("\nTop Cluster Comparison Stats:")
print(f"Return Win %: Cluster {top_ret} - Mean {ret_scores[top_ret]:.4f}, T p={ttest_ret.pvalue:.5f}, ANOVA p={anova_ret.pvalue:.5f}")
print(f"Serve Win %: Cluster {top_srv} - Mean {srv_scores[top_srv]:.4f}, T p={ttest_srv.pvalue:.5f}, ANOVA p={anova_srv.pvalue:.5f}")
print(f"Total Win %: Cluster {top_tot} - Mean {tot_scores[top_tot]:.4f}, T p={ttest_tot.pvalue:.5f}, ANOVA p={anova_tot.pvalue:.5f}")
