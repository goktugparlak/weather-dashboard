const cityInput = document.getElementById("city-input");
const searchForm = document.getElementById("search-form");
const searchButton = document.getElementById("search-button");
const weatherResult = document.getElementById("weather-result");
let isLoading = false;

searchForm.addEventListener("submit", getWeather);

function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
}

function showMessage(message, className) {
    weatherResult.replaceChildren(element("p", className, message));
}

function errorMessage(data) {
    if (typeof data?.detail === "string") return data.detail;
    if (Array.isArray(data?.detail)) {
        return data.detail.map((error) => error.msg || "Invalid input").join(". ");
    }
    return "Unable to retrieve weather. Please try again.";
}

async function getWeather(event) {
    event.preventDefault();
    if (isLoading) return;
    const city = cityInput.value.trim();
    if ([...city].length < 2 || [...city].length > 100) {
        cityInput.setAttribute("aria-invalid", "true");
        showMessage("Enter a city name between 2 and 100 characters.", "error-message");
        cityInput.focus();
        return;
    }
    cityInput.removeAttribute("aria-invalid");
    isLoading = true;
    searchButton.disabled = true;
    searchButton.textContent = "Searching…";
    weatherResult.setAttribute("aria-busy", "true");
    showMessage("Loading weather…", "loading-message");
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    try {
        const response = await fetch(`/weather?city=${encodeURIComponent(city)}`, {
            signal: controller.signal,
        });
        let data;
        try {
            data = await response.json();
        } catch (error) {
            if (error.name === "AbortError") throw error;
            showMessage("The server returned an unreadable response. Please try again.", "error-message");
            return;
        }
        if (!response.ok) {
            showMessage(errorMessage(data), "error-message");
            return;
        }
        if (!validWeather(data)) {
            showMessage("The server returned incomplete weather data.", "error-message");
            return;
        }
        showWeather(data);
    } catch (error) {
        showMessage(error.name === "AbortError"
            ? "The request took too long. Please try again."
            : "Could not connect to the weather server. Check your connection and try again.", "error-message");
    } finally {
        clearTimeout(timeout);
        isLoading = false;
        searchButton.disabled = false;
        searchButton.textContent = "Search";
        weatherResult.setAttribute("aria-busy", "false");
    }
}

function validWeather(data) {
    return data && ["city", "country", "condition", "description"].every(
        (key) => typeof data[key] === "string",
    ) && ["temperature", "feels_like", "humidity", "wind_speed"].every(
        (key) => typeof data[key] === "number" && Number.isFinite(data[key]),
    );
}

function showWeather(data) {
    const card = element("article", "weather-card");
    card.append(element("p", "eyebrow", "CURRENT WEATHER"));
    card.append(element("h2", "", `${data.city}, ${data.country}`));
    card.append(element("p", "temperature", `${Math.round(data.temperature)}°C`));
    card.append(element("p", "condition", `${data.condition} · ${data.description}`));
    const details = element("dl", "weather-details");
    for (const [label, value] of [
        ["Feels like", `${Math.round(data.feels_like)} °C`],
        ["Humidity", `${data.humidity}%`],
        ["Wind", `${data.wind_speed} m/s`],
    ]) {
        const item = element("div", "metric");
        item.append(element("dt", "", label), element("dd", "", value));
        details.append(item);
    }
    card.append(details);
    weatherResult.replaceChildren(card);
}
