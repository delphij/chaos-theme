#!/usr/bin/env node
// Copyright 2026 The Hugo Authors. All rights reserved.
// Use of this source code is governed by an Apache-2.0
// license that can be found in the LICENSE file.
//
// Retakes the Chaos theme specimen screenshots (screenshot.png,
// screenshot-dark.png, and tn.png) from the bundled exampleSite.
//
// Uses headless Chrome via the Chrome DevTools Protocol (CDP) over Node's
// native WebSocket. Requires no external npm dependencies or heavy browser
// frameworks (Playwright/Puppeteer).
//
// Usage:
//   node tools/take_screenshots.mjs [--chrome "/path/to/chrome"]
//
// Without --chrome, $CHROME_BIN (or $GOOGLE_CHROME_BIN) is used, then the
// usual macOS install locations, then the usual names on $PATH.

import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { promises as fs } from 'node:fs';
import { existsSync, createReadStream } from 'node:fs';
import { join, resolve, extname, dirname, delimiter } from 'node:path';
import { fileURLToPath } from 'node:url';
import { tmpdir } from 'node:os';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const THEME_ROOT = resolve(__dirname, '..');
const IMAGES_DIR = join(THEME_ROOT, 'images');
const EXAMPLE_SITE_DIR = join(THEME_ROOT, 'exampleSite');

// Locate Chrome / Chromium: --chrome, then $CHROME_BIN or $GOOGLE_CHROME_BIN,
// then the usual macOS locations, then the usual names on $PATH.
function findChrome() {
  const args = process.argv.slice(2);
  const chromeArgIdx = args.indexOf('--chrome');
  if (chromeArgIdx !== -1) {
    const bin = args[chromeArgIdx + 1];
    if (!bin || !existsSync(bin)) throw new Error(`--chrome: no such file: ${bin ?? ''}`);
    return bin;
  }

  const envBin = process.env.CHROME_BIN || process.env.GOOGLE_CHROME_BIN;
  if (envBin && existsSync(envBin)) return envBin;

  const macCandidates = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
  ];
  for (const c of macCandidates) {
    if (existsSync(c)) return c;
  }

  const pathDirs = (process.env.PATH || '').split(delimiter).filter(Boolean);
  for (const name of ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']) {
    for (const dir of pathDirs) {
      const candidate = join(dir, name);
      if (existsSync(candidate)) return candidate;
    }
  }
  throw new Error('Chrome not found; pass --chrome /path/to/chrome or set CHROME_BIN');
}

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.mjs': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.xml': 'application/xml; charset=utf-8'
};

// Simple static HTTP server for the built example site
function startStaticServer(rootDir) {
  return new Promise((res, rej) => {
    const server = createServer(async (req, resHttp) => {
      try {
        let pathname = decodeURIComponent(new URL(req.url, 'http://127.0.0.1').pathname);
        if (pathname.endsWith('/')) {
          pathname += 'index.html';
        }
        let filePath = join(rootDir, pathname);
        if (existsSync(filePath) && (await fs.stat(filePath)).isDirectory()) {
          filePath = join(filePath, 'index.html');
        }

        if (!existsSync(filePath)) {
          resHttp.writeHead(404, { 'Content-Type': 'text/plain' });
          resHttp.end('Not Found');
          return;
        }

        const ext = extname(filePath).toLowerCase();
        const contentType = MIME_TYPES[ext] || 'application/octet-stream';
        resHttp.writeHead(200, { 'Content-Type': contentType });
        createReadStream(filePath).pipe(resHttp);
      } catch (err) {
        resHttp.writeHead(500, { 'Content-Type': 'text/plain' });
        resHttp.end('Server Error: ' + err.message);
      }
    });

    server.listen(0, '127.0.0.1', () => {
      const port = server.address().port;
      res({
        server,
        port,
        close: () => new Promise(cb => server.close(cb))
      });
    });
    server.on('error', rej);
  });
}

// Build exampleSite with Hugo
function buildExampleSite(destination, baseURL) {
  return new Promise((res, rej) => {
    console.log(`Building exampleSite with baseURL=${baseURL}...`);
    const hugo = spawn('hugo', [
      '--source', EXAMPLE_SITE_DIR,
      '--destination', destination,
      '--baseURL', baseURL,
      '--gc',
      '--minify'
    ], { stdio: 'inherit' });

    hugo.on('close', code => {
      if (code === 0) res();
      else rej(new Error(`hugo exited with code ${code}`));
    });
    hugo.on('error', rej);
  });
}

// Helper for CDP client
class CDPClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.ws = null;
    this.id = 1;
    this.callbacks = new Map();
    this.eventListeners = new Map();
  }

  async connect() {
    return new Promise((res, rej) => {
      this.ws = new WebSocket(this.wsUrl);
      this.ws.onopen = () => res();
      this.ws.onerror = err => rej(err);
      this.ws.onmessage = evt => {
        const msg = JSON.parse(evt.data);
        if (msg.id && this.callbacks.has(msg.id)) {
          const { resolve, reject } = this.callbacks.get(msg.id);
          this.callbacks.delete(msg.id);
          if (msg.error) {
            reject(new Error(msg.error.message));
          } else {
            resolve(msg.result);
          }
        } else if (msg.method && this.eventListeners.has(msg.method)) {
          for (const cb of [...this.eventListeners.get(msg.method)]) {
            cb(msg.params);
          }
        }
      };
    });
  }

  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = this.id++;
      this.callbacks.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  // Resolves on the next `event`; the listener is dropped once it fires.
  once(event) {
    return new Promise(resolve => {
      const listeners = this.eventListeners.get(event) || [];
      const cb = params => {
        listeners.splice(listeners.indexOf(cb), 1);
        resolve(params);
      };
      listeners.push(cb);
      this.eventListeners.set(event, listeners);
    });
  }

  async navigate(url) {
    const loaded = this.once('Page.loadEventFired');
    await this.send('Page.navigate', { url });
    await loaded;
  }

  close() {
    if (this.ws) this.ws.close();
  }
}

async function main() {
  const chromePath = findChrome();
  console.log(`Using Chrome binary: ${chromePath}`);

  const tempBuildDir = join(tmpdir(), `chaos-site-${Date.now()}`);
  const tempUserDataDir = join(tmpdir(), `chaos-chrome-${Date.now()}`);

  let staticServer = null;
  let chromeProcess = null;
  let cdp = null;

  try {
    // 1. Start static HTTP server on ephemeral port
    staticServer = await startStaticServer(tempBuildDir);
    const baseURL = `http://127.0.0.1:${staticServer.port}/`;

    // 2. Build exampleSite to tempBuildDir
    await buildExampleSite(tempBuildDir, baseURL);

    // 3. Launch headless Chrome
    console.log('Launching headless Chrome...');
    await fs.mkdir(tempUserDataDir, { recursive: true });

    chromeProcess = spawn(chromePath, [
      '--headless=new',
      '--remote-debugging-port=0',
      `--user-data-dir=${tempUserDataDir}`,
      '--no-first-run',
      '--no-default-browser-check',
      '--hide-scrollbars',
      '--disable-background-networking',
      '--disable-sync',
      '--disable-gpu',
      '--mute-audio',
      'about:blank'
    ]);

    // Read the DevTools port from stderr
    const wsEndpoint = await new Promise((res, rej) => {
      let stderrAcc = '';
      const timeout = setTimeout(() => {
        rej(new Error('Timed out waiting for Chrome DevTools endpoint'));
      }, 10000);

      chromeProcess.stderr.on('data', chunk => {
        stderrAcc += chunk.toString();
        const match = stderrAcc.match(/DevTools listening on (ws:\/\/127\.0\.0\.1:\d+\/[^\s]+)/);
        if (match) {
          clearTimeout(timeout);
          res(match[1]);
        }
      });

      chromeProcess.on('exit', code => {
        clearTimeout(timeout);
        rej(new Error(`Chrome exited prematurely with code ${code}`));
      });
      chromeProcess.on('error', err => {
        clearTimeout(timeout);
        rej(err);
      });
    });

    const portMatch = wsEndpoint.match(/127\.0\.0\.1:(\d+)/);
    const chromePort = portMatch[1];

    // Open a new target page
    const newPageResp = await fetch(`http://127.0.0.1:${chromePort}/json/new`, { method: 'PUT' });
    const pageData = await newPageResp.json();
    const pageWsUrl = pageData.webSocketDebuggerUrl;

    cdp = new CDPClient(pageWsUrl);
    await cdp.connect();

    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    // The theme follows prefers-color-scheme when no mode is stored, and the
    // profile is fresh, so emulating the media query picks the mode before
    // the first paint, as a reader's own setting would.
    const setScheme = value => cdp.send('Emulation.setEmulatedMedia', {
      features: [{ name: 'prefers-color-scheme', value }]
    });
    const settle = () => cdp.send('Runtime.evaluate', {
      expression: 'document.fonts.ready.then(() => undefined)',
      awaitPromise: true
    });

    console.log('\n--- 1/3: Taking screenshot.png (Light Mode, 1500x1000) ---');
    // The theme reserves the scrollbar's width (scrollbar-gutter: stable on
    // html), and headless Chrome keeps that reservation with scrollbars
    // hidden: the page would lay out 15px narrower, with a blank strip at the
    // right edge that a browser with overlay scrollbars never shows. Widen the
    // viewport by the gutter so the page lays out at 1500px, and capture only
    // those 1500px. The clip is in document coordinates, hence scrollY.
    const setWidth = width => cdp.send('Emulation.setDeviceMetricsOverride', {
      width, height: 1000, deviceScaleFactor: 1, mobile: false
    });
    const VIEW = { x: 0, y: 0, width: 1500, height: 1000 };
    const capture = async (scale = 1) => {
      const { result } = await cdp.send('Runtime.evaluate', {
        expression: 'scrollY',
        returnByValue: true
      });
      return cdp.send('Page.captureScreenshot', {
        format: 'png',
        clip: { ...VIEW, y: result.value, scale }
      });
    };
    await setWidth(VIEW.width);

    await setScheme('light');
    await cdp.navigate(baseURL);
    await settle();
    const { result: gutter } = await cdp.send('Runtime.evaluate', {
      expression: 'innerWidth - document.body.clientWidth',
      returnByValue: true
    });
    if (gutter.value > 0) await setWidth(VIEW.width + gutter.value);
    await new Promise(r => setTimeout(r, 600));

    const screenshotData = await capture();
    const screenshotPath = join(IMAGES_DIR, 'screenshot.png');
    await fs.writeFile(screenshotPath, Buffer.from(screenshotData.data, 'base64'));
    console.log(`Saved: ${screenshotPath}`);

    // The thumbnail is the same view scaled to 900x600, so it shows the
    // desktop layout rather than the narrower one a 900px viewport gets.
    console.log('\n--- 2/3: Taking tn.png (Light Mode, screenshot.png at 0.6x) ---');
    const tnData = await capture(0.6);
    const tnPath = join(IMAGES_DIR, 'tn.png');
    await fs.writeFile(tnPath, Buffer.from(tnData.data, 'base64'));
    console.log(`Saved: ${tnPath}`);

    console.log('\n--- 3/3: Taking screenshot-dark.png (Dark Mode, 1500x1000, KaTeX block math) ---');
    await setScheme('dark');
    await cdp.navigate(`${baseURL}posts/math-with-katex/`);
    await settle();

    // Scroll to the block-math section and wait for the TOC to mark it active.
    const { result } = await cdp.send('Runtime.evaluate', {
      expression: `
        (async () => {
          const id = '块级公式';
          const target = document.getElementById(id);
          if (!target) return 'no #' + id + ' in posts/math-with-katex/';
          target.scrollIntoView({ behavior: 'instant', block: 'start' });
          for (let i = 0; i < 40; i++) {
            const active = document.querySelector('#tableOfContents a.active');
            if (active && decodeURIComponent(active.getAttribute('href')) === '#' + id) return '';
            await new Promise(r => setTimeout(r, 50));
          }
          return 'the table of contents never marked #' + id + ' active';
        })()
      `,
      awaitPromise: true,
      returnByValue: true
    });
    if (result.value) throw new Error(result.value);
    await new Promise(r => setTimeout(r, 600));

    const darkData = await capture();
    const darkPath = join(IMAGES_DIR, 'screenshot-dark.png');
    await fs.writeFile(darkPath, Buffer.from(darkData.data, 'base64'));
    console.log(`Saved: ${darkPath}`);

    console.log('\nAll 3 screenshots updated successfully!');
  } finally {
    if (cdp) cdp.close();
    if (chromeProcess) {
      chromeProcess.kill('SIGTERM');
    }
    if (staticServer) {
      await staticServer.close();
    }
    // Clean up temp dirs
    try {
      await fs.rm(tempBuildDir, { recursive: true, force: true });
      await fs.rm(tempUserDataDir, { recursive: true, force: true });
    } catch (_) {}
  }
}

main().catch(err => {
  console.error('Error taking screenshots:', err);
  process.exit(1);
});

