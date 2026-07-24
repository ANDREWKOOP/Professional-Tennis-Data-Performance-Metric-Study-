# Deploying This Project

## What to Commit

Commit these:

- `dashboard/streamlit_app.py`
- `notebooks/tennis_capstone_story.ipynb`
- `scripts/`
- `reports/`
- `data/processed/` except the large row-level files ignored by `.gitignore`
- `requirements.txt`
- `requirements-pipeline.txt`
- `.streamlit/config.toml`
- `README.md`
- `DATA_PROVENANCE.md`

Do not commit these:

- `.venv/`
- `data/raw/`
- `data/processed/merged_point_data.csv`
- `data/processed/body_serve_points.csv`

The Streamlit dashboard reads the small summary CSVs and image artifacts from `data/processed/`, so those files should be on GitHub.

## Git Commands

If this folder is not already a Git repository:

```powershell
git init
git branch -M main
git add .
git commit -m "Add RAAVBSS tennis capstone notebook and dashboard"
git remote add origin https://github.com/ANDREWKOOP/Professional-Tennis-Data-Performance-Metric-Study-.git
git push -u origin main
```

If the GitHub repo already has files and you want to preserve them, clone the repo first, copy this project into the clone, then commit and push.

## Streamlit Community Cloud

1. Go to https://share.streamlit.io.
2. Create a new app from GitHub.
3. Select repository: `ANDREWKOOP/Professional-Tennis-Data-Performance-Metric-Study-`.
4. Select branch: `main`.
5. Set main file path to either:

```text
dashboard/streamlit_app.py
```

or the root wrapper:

```text
streamlit_app.py
```

6. In advanced settings, select **Python 3.12**. Do not use Python 3.14 for this app.
7. Deploy.

Streamlit Community Cloud runs apps from the repository root, so keep `requirements.txt`, `.streamlit/config.toml`, and `data/processed/` at the repository root. `requirements.txt` is intentionally dashboard-only and Cloud-first; the heavier local data-generation packages are in `requirements-pipeline.txt`.

## If Dependency Installation Fails

If logs show something like:

```text
Using Python 3.14.x environment
Failed to download and build pillow
The headers or library files could not be found for zlib
```

push the latest `requirements.txt`, then delete the Streamlit app and redeploy it with **Python 3.12** selected in Advanced settings. Streamlit's docs say Python itself cannot be changed after deployment; the app has to be deleted and redeployed to change Python versions.
