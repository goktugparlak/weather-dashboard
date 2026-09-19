# Finish setup and publish

## What you need to do

1. Extract the ZIP and open the inner `weather-dashboard` folder in VS Code.
2. Follow the README to create a virtual environment and install dependencies.
3. Copy `.env.example` to `.env`, add your own key, and start the server.
4. Search for a real city to verify your account/key and network access.
5. Run the tests, then upload the project files to your GitHub repository.

The archive deliberately excludes your original `.env` and `.venv`. It includes all source, tests, documentation, screenshot-generation script, and CI workflow. You do not need to write additional code to use this version.

## New GitHub repository

Create an empty repository named `weather-dashboard` on GitHub without initializing another README, license, or .gitignore. Then run these commands from the inner project folder:

```powershell
git init
git branch -M main
git add .
git status
git diff --cached --stat
```

Inspect the staged list. It should include `.env.example`, but not `.env` or `.venv`.

```powershell
git commit -m "Complete weather dashboard with async requests and tests"
git remote add origin https://github.com/YOUR_USERNAME/weather-dashboard.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username. Authenticate through your Git installation/GitHub sign-in flow. Never paste tokens into code, the README, or a remote URL.

## Existing repository

Do not create another Git history or force-push. Clone the existing repository first (or use your current checkout), copy this archive's project contents into that checkout, and keep its `.git` directory and unrelated files. Review `git diff` and `git status`, commit the intended changes, and push normally. Resolve any conflicting remote changes before pushing.

If a real `.env` was already tracked, use `git rm --cached .env` to stop tracking it. If a key was ever exposed publicly, rotate it; a later deletion does not erase earlier commits.

## Repository presentation

- About description: “Current-weather dashboard built with FastAPI, asynchronous HTTP requests, and vanilla JavaScript.”
- Suggested topics: `python`, `fastapi`, `javascript`, `weather`, `pytest`.
- Confirm the Actions test run succeeds.
- Optionally run the browser checks to create `docs/screenshot.png`, then add `![Weather Dashboard](docs/screenshot.png)` to the README. Label it as a sample-data preview, because the screenshot script mocks weather values.
- Pin the project on your profile if it represents work you can explain.
- Upload the extracted source files, not just the ZIP.

A license is a choice about reuse permissions; no license was selected automatically. Add one only after choosing the permissions you want to grant.
