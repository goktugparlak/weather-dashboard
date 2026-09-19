# Understand and demonstrate the project

Read the code and practice these explanations in your own words. Use the project to demonstrate your actual understanding; be candid about assistance or tools used if asked.

## Walk through one request

1. The form submit handler prevents page reload and trims the city.
2. Basic client validation gives quick feedback. A loading flag blocks duplicate submissions.
3. `fetch` requests a relative `/weather` URL, so the same host serves UI and API.
4. FastAPI/Pydantic trim and validate the query independently of the browser.
5. The route awaits the service function, which awaits a shared `httpx.AsyncClient` request.
6. The service maps provider failures to deliberate HTTP statuses and validates successful data with `WeatherResponse`.
7. The browser checks the HTTP status and payload, renders text with `textContent`, and restores the UI in `finally`.

## Questions worth practicing

| Question | Explanation |
| --- | --- |
| Why use a backend? | Keep the provider key off the browser, enforce validation, and normalize errors/data. |
| Why async? | Waiting for network I/O can yield to other requests. It does not make OpenWeather itself faster or speed up CPU-bound work. |
| Why share the HTTP client? | Reuse connections and close resources predictably through FastAPI's lifespan. |
| What does Pydantic do? | Validate trimmed input constraints and the typed outgoing weather contract, including humidity/wind ranges. |
| Why validate twice? | Browser validation helps users; backend validation is necessary for all clients, including direct API requests. |
| Why no CORS middleware? | The UI and API are served from the same origin. Separate origins would require deliberate CORS configuration. |
| Why `textContent`? | Returned strings are displayed as text, not parsed as executable HTML. |
| What is mocked? | The external HTTP transport. The application route, mapping, validation, and error handling actually run. |
| Why 503 for provider 429? | The provider's shared quota is temporarily unavailable; this is not necessarily a limit imposed on the individual dashboard user. |
| What does `/health` prove? | The process is responsive, not that the provider or credentials are working. |
| Why no database? | Current lookup functionality has no persistence requirement. |

## Suggested demonstration

- Start the server and show a successful search using your own key.
- Search for a clearly nonexistent city and show the useful error.
- Open `/docs` and explain the JSON fields and units.
- Run `python -m pytest -q` in your activated environment.
- Show one provider-failure test and explain the boundary being mocked.
- Walk through `main.py`, `weather.py`, and `script.js`.

## Honest scope

This is a small full-stack portfolio application, not a production weather platform. Reasonable next steps include caching to reduce quota usage, a location picker for ambiguous names, and deployment with abuse controls. Explain why you would add a feature before adding more dependencies.

Live provider access and GitHub CI must still be verified with your account/environment. Offline tests simulate the provider and cannot establish that a real API key is valid.
