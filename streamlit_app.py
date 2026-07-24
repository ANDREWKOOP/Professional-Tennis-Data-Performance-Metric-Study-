from pathlib import Path


app_path = Path(__file__).parent / "dashboard" / "streamlit_app.py"
globals_dict = {
    "__file__": str(app_path),
    "__name__": "__main__",
}
exec(app_path.read_text(encoding="utf-8"), globals_dict)
