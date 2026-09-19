// Dependency-free logic tests. DOM stubs do not replace real browser/layout checks.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../frontend/script.js', import.meta.url), 'utf8');
class Element {
    constructor() { this.children = []; this.attrs = {}; this.textContent = ''; this.value = ''; }
    append(...nodes) { this.children.push(...nodes); }
    replaceChildren(...nodes) { this.children = nodes; }
    setAttribute(k, v) { this.attrs[k] = v; }
    removeAttribute(k) { delete this.attrs[k]; }
    addEventListener() {}
    focus() {}
    get text() { return this.textContent + this.children.map(n => n.text).join(' '); }
}
const sample = {city: 'Torino', country: 'IT', temperature: 23.4, feels_like: 22.8,
    condition: 'Clouds', description: 'few clouds', humidity: 54, wind_speed: 2.6};
function setup(fetch) {
    const nodes = Object.fromEntries(['city-input', 'search-form', 'search-button', 'weather-result'].map(id => [id, new Element()]));
    const context = vm.createContext({document: {getElementById: id => nodes[id], createElement: () => new Element()},
        fetch, AbortController, setTimeout: () => 1, clearTimeout: () => {}});
    vm.runInContext(source, context);
    nodes['city-input'].value = 'Torino';
    return {nodes, run: () => vm.runInContext('getWeather({preventDefault() {}})', context)};
}
const response = (data, ok = true) => ({ok, json: async () => data});

test('success trims and encodes city, renders values, resets loading', async () => {
    let url;
    const {nodes, run} = setup(async u => {url = u; return response(sample);});
    nodes['city-input'].value = '  São Paulo,BR  ';
    await run();
    assert.equal(url, '/weather?city=S%C3%A3o%20Paulo%2CBR');
    assert.match(nodes['weather-result'].text, /Torino, IT/);
    assert.match(nodes['weather-result'].text, /23°C/);
    assert.equal(nodes['search-button'].disabled, false);
    assert.equal(nodes['weather-result'].attrs['aria-busy'], 'false');
});
for (const value of ['', '   ', 'a', 'a'.repeat(101)]) {
    test(`rejects invalid city length ${value.length} without request`, async () => {
        const {nodes, run} = setup(() => {throw Error('Must not fetch');});
        nodes['city-input'].value = value;
        await run();
        assert.match(nodes['weather-result'].text, /between 2 and 100/);
    });
}
for (const [detail, expected] of [['City not found', /City not found/], [[{msg: 'Invalid city'}], /Invalid city/]]) {
    test(`renders backend error ${JSON.stringify(detail)}`, async () => {
        const {nodes, run} = setup(async () => response({detail}, false));
        await run();
        assert.match(nodes['weather-result'].text, expected);
        assert.equal(nodes['search-button'].disabled, false);
    });
}
test('malformed JSON gives readable error', async () => {
    const {nodes, run} = setup(async () => ({json: async () => {throw new SyntaxError();}}));
    await run();
    assert.match(nodes['weather-result'].text, /unreadable response/);
});
test('incomplete data is rejected', async () => {
    const {nodes, run} = setup(async () => response({city:'Torino'}));
    await run();
    assert.match(nodes['weather-result'].text, /incomplete weather data/);
});
for (const [name, message] of [['TypeError', /Could not connect/], ['AbortError', /too long/]]) {
    test(`recovers after ${name}`, async () => {
        const {nodes, run} = setup(async () => {const error = new Error(); error.name = name; throw error;});
        await run();
        assert.match(nodes['weather-result'].text, message);
        assert.equal(nodes['search-button'].disabled, false);
    });
}
test('duplicate submissions make only one request', async () => {
    let resolve, calls = 0;
    const {nodes, run} = setup(() => {calls++; return new Promise(r => {resolve = r;});});
    const first = run();
    assert.equal(nodes['search-button'].disabled, true);
    await run();
    assert.equal(calls, 1);
    resolve(response(sample));
    await first;
    assert.equal(nodes['search-button'].disabled, false);
});
test('dynamic markup remains text', async () => {
    const city = '<img src=x onerror=alert(1)>';
    const {nodes, run} = setup(async () => response({...sample, city}));
    await run();
    assert.ok(nodes['weather-result'].text.includes(city));
    assert.ok(!source.includes('innerHTML'));
});
