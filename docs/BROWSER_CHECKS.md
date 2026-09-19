# Optional browser checks

These checks exercise the real page and JavaScript in Chromium. Browser weather requests are intercepted and receive fixture responses; no API key or OpenWeather access is needed. The generated screenshot uses the same fixture, not live data. A screenshot is not bundled because Chromium installation was unavailable in the preparation environment. The browser script has not been executed there.

Install the optional dependencies and browser (Windows PowerShell):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-browser.txt
.\.venv\Scripts\python.exe -m playwright install chromium
```

Start the app using the README command. In another terminal, from the project root:

```powershell
.\.venv\Scripts\python.exe scripts/check_browser.py
```

On macOS/Linux, substitute `.venv/bin/python`. Some Linux systems also need Playwright's browser system dependencies.

The script checks keyboard search, client validation, string/array errors, malformed responses, connection failure, safe text rendering, duplicate submission prevention, loading-state recovery, and a 320px mobile layout. It regenerates `docs/screenshot.png`. Backend behavior is tested separately with pytest.

The default GitHub Actions workflow runs Python API tests and Node.js frontend logic tests; it does not install or run browser tests.
