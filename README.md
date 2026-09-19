# Weather Dashboard

A small full-stack application for searching current weather by city. A FastAPI backend calls OpenWeather, validates the response, and returns a compact JSON payload to a vanilla JavaScript frontend.

## Features

- City search, including Unicode names and optional country codes such as `Torino,IT`.
- Temperature, feels-like temperature, conditions, humidity, and wind speed.
- Asynchronous HTTP requests in both Python and JavaScript.
- Backend input validation and Pydantic response validation.
- Friendly handling of unknown cities, timeouts, provider failures, and malformed responses.
- Loading feedback, keyboard submission, accessible labels, and responsive styling.
- One server for the frontend and API; no separate frontend build or CORS setup.
- Mocked API tests, frontend logic tests, and a GitHub Actions test workflow.

## Stack and structure

Python 3.12, FastAPI, Pydantic, HTTPX, python-dotenv, Uvicorn, HTML/CSS, JavaScript, and pytest.

| Path | Responsibility |
| --- | --- |
| `backend/main.py` | App lifecycle, input validation, routes, static frontend |
| `backend/weather.py` | OpenWeather request and error translation |
| `backend/models.py` | Public weather response schema |
| `frontend/` | Search form, rendering, and styles |
| `tests/test_weather_api.py` | API/service tests with the external HTTP transport mocked |
| `.github/workflows/tests.yml` | Runs Python and frontend logic tests on pushes and pull requests |
| `docs/` | Browser checks, setup/publishing guide, interview notes |

The browser requests `/weather?city=Torino,IT`. FastAPI validates the city, awaits OpenWeather through a shared HTTPX client, validates the provider data, and returns the public response. The browser inserts returned text using `textContent`.

## Run locally

Use Python 3.12 (the tested version). Run commands from the project root.

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and replace `your_api_key_here` with your own [OpenWeather API key](https://home.openweathermap.org/api_keys). Keep this file private.

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

### macOS / Linux

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
# Edit .env and insert your own key.
.venv/bin/python -m uvicorn backend.main:app --reload
```

Open **http://127.0.0.1:8000**. API docs: **http://127.0.0.1:8000/docs**.

Do not open the HTML file directly or start a separate frontend server. The API key stays on the backend. Existing environment variables override `.env` settings. Restart the server after changing the key.

## API

`GET /weather?city=Torino,IT`

The city is trimmed before validating its length (2–100 characters). No ASCII-only name restriction is applied.

Example response (illustrative values):

```json
{
  "city": "Torino",
  "country": "IT",
  "temperature": 23.4,
  "feels_like": 22.8,
  "condition": "Clouds",
  "description": "few clouds",
  "humidity": 54,
  "wind_speed": 2.6
}
```

Temperatures are °C, humidity is a percentage, and wind speed is m/s. The frontend rounds displayed temperatures; the API retains provider precision.

| Status | Meaning |
| --- | --- |
| `200` | Weather returned |
| `422` | Missing city or invalid trimmed length |
| `404` | Provider could not find the city |
| `500` | Backend API key not configured |
| `502` | Provider credentials rejected, unexpected status, or malformed data |
| `503` | Provider connection failure or provider rate limit |
| `504` | Provider request timed out |

Application errors use `{"detail": "message"}`. FastAPI validation errors use a `detail` array, also handled by the frontend. `/health` reports process health only; it does not verify the provider or key.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

On macOS/Linux, substitute `.venv/bin/python`.

The suite exercises the actual route and service, replacing only the external HTTP transport with `httpx.MockTransport`. It checks response mapping, provider parameters, validation, missing keys, provider statuses, network failures, malformed data, and static routes. It needs no real key and makes no real provider requests.

With Node.js 22 installed, run `node --test scripts/check_frontend.mjs` for 13 dependency-free frontend logic tests. These use DOM stubs and do not verify browser layout.

Optional browser checks and screenshot generation are documented in [docs/BROWSER_CHECKS.md](docs/BROWSER_CHECKS.md).

## Design choices and limitations

- A shared async HTTP client is opened at startup and closed at shutdown. Calls have an explicit 10-second HTTPX timeout; the browser cancels requests after 15 seconds.
- New submissions are ignored while a request is running, preventing overlapping results.
- Current weather is fetched on search; this is not a continuously updating feed or forecast.
- City names can be ambiguous; a country code helps but is not a complete location picker.
- The application depends on OpenWeather access and quota. There is no caching, user authentication, or application-level rate limiting.
- Intended as a local portfolio/demo application. Before public hosting, configure HTTPS, quota controls/rate limiting, and deployment-specific operations. `--reload` is for local development.
- Provider URLs and raw exceptions are not logged by the application because query parameters contain the API key. Do not enable verbose HTTP client logging with a real key.

For publishing instructions, see [docs/GITHUB_SETUP.md](docs/GITHUB_SETUP.md). For architecture and interview preparation, see [docs/INTERVIEW_GUIDE.md](docs/INTERVIEW_GUIDE.md).
