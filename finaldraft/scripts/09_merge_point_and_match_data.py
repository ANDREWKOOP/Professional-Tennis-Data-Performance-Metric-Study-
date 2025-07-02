# 08_merge_point_and_match_data.py

import pandas as pd
import os
from glob import glob
import re

DATA_DIR = r"D:/school programs/TennisStrategyProject/mydata"
MERGED_FILE = os.path.join(DATA_DIR, "merged_point_data.csv")

def load_slam_data():
    matches, points = [], []

    for file in glob(os.path.join(DATA_DIR, "*-matches.csv")):
        year_match = re.search(r"(\d{4})", os.path.basename(file))
        if year_match and int(year_match.group(1)) >= 2017:
            df = pd.read_csv(file)
            df["year"] = int(year_match.group(1))
            matches.append(df)

    for file in glob(os.path.join(DATA_DIR, "*-points.csv")):
        year_point = re.search(r"(\d{4})", os.path.basename(file))
        if year_point and int(year_point.group(1)) >= 2017:
            df = pd.read_csv(file)
            df["year"] = int(year_point.group(1))
            points.append(df)

    return pd.concat(matches, ignore_index=True), pd.concat(points, ignore_index=True)

matches_df, points_df = load_slam_data()
merged = points_df.merge(matches_df[['match_id', 'player1', 'player2']], on='match_id', how='left')
merged.to_csv(MERGED_FILE, index=False)
print(f"Merged point-level dataset saved: {merged.shape} → {MERGED_FILE}")
