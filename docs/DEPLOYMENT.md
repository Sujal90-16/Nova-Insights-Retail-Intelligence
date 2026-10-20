# Deployment Notes

The dashboard can be deployed to a Streamlit-compatible hosting service by connecting the Git repository, selecting `app/streamlit_app.py` as the app entry point, and installing dependencies from `requirements.txt`.

Before deployment, verify that all input data files are committed, paths are relative to the repository, and the app does not depend on local-only files. If real data is used, review access controls and data privacy first. Do not add secrets to source control.
