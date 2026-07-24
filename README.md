# Professional Tennis Data Performance Metric Study

This local project is set up to reproduce the tennis capstone report from raw public data.

## One-command run

From PowerShell, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_tennis_project.ps1
```

That script will:

1. Create a local Python virtual environment in `.venv`.
2. Install the Python packages in `requirements-pipeline.txt`.
3. Download Grand Slam point-level and match-level files from the Jeff Sackmann archive mirror.
4. Derive RAAVBSS features from body serves.
5. Cluster player return profiles.
6. Generate CSV outputs and plot images.
7. Try to render the RMarkdown report if `Rscript` is installed.

## Main outputs

- `data/raw/slam_pointbypoint/`: downloaded raw Jeff Sackmann Grand Slam files.
- `data/processed/`: derived CSV files and PNG plots used by the report.
- `notebooks/tennis_capstone_story.ipynb`: one large portfolio notebook written for non-tennis readers.
- `dashboard/streamlit_app.py`: interactive Streamlit dashboard for the project.
- `streamlit_app.py`: root-level wrapper for Streamlit Community Cloud.
- `reports/tennis_capstone_report.Rmd`: RMarkdown portfolio report.
- `reports/portfolio_report.md`: GitHub-friendly written project summary.

## Dashboard

After running the project once, launch the dashboard with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_dashboard.ps1
```

Then open http://127.0.0.1:8501.

`requirements.txt` is intentionally small and Cloud-first for Streamlit Community Cloud. The full local data-generation environment is in `requirements-pipeline.txt`.

## Story notebook

The main portfolio notebook is:

```text
notebooks/tennis_capstone_story.ipynb
```

If you edit the notebook builder and want to regenerate the notebook:

```powershell
.\.venv\Scripts\python.exe .\scripts\build_story_notebook.py
```

## Data source and license

The setup script downloads from the Hugging Face mirror of Jeff Sackmann's public tennis datasets:

- Original upstream: https://github.com/JeffSackmann/tennis_slam_pointbypoint
- Mirror used by this script: https://huggingface.co/datasets/Aneeshers/tennis-sackmann-archive

Jeff Sackmann's tennis data is licensed under CC BY-NC-SA 4.0. Use this project for non-commercial portfolio/academic purposes and keep attribution with any shared outputs.
