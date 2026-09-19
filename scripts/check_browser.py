"""Optional browser checks; start the app first. All weather requests are mocked."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = {"city": "Torino", "country": "IT", "temperature": 23.4, "feels_like": 22.8,
          "condition": "Clouds", "description": "few clouds", "humidity": 54, "wind_speed": 2.6}


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1100, "height": 1000}, device_scale_factor=1)
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_default_timeout(10000)
        page.goto("http://127.0.0.1:8000")
        city = page.get_by_label("City", exact=True)
        button = page.get_by_role("button", name="Search", exact=True)
        result = page.locator("#weather-result")
        page.route("**/weather?*", lambda route: route.fulfill(json=SAMPLE))
        city.fill("Torino,IT")
        city.press("Enter")
        expect(result).to_contain_text("Torino, IT")
        expect(result).to_contain_text("23°C")
        expect(button).to_be_enabled()
        page.screenshot(path=str(ROOT / "docs/screenshot.png"), full_page=True)

        city.fill(" ")
        button.click()
        expect(result).to_contain_text("between 2 and 100")
        expect(city).to_have_attribute("aria-invalid", "true")

        for status, payload, message in [
            (404, {"detail": "City not found"}, "City not found"),
            (422, {"detail": [{"msg": "Invalid city length"}]}, "Invalid city length"),
            (200, {"city": "Torino"}, "incomplete weather data"),
            (200, {**SAMPLE, "city": '<img src=x onerror="window.injected=true">'}, "<img"),
        ]:
            page.unroute("**/weather?*")
            page.route("**/weather?*", lambda route: route.fulfill(status=status, json=payload))
            city.fill("Torino")
            button.click()
            expect(result).to_contain_text(message)
            expect(button).to_be_enabled()
        assert page.locator("#weather-result img").count() == 0
        assert page.evaluate("window.injected === undefined")

        page.unroute("**/weather?*")
        page.route("**/weather?*", lambda route: route.fulfill(body="not JSON", content_type="text/plain"))
        button.click()
        expect(result).to_contain_text("unreadable response")
        expect(button).to_be_enabled()

        page.unroute("**/weather?*")
        page.route("**/weather?*", lambda route: route.abort())
        button.click()
        expect(result).to_contain_text("Could not connect")
        expect(button).to_be_enabled()

        # Hold a response while submitting again: the pending lookup must remain unique.
        page.unroute("**/weather?*")
        pending = []
        page.route("**/weather?*", lambda route: pending.append(route))
        button.click()
        expect(page.get_by_role("button", name="Searching…")).to_be_disabled()
        expect(result).to_contain_text("Loading weather")
        city.press("Enter")
        page.evaluate("document.querySelector('form').dispatchEvent(new Event('submit', {cancelable: true}))")
        assert len(pending) == 1
        pending.pop().fulfill(json=SAMPLE)
        expect(result).to_contain_text("Torino, IT")
        expect(button).to_be_enabled()
        expect(result).to_have_attribute("aria-busy", "false")

        page.set_viewport_size({"width": 320, "height": 740})
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        assert button.bounding_box()["width"] > 0
        assert not errors, errors
        browser.close()
    print("Browser checks passed: search, validation, provider errors, safe text, duplicate prevention, mobile layout.")


if __name__ == "__main__":
    main()
