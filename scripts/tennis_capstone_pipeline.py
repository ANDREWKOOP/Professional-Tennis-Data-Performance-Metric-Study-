from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import urllib.request
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


HF_API = "https://huggingface.co/api/datasets/Aneeshers/tennis-sackmann-archive/tree/main/slam_pointbypoint?recursive=false"
HF_RAW = "https://huggingface.co/datasets/Aneeshers/tennis-sackmann-archive/resolve/main/"
SLAMS = {"ausopen", "frenchopen", "usopen", "wimbledon"}
BODY_WIDTHS = {"B", "BC", "BW"}
SPEED_LABELS = ["slow", "medium", "fast"]


def request_json(url: str) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": "tennis-capstone-pipeline"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0:
        return
    req = urllib.request.Request(url, headers={"User-Agent": "tennis-capstone-pipeline"})
    with urllib.request.urlopen(req, timeout=120) as response:
        destination.write_bytes(response.read())


def list_slam_files(start_year: int, end_year: int) -> list[str]:
    items = request_json(HF_API)
    files: list[str] = []
    pattern = re.compile(r"^slam_pointbypoint/(\d{4})-([a-z]+)-(matches|points)\.csv$")
    for item in items:
        path = item.get("path", "")
        match = pattern.match(path)
        if not match:
            continue
        year = int(match.group(1))
        slam = match.group(2)
        if start_year <= year <= end_year and slam in SLAMS:
            files.append(path)
    return sorted(files)


def download_raw_data(raw_dir: Path, start_year: int, end_year: int) -> list[Path]:
    files = list_slam_files(start_year, end_year)
    if not files:
        raise RuntimeError("No matching Grand Slam point-by-point files were found.")

    downloaded: list[Path] = []
    for remote_path in files:
        target = raw_dir / Path(remote_path).name
        print(f"Downloading/checking {remote_path}")
        download_file(HF_RAW + remote_path, target)
        downloaded.append(target)

    data_dictionary = raw_dir / "data_dictionary.txt"
    download_file(HF_RAW + "slam_pointbypoint/data_dictionary.txt", data_dictionary)
    return downloaded


def infer_tour(match_num: object, match_id: object) -> str:
    match_num_text = "" if pd.isna(match_num) else str(match_num)
    digits = re.sub(r"\D", "", match_num_text)
    if digits:
        return "WTA" if int(digits[0]) == 2 else "ATP"
    match_text = "" if pd.isna(match_id) else str(match_id)
    last_token = match_text.split("-")[-1]
    return "WTA" if last_token.startswith("2") else "ATP"


def read_tournament_pair(points_path: Path, matches_path: Path) -> pd.DataFrame:
    points = pd.read_csv(points_path, low_memory=False)
    matches = pd.read_csv(matches_path, low_memory=False)

    keep_cols = [col for col in ["match_id", "year", "slam", "match_num", "player1", "player2", "round"] if col in matches.columns]
    matches = matches[keep_cols].copy()
    if "year" not in matches.columns:
        matches["year"] = int(points_path.name[:4])
    if "slam" not in matches.columns:
        matches["slam"] = points_path.name.split("-")[1]
    if "match_num" not in matches.columns:
        matches["match_num"] = matches["match_id"].astype(str).str.extract(r"-(\d+)$")[0]
    if "round" not in matches.columns:
        matches["round"] = ""

    merged = points.merge(matches, on="match_id", how="left")
    merged["tour"] = [infer_tour(num, mid) for num, mid in zip(merged["match_num"], merged["match_id"])]
    return merged


def load_merged_points(raw_dir: Path, processed_dir: Path) -> pd.DataFrame:
    point_files = sorted(raw_dir.glob("*-points.csv"))
    frames: list[pd.DataFrame] = []

    for points_path in point_files:
        matches_path = raw_dir / points_path.name.replace("-points.csv", "-matches.csv")
        if not matches_path.exists():
            print(f"Skipping {points_path.name}: missing {matches_path.name}")
            continue
        print(f"Reading {points_path.name}")
        frames.append(read_tournament_pair(points_path, matches_path))

    if not frames:
        raise RuntimeError("No point/match file pairs were available to process.")

    merged = pd.concat(frames, ignore_index=True)
    merged["PointServer"] = pd.to_numeric(merged.get("PointServer"), errors="coerce")
    merged["PointWinner"] = pd.to_numeric(merged.get("PointWinner"), errors="coerce")
    if "Speed_MPH" in merged.columns:
        merged["speed_mph"] = pd.to_numeric(merged["Speed_MPH"], errors="coerce")
    else:
        merged["speed_mph"] = pd.to_numeric(merged.get("Speed_KMH"), errors="coerce") * 0.621371

    merged["serve_width"] = merged.get("ServeWidth", "").astype(str).str.strip().str.upper()
    merged["return_depth"] = merged.get("ReturnDepth", "").astype(str).str.strip().str.upper()
    merged["server_name"] = np.where(merged["PointServer"] == 1, merged["player1"], np.where(merged["PointServer"] == 2, merged["player2"], np.nan))
    merged["returner_name"] = np.where(merged["PointServer"] == 1, merged["player2"], np.where(merged["PointServer"] == 2, merged["player1"], np.nan))
    valid_point_flags = merged["PointServer"].isin([1, 2]) & merged["PointWinner"].isin([1, 2])
    merged["server_won"] = np.where(valid_point_flags, merged["PointWinner"] == merged["PointServer"], False)
    merged["returner_won"] = np.where(valid_point_flags, merged["PointWinner"] != merged["PointServer"], False)

    relevant_cols = [
        "match_id", "year", "slam", "tour", "round", "player1", "player2", "PointServer", "PointWinner",
        "speed_mph", "serve_width", "return_depth", "server_name", "returner_name", "server_won", "returner_won",
    ]
    merged[relevant_cols].to_csv(processed_dir / "merged_point_data.csv", index=False)
    return merged


def add_speed_bins(body_points: pd.DataFrame, processed_dir: Path) -> pd.DataFrame:
    binned_parts: list[pd.DataFrame] = []
    thresholds: list[dict[str, object]] = []

    for tour, group in body_points.groupby("tour"):
        group = group.copy()
        unique_speeds = group["speed_mph"].dropna().unique()
        if len(unique_speeds) < 3:
            group["speed_bin"] = pd.cut(group["speed_mph"], bins=3, labels=SPEED_LABELS, include_lowest=True)
        else:
            group["speed_bin"] = pd.qcut(group["speed_mph"], q=3, labels=SPEED_LABELS, duplicates="drop")
            if group["speed_bin"].nunique(dropna=True) < 3:
                group["speed_bin"] = pd.cut(group["speed_mph"], bins=3, labels=SPEED_LABELS, include_lowest=True)

        for label in SPEED_LABELS:
            speeds = group.loc[group["speed_bin"].astype(str) == label, "speed_mph"]
            thresholds.append({
                "tour": tour,
                "speed_bin": label,
                "min_speed_mph": speeds.min(),
                "max_speed_mph": speeds.max(),
                "n_body_serves": len(speeds),
            })
        binned_parts.append(group)

    pd.DataFrame(thresholds).to_csv(processed_dir / "speed_bin_thresholds.csv", index=False)
    return pd.concat(binned_parts, ignore_index=True)


def build_player_features(
    merged: pd.DataFrame,
    processed_dir: Path,
    min_body_serves: int,
    min_bin_serves: int,
    min_return_points: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    point_valid = (
        merged["PointServer"].isin([1, 2])
        & merged["PointWinner"].isin([1, 2])
        & merged["server_name"].notna()
        & merged["returner_name"].notna()
    )
    valid_points = merged.loc[point_valid].copy()

    body_points = valid_points[
        valid_points["serve_width"].isin(BODY_WIDTHS)
        & valid_points["speed_mph"].notna()
        & (valid_points["speed_mph"] > 0)
    ].copy()
    body_points["return_in"] = body_points["return_depth"].isin(["D", "ND"])
    body_points = add_speed_bins(body_points, processed_dir)
    body_points.to_csv(processed_dir / "body_serve_points.csv", index=False)

    grouped = body_points.groupby(["tour", "returner_name", "speed_bin"], observed=False)
    ras = grouped.agg(
        return_accuracy=("return_in", "mean"),
        body_serves=("return_in", "size"),
        return_points_won=("returner_won", "sum"),
    ).reset_index()

    accuracy = ras.pivot(index=["tour", "returner_name"], columns="speed_bin", values="return_accuracy").reset_index()
    counts = ras.pivot(index=["tour", "returner_name"], columns="speed_bin", values="body_serves").reset_index()
    accuracy.columns.name = None
    counts.columns.name = None
    accuracy = accuracy.rename(columns={label: f"ras_{label}" for label in SPEED_LABELS})
    counts = counts.rename(columns={label: f"n_{label}" for label in SPEED_LABELS})

    player_ras = accuracy.merge(counts, on=["tour", "returner_name"], how="left")
    player_ras["body_return_pts"] = player_ras[[f"n_{label}" for label in SPEED_LABELS]].sum(axis=1)
    player_ras = player_ras.rename(columns={"returner_name": "player_name"})
    player_ras = player_ras[
        (player_ras["body_return_pts"] >= min_body_serves)
        & np.logical_and.reduce([(player_ras[f"n_{label}"] >= min_bin_serves) for label in SPEED_LABELS])
    ].copy()
    player_ras.to_csv(processed_dir / "player_rse_clusters.csv", index=False)

    serve_stats = valid_points.groupby(["tour", "server_name"]).agg(
        serve_pts=("server_won", "size"),
        serve_pts_won=("server_won", "sum"),
    ).reset_index().rename(columns={"server_name": "player_name"})
    return_stats = valid_points.groupby(["tour", "returner_name"]).agg(
        return_pts=("returner_won", "size"),
        return_pts_won=("returner_won", "sum"),
    ).reset_index().rename(columns={"returner_name": "player_name"})
    stats_df = serve_stats.merge(return_stats, on=["tour", "player_name"], how="outer").fillna(0)
    stats_df["serve_win_pct"] = np.where(stats_df["serve_pts"] > 0, stats_df["serve_pts_won"] / stats_df["serve_pts"], np.nan)
    stats_df["return_win_pct"] = np.where(stats_df["return_pts"] > 0, stats_df["return_pts_won"] / stats_df["return_pts"], np.nan)
    stats_df["total_win_pct"] = np.where(
        (stats_df["serve_pts"] + stats_df["return_pts"]) > 0,
        (stats_df["serve_pts_won"] + stats_df["return_pts_won"]) / (stats_df["serve_pts"] + stats_df["return_pts"]),
        np.nan,
    )
    stats_df.to_csv(processed_dir / "aggregated_player_stats.csv", index=False)

    comparison = stats_df.merge(player_ras, on=["tour", "player_name"], how="left")
    comparison_cleaned = comparison[comparison["return_pts"] >= min_return_points].copy()
    comparison_cleaned.to_csv(processed_dir / "cluster_comparison_stats_cleaned.csv", index=False)

    return player_ras, stats_df, comparison_cleaned


def label_archetype(row: pd.Series) -> str:
    values = np.array([row["ras_slow"], row["ras_medium"], row["ras_fast"]], dtype=float)
    avg = np.nanmean(values)
    spread = np.nanmax(values) - np.nanmin(values)
    weakest = SPEED_LABELS[int(np.nanargmin(values))]
    strongest = SPEED_LABELS[int(np.nanargmax(values))]
    if avg >= 0.90 and spread <= 0.08:
        return "Elite adaptive returners"
    if avg >= 0.80:
        return f"Strong {strongest}-speed returners"
    if spread <= 0.06:
        return "Balanced returners"
    if weakest == "fast":
        return "Pace-sensitive returners"
    return f"{strongest.title()}-reliant returners"


def cluster_players(player_ras: pd.DataFrame, comparison: pd.DataFrame, processed_dir: Path, requested_k: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    features = ["ras_slow", "ras_medium", "ras_fast"]
    cluster_input = player_ras.dropna(subset=features).copy()
    if len(cluster_input) < 3:
        raise RuntimeError("Not enough players met the body-serve thresholds to cluster.")

    scaler = StandardScaler()
    x = scaler.fit_transform(cluster_input[features])

    max_k = min(12, len(cluster_input) - 1)
    rows: list[dict[str, float]] = []
    for k in range(2, max_k + 1):
        model = KMeans(n_clusters=k, random_state=42, n_init=25)
        labels = model.fit_predict(x)
        rows.append({
            "k": k,
            "inertia": float(model.inertia_),
            "silhouette": float(silhouette_score(x, labels)),
        })
    silhouette_df = pd.DataFrame(rows)
    silhouette_df.to_csv(processed_dir / "k_selection_silhouette.csv", index=False)

    final_k = max(2, min(requested_k, len(cluster_input) - 1))
    final_model = KMeans(n_clusters=final_k, random_state=42, n_init=50)
    cluster_input["cluster"] = final_model.fit_predict(x)

    pca = PCA(n_components=2)
    coords = pca.fit_transform(x)
    cluster_input["PC1"] = coords[:, 0]
    cluster_input["PC2"] = coords[:, 1]
    cluster_input.to_csv(processed_dir / "player_rse_clusters_k7.csv", index=False)

    clustered_comparison = comparison.drop(columns=["cluster"], errors="ignore").merge(
        cluster_input[["tour", "player_name", "cluster", "PC1", "PC2"]],
        on=["tour", "player_name"],
        how="left",
    )
    clustered_comparison.to_csv(processed_dir / "cluster_comparison_stats_cleaned.csv", index=False)
    clustered_comparison[clustered_comparison["tour"] == "ATP"].to_csv(processed_dir / "cluster_comparison_atp.csv", index=False)
    clustered_comparison[clustered_comparison["tour"] == "WTA"].to_csv(processed_dir / "cluster_comparison_wta.csv", index=False)
    cluster_input[cluster_input["tour"] == "ATP"].to_csv(processed_dir / "clustered_atp.csv", index=False)
    cluster_input[cluster_input["tour"] == "WTA"].to_csv(processed_dir / "clustered_wta.csv", index=False)

    profile = clustered_comparison.dropna(subset=["cluster"]).groupby("cluster").agg(
        n_players=("player_name", "nunique"),
        ras_slow=("ras_slow", "mean"),
        ras_medium=("ras_medium", "mean"),
        ras_fast=("ras_fast", "mean"),
        return_win_pct=("return_win_pct", "mean"),
        serve_win_pct=("serve_win_pct", "mean"),
        total_win_pct=("total_win_pct", "mean"),
    ).reset_index()
    profile["archetype"] = profile.apply(label_archetype, axis=1)
    profile.to_csv(processed_dir / "cluster_profiles.csv", index=False)
    return cluster_input, clustered_comparison


def save_barplot_raavbss(df: pd.DataFrame, output: Path, title: str) -> None:
    if df.empty:
        return
    profile = df.groupby("cluster")[["ras_slow", "ras_medium", "ras_fast"]].mean().reset_index()
    long = profile.melt(id_vars="cluster", var_name="Serve Speed Bin", value_name="Return Accuracy Score")
    long["Serve Speed Bin"] = long["Serve Speed Bin"].str.replace("ras_", "", regex=False).str.title()
    plt.figure(figsize=(12, 6))
    sns.barplot(data=long, x="cluster", y="Return Accuracy Score", hue="Serve Speed Bin", palette="Set2")
    plt.title(title)
    plt.ylim(0, 1)
    plt.xlabel("Cluster")
    plt.ylabel("Return Accuracy Score")
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()


def save_return_barplot(df: pd.DataFrame, output: Path, title: str) -> None:
    clustered = df.dropna(subset=["cluster", "return_win_pct"]).copy()
    if clustered.empty:
        return
    clustered["cluster"] = clustered["cluster"].astype(int)
    plt.figure(figsize=(11, 6))
    sns.barplot(data=clustered, x="cluster", y="return_win_pct", hue="cluster", errorbar=("ci", 95), palette="viridis", legend=False)
    plt.title(title)
    plt.ylabel("Return Point Win %")
    plt.xlabel("Cluster")
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()


def save_return_boxplot(df: pd.DataFrame, output: Path, title: str) -> None:
    clustered = df.dropna(subset=["cluster", "return_win_pct"]).copy()
    if clustered.empty:
        return
    clustered["cluster"] = clustered["cluster"].astype(int)
    plt.figure(figsize=(11, 6))
    sns.boxplot(data=clustered, x="cluster", y="return_win_pct")
    plt.title(title)
    plt.ylabel("Return Point Win %")
    plt.xlabel("Cluster")
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()


def save_radar_charts(df: pd.DataFrame, output: Path, annotated: bool) -> None:
    clustered = df.dropna(subset=["cluster", "ras_slow", "ras_medium", "ras_fast"]).copy()
    if clustered.empty:
        return
    means = clustered.groupby("cluster")[["ras_slow", "ras_medium", "ras_fast"]].mean()
    labels = ["Slow", "Medium", "Fast"]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    n_clusters = len(means)
    ncols = 4
    nrows = math.ceil(n_clusters / ncols)
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(5 * ncols, 4.2 * nrows), subplot_kw={"polar": True})
    axes = np.array(axes).reshape(-1)

    for ax, (cluster, row) in zip(axes, means.iterrows()):
        if annotated:
            players = clustered[clustered["cluster"] == cluster][["ras_slow", "ras_medium", "ras_fast"]]
            for _, player_row in players.iterrows():
                individual = player_row.to_list() + [player_row.iloc[0]]
                ax.plot(angles, individual, color="gray", alpha=0.18, linewidth=0.7)
        values = row.to_list() + [row.iloc[0]]
        ax.plot(angles, values, linewidth=2, color="#1f77b4")
        ax.fill(angles, values, alpha=0.25, color="#1f77b4")
        ax.set_title(f"Cluster {int(cluster)}", y=1.12)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)
        ax.set_ylim(0, 1)
        ax.set_yticklabels([])
        if annotated:
            for angle, value in zip(angles[:-1], values[:-1]):
                ax.text(angle, min(value + 0.06, 1.0), f"{value:.2f}", ha="center", va="center", fontsize=8)

    for ax in axes[n_clusters:]:
        fig.delaxes(ax)
    fig.suptitle("RAAVBSS Return Accuracy Profiles by Cluster", fontsize=16)
    plt.tight_layout()
    plt.savefig(output, dpi=160, bbox_inches="tight")
    plt.close()


def save_violin_boxplot(df: pd.DataFrame, output: Path) -> None:
    clustered = df.dropna(subset=["cluster", "return_win_pct", "serve_win_pct"]).copy()
    if clustered.empty:
        return
    clustered["cluster"] = clustered["cluster"].astype(int)
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)
    sns.violinplot(data=clustered, x="cluster", y="return_win_pct", hue="cluster", inner=None, ax=axes[0], palette="Blues", linewidth=0.8, legend=False)
    sns.boxplot(data=clustered, x="cluster", y="return_win_pct", ax=axes[0], width=0.2, color="black", showcaps=True, boxprops={"facecolor": "none"})
    axes[0].set_title("Return Win Percentage by Cluster")
    axes[0].set_xlabel("Cluster")
    axes[0].set_ylabel("Win Percentage")
    axes[0].grid(True, alpha=0.25)

    sns.violinplot(data=clustered, x="cluster", y="serve_win_pct", hue="cluster", inner=None, ax=axes[1], palette="Oranges", linewidth=0.8, legend=False)
    sns.boxplot(data=clustered, x="cluster", y="serve_win_pct", ax=axes[1], width=0.2, color="black", showcaps=True, boxprops={"facecolor": "none"})
    axes[1].set_title("Serve Win Percentage by Cluster")
    axes[1].set_xlabel("Cluster")
    axes[1].set_ylabel("")
    axes[1].grid(True, alpha=0.25)

    plt.suptitle("Return and Serve Win % by Cluster")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output, dpi=160)
    plt.close()


def save_pca_plot(clustered_players: pd.DataFrame, output: Path) -> None:
    if clustered_players.empty:
        return
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=clustered_players, x="PC1", y="PC2", hue="cluster", style="tour", palette="tab10", s=80)
    plt.title("PCA View of Returner Archetypes")
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()


def run_stat_tests(comparison: pd.DataFrame, processed_dir: Path) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for label, df in [("ATP", comparison[comparison["tour"] == "ATP"]), ("WTA", comparison[comparison["tour"] == "WTA"]), ("Combined", comparison)]:
        clustered = df.dropna(subset=["cluster", "return_win_pct"]).copy()
        if clustered["cluster"].nunique() > 1:
            groups = [g["return_win_pct"].dropna() for _, g in clustered.groupby("cluster") if len(g) > 1]
            if len(groups) > 1:
                f_stat, p_val = stats.f_oneway(*groups)
                rows.append({"dataset": label, "test": "ANOVA return_win_pct by cluster", "statistic": f_stat, "p_value": p_val})
        if (clustered["cluster"] == 0).any() and (clustered["cluster"] != 0).any():
            cluster_0 = clustered.loc[clustered["cluster"] == 0, "return_win_pct"]
            others = clustered.loc[clustered["cluster"] != 0, "return_win_pct"]
            if len(cluster_0) > 1 and len(others) > 1:
                t_stat, p_val = stats.ttest_ind(cluster_0, others, equal_var=False, nan_policy="omit")
                rows.append({"dataset": label, "test": "Cluster 0 vs other clusters", "statistic": t_stat, "p_value": p_val})
    result = pd.DataFrame(rows)
    result.to_csv(processed_dir / "statistical_tests.csv", index=False)
    return result


def make_plots(clustered_players: pd.DataFrame, comparison: pd.DataFrame, processed_dir: Path) -> None:
    sns.set_theme(style="whitegrid")
    save_radar_charts(clustered_players, processed_dir / "raavbss_radar_charts.png", annotated=False)
    save_radar_charts(clustered_players, processed_dir / "annotated_radar_plot_with_individuals.png", annotated=True)
    save_pca_plot(clustered_players, processed_dir / "pca_returner_archetypes.png")
    save_barplot_raavbss(clustered_players[clustered_players["tour"] == "ATP"], processed_dir / "atp_raavbss_barplot.png", "ATP RAAVBSS by Cluster")
    save_barplot_raavbss(clustered_players[clustered_players["tour"] == "WTA"], processed_dir / "wta_raavbss_barplot.png", "WTA RAAVBSS by Cluster")
    save_return_barplot(comparison[comparison["tour"] == "ATP"], processed_dir / "atp_return_winrate_by_cluster_barplot.png", "ATP Return Point Win % by Cluster")
    save_return_barplot(comparison[comparison["tour"] == "WTA"], processed_dir / "wta_return_winrate_by_cluster_barplot.png", "WTA Return Point Win % by Cluster")
    save_return_boxplot(comparison[comparison["tour"] == "ATP"], processed_dir / "atp_return_win_by_cluster_boxplot.png", "ATP Return Point Win % by Cluster")
    save_return_boxplot(comparison[comparison["tour"] == "WTA"], processed_dir / "wta_return_win_by_cluster_boxplot.png", "WTA Return Point Win % by Cluster")
    save_violin_boxplot(comparison, processed_dir / "violinbox_return_serve_by_cluster.png")

    silhouette = pd.read_csv(processed_dir / "k_selection_silhouette.csv")
    plt.figure(figsize=(9, 5))
    sns.lineplot(data=silhouette, x="k", y="silhouette", marker="o")
    plt.title("K-Means Cluster Selection: Silhouette Score")
    plt.xlabel("k")
    plt.ylabel("Silhouette score")
    plt.tight_layout()
    plt.savefig(processed_dir / "k_selection_silhouette.png", dpi=160)
    plt.close()


def write_generated_summary(project_root: Path, processed_dir: Path, comparison: pd.DataFrame, tests_df: pd.DataFrame) -> None:
    reports_dir = project_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    profiles = pd.read_csv(processed_dir / "cluster_profiles.csv")
    thresholds = pd.read_csv(processed_dir / "speed_bin_thresholds.csv")
    n_matches = pd.read_csv(processed_dir / "merged_point_data.csv", usecols=["match_id"])["match_id"].nunique()
    n_players = comparison["player_name"].nunique()
    years = pd.read_csv(processed_dir / "merged_point_data.csv", usecols=["year"])["year"]

    summary = [
        "# Tennis Capstone Generated Summary",
        "",
        f"- Analysis window: {int(years.min())}-{int(years.max())}",
        f"- Matches processed: {n_matches:,}",
        f"- Players in comparison dataset: {n_players:,}",
        f"- Players with assigned RAAVBSS clusters: {comparison['cluster'].notna().sum():,}",
        "",
        "## Speed Bins",
        "",
        thresholds.to_markdown(index=False),
        "",
        "## Cluster Profiles",
        "",
        profiles.to_markdown(index=False),
        "",
        "## Statistical Tests",
        "",
        tests_df.to_markdown(index=False) if not tests_df.empty else "No statistical tests could be computed.",
        "",
        "## Key Artifacts",
        "",
        "- `data/processed/player_rse_clusters_k7.csv`",
        "- `data/processed/cluster_comparison_stats_cleaned.csv`",
        "- `data/processed/cluster_profiles.csv`",
        "- `data/processed/statistical_tests.csv`",
        "- `data/processed/*.png`",
    ]
    (reports_dir / "generated_summary.md").write_text("\n".join(summary), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download data and build the RAAVBSS tennis capstone artifacts.")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--start-year", type=int, default=2017)
    parser.add_argument("--end-year", type=int, default=2024)
    parser.add_argument("--clusters", type=int, default=7)
    parser.add_argument("--min-body-serves", type=int, default=50)
    parser.add_argument("--min-bin-serves", type=int, default=10)
    parser.add_argument("--min-return-points", type=int, default=1000)
    parser.add_argument("--skip-download", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    raw_dir = project_root / "data" / "raw" / "slam_pointbypoint"
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    if not args.skip_download:
        download_raw_data(raw_dir, args.start_year, args.end_year)

    merged = load_merged_points(raw_dir, processed_dir)
    player_ras, _stats_df, comparison = build_player_features(
        merged,
        processed_dir,
        min_body_serves=args.min_body_serves,
        min_bin_serves=args.min_bin_serves,
        min_return_points=args.min_return_points,
    )
    clustered_players, clustered_comparison = cluster_players(player_ras, comparison, processed_dir, args.clusters)
    tests_df = run_stat_tests(clustered_comparison, processed_dir)
    make_plots(clustered_players, clustered_comparison, processed_dir)
    write_generated_summary(project_root, processed_dir, clustered_comparison, tests_df)

    print("\nPipeline complete.")
    print(f"Processed files: {processed_dir}")
    print(f"Generated summary: {project_root / 'reports' / 'generated_summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
