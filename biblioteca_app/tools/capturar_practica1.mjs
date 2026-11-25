// Evidencias de la Práctica 1: ejecuta la app web real y captura cada paso.
// Requiere: flutter build web --release y servidor estático en http://127.0.0.1:8082
import { spawn } from 'node:child_process';
import { mkdirSync, mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import process from 'node:process';

const APP_URL = process.env.APP_URL ?? 'http://127.0.0.1:8082/';
const OUT_DIR = path.resolve('evidencias');
const PORT = 9334;
const CHROME =
  process.env.CHROME_PATH ?? 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status} en ${url}`);
  return response.json();
}

mkdirSync(OUT_DIR, { recursive: true });
const profile = mkdtempSync(path.join(tmpdir(), 'biblioteca-chrome-'));
const chrome = spawn(
  CHROME,
  [
    '--headless=new',
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${profile}`,
    '--window-size=1100,820',
    '--hide-scrollbars',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-extensions',
    'about:blank',
  ],
  { stdio: 'ignore' },
);

let browserWs;
try {
  let version;
  for (let i = 0; i < 50; i += 1) {
    try {
      version = await getJson(`http://127.0.0.1:${PORT}/json/version`);
      break;
    } catch {
      await delay(200);
    }
  }
  if (!version) throw new Error('Chrome no expuso el puerto de depuración');

  browserWs = new WebSocket(version.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    browserWs.onopen = resolve;
    browserWs.onerror = reject;
  });

  let nextId = 0;
  const pending = new Map();
  const listeners = new Set();
  const consola = [];

  browserWs.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
      return;
    }
    if (msg.method === 'Runtime.consoleAPICalled') {
      const texto = (msg.params.args ?? [])
        .map((a) => a.value ?? a.description ?? '')
        .join(' ');
      consola.push(texto);
    }
    listeners.forEach((listener) => listener(msg));
  };

  const send = (method, params = {}, sessionId) =>
    new Promise((resolve, reject) => {
      const id = ++nextId;
      pending.set(id, { resolve, reject });
      browserWs.send(
        JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }),
      );
    });

  const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
  const cmd = (method, params = {}) => send(method, params, sessionId);

  await cmd('Page.enable');
  await cmd('Runtime.enable');
  await cmd('Accessibility.enable');
  await cmd('Emulation.setDeviceMetricsOverride', {
    width: 1100,
    height: 820,
    deviceScaleFactor: 1,
    mobile: false,
  });

  const evalJs = async (expression) => {
    const result = await cmd('Runtime.evaluate', {
      expression,
      returnByValue: true,
    });
    return result.result.value;
  };

  const axLabels = async () => {
    const ax = await cmd('Accessibility.getFullAXTree');
    return ax.nodes.map((n) => n.name?.value).filter(Boolean);
  };

  const waitForLabels = async (predicado, timeout = 20000) => {
    const inicio = Date.now();
    while (Date.now() - inicio < timeout) {
      const labels = await axLabels();
      if (predicado(labels)) return labels;
      await delay(300);
    }
    throw new Error(`Timeout esperando etiquetas: ${(await axLabels()).join(' | ')}`);
  };

  const abrirApp = async () => {
    await cmd('Page.navigate', { url: APP_URL });
    for (let i = 0; i < 100; i += 1) {
      const listo = await evalJs(
        "!!document.querySelector('[aria-label=\"Enable accessibility\"]') || !!document.querySelector('flt-glass-pane')",
      );
      if (listo) break;
      await delay(200);
    }
    // Activa semántica de Flutter para poder localizar los controles.
    await evalJs(
      "document.querySelector('[aria-label=\"Enable accessibility\"]')?.click()",
    );
    await delay(800);
    await waitForLabels((labels) =>
      labels.some((l) => l.includes('Cien') || l.includes('Pedro')),
    );
    const domLabels = await evalJs(
      "[...document.querySelectorAll('[role]')].map(e => e.tagName + ':' + e.getAttribute('role') + ':' + (e.getAttribute('aria-label') || e.textContent || '')).slice(0, 30)",
    );
    console.log('Nodos con rol:', domLabels.join(' | '));
  };

  const centroDe = async (etiqueta, indice = 0) => {
    const punto = await evalJs(`(() => {
      const todos = [...document.querySelectorAll('[role]')];
      const texto = e => (e.getAttribute('aria-label') || e.textContent || '').trim();
      let els = todos.filter(e => texto(e) === ${JSON.stringify(etiqueta)});
      if (!els.length) {
        els = todos.filter(e => texto(e).startsWith(${JSON.stringify(etiqueta)}));
      }
      const el = els[${indice}];
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2, w: r.width, h: r.height };
    })()`);
    if (!punto) throw new Error(`No encontré el control "${etiqueta}" (índice ${indice})`);
    return punto;
  };

  const click = async (etiqueta, indice = 0) => {
    const { x, y } = await centroDe(etiqueta, indice);
    for (const type of ['mousePressed', 'mouseReleased']) {
      await cmd('Input.dispatchMouseEvent', {
        type,
        x,
        y,
        button: 'left',
        clickCount: 1,
      });
    }
    await delay(500);
  };

  const clickXY = async (x, y) => {
    for (const type of ['mousePressed', 'mouseReleased']) {
      await cmd('Input.dispatchMouseEvent', {
        type,
        x,
        y,
        button: 'left',
        clickCount: 1,
      });
    }
    await delay(300);
  };

  const escribir = async (texto) => {
    await cmd('Input.dispatchKeyEvent', {
      type: 'keyDown',
      windowsVirtualKeyCode: 65,
      modifiers: 2,
      key: 'a',
      code: 'KeyA',
    });
    await cmd('Input.dispatchKeyEvent', {
      type: 'keyUp',
      windowsVirtualKeyCode: 65,
      modifiers: 2,
      key: 'a',
      code: 'KeyA',
    });
    await cmd('Input.insertText', { text: texto });
    await delay(300);
  };

  const shot = async (archivo) => {
    const { data } = await cmd('Page.captureScreenshot', { format: 'png' });
    writeFileSync(path.join(OUT_DIR, archivo), Buffer.from(data, 'base64'));
    const labels = await axLabels();
    console.log(`Guardada: ${archivo}`);
    console.log(`  Etiquetas: ${labels.slice(0, 14).join(' | ')}`);
  };

  // ---------------------------------------------------------------- Figura 1
  await abrirApp();
  await waitForLabels((l) => l.includes('Editar (PUT)'));
  await shot('figura_1_lista_antes.png');

  // -------------------------------------------------- Reto: detalle GET /{id}
  await click('Cien años de soledad'); // coincide por prefijo con la etiqueta del ListTile
  await waitForLabels((l) => l.some((x) => x.includes('Detalle del libro')));
  await delay(600);
  await shot('figura_6_detalle.png');

  // ---------------------------------------------------------------- Figura 2
  await abrirApp();
  await click('Editar (PUT)', 0);
  await waitForLabels((l) => l.includes('Actualizar (PUT)'));
  await shot('figura_2_formulario_edicion.png');
  const rolesForm = await evalJs(
    "[...document.querySelectorAll('flt-semantics')].map(e => { const r = e.getBoundingClientRect(); return e.getAttribute('role') + ':' + (e.getAttribute('aria-label') || e.textContent || '') + '@' + Math.round(r.x) + ',' + Math.round(r.y) + ',' + Math.round(r.width) + ',' + Math.round(r.height); }).slice(0, 30)",
  );
  console.log('Nodos del formulario:', rolesForm.join(' | '));

  // El campo Título no expone rol en el DOM; su caja semántica es (16,72,1068,48).
  await clickXY(550, 96);
  await escribir('Cien años de soledad (editado)');
  await click('Disponible para préstamo');
  await delay(300);

  // ---------------------------------------------------------------- Figura 3
  // Hay dos nodos con ese texto: el group y el button; el botón es el índice 1.
  await click('Actualizar (PUT)', 1);
  await waitForLabels(
    (l) => l.some((x) => x.includes('(editado)')) && !l.some((x) => x.includes('Editar libro')),
  );
  await delay(800);
  await shot('figura_3_lista_despues_editar.png');

  // ---------------------------------------------------------------- Figura 4
  await click('Eliminar (DELETE)', 0);
  await waitForLabels((l) => l.includes('Eliminar libro'));
  await click('Eliminar');
  await delay(1200);
  await shot('figura_4_lista_despues_eliminar.png');

  // ---------------------------------------- Reto: 404 -> "El libro no existe"
  await abrirApp();
  // Navegamos por la URL a un id inexistente para provocar el 404 de la API.
  await evalJs("location.hash = '#/libro/999';");
  await waitForLabels(
    (l) => l.some((x) => x.includes('El libro no existe')),
    15000,
  );
  await delay(500);
  await shot('figura_7_no_existe.png');

  // -------------------------------------------------- Consola con PUT y DELETE
  const lineas = consola.filter((l) =>
    /PUT|DELETE|statusCode|response|request/i.test(l),
  );
  const html = `<!doctype html><html lang="es"><head><meta charset="utf-8">
  <title>Consola Flutter — PUT y DELETE</title>
  <style>body{margin:0;padding:20px;background:#1e1e1e;color:#d4d4d4;
  font-family:Consolas,"Courier New",monospace;font-size:15px;line-height:1.5}
  h2{font-family:Segoe UI,sans-serif;color:#569cd6;margin:0 0 12px;font-size:18px}
  .ok{color:#4ec9b0}</style></head><body>
  <h2>Consola Flutter / LogInterceptor — peticiones PUT y DELETE</h2>
  <pre>${lineas.map((l) => l.replace(/&/g, '&amp;').replace(/</g, '&lt;')).join('\n')}</pre>
  </body></html>`;
  writeFileSync(path.join(OUT_DIR, 'consola.html'), html, 'utf8');
  writeFileSync(path.join(OUT_DIR, 'consola.txt'), consola.join('\n'), 'utf8');
  console.log(`Líneas de consola relevantes: ${lineas.length}`);

  console.log('Evidencias generadas en', OUT_DIR);
} finally {
  browserWs?.close();
  chrome.kill();
}
