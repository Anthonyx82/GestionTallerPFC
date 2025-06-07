import puppeteer, { Page } from 'puppeteer';
import fs from 'fs';
import path from 'path';

const pages = [
  { route: '/', name: 'home', file: 'app.component.ts' },
  { route: '/register', name: 'registro', file: 'pages/register/register.component.ts' },
  { route: '/login', name: 'login', file: 'pages/login/login.component.ts' },
  { route: '/mis-vehiculos', name: 'mis-vehiculos', file: 'mis-vehiculos/mis-vehiculos.component.ts' },
  { route: '/editar-vehiculo/2', name: 'editar-vehiculo', file: 'editar-vehiculo/editar-vehiculo.component.ts' },
  { route: '/informe/56c0db69-cb5f-42ad-a31b-b77422533904', name: 'informe', file: 'informe-publico/informe-publico.component.ts' },
];


const baseUrl = 'https://anthonyx82.ddns.net/taller-front';
const screenshotsDir = path.join('src', 'assets', 'docs', 'screenshots');

const CREDENTIALS = {
  username: 'Antonio',
  password: 'Ams1313*',
};

async function getTokenFromApi(): Promise<string> {
  const response = await fetch('https://anthonyx82.ddns.net/taller/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(CREDENTIALS),
  });

  if (!response.ok) {
    throw new Error(`Error al iniciar sesión: ${response.status}`);
  }

  const data = await response.json();
  return data.access_token;
}

async function captureScreenshots() {
  const browser = await puppeteer.launch({ headless: true }); // corrected

  const token = await getTokenFromApi();

  if (!fs.existsSync(screenshotsDir)) {
    fs.mkdirSync(screenshotsDir, { recursive: true });
  }

  for (const { route, name } of pages) {
    const page = await browser.newPage();

    await page.goto(baseUrl, { waitUntil: 'domcontentloaded' });

    // Inyecta token en localStorage
    await page.evaluate((token: string) => {
      localStorage.setItem('token', token);
    }, token);

    await page.goto(`${baseUrl}${route}`, { waitUntil: 'networkidle0' });

    const filePath = path.join(screenshotsDir, `${name}.png`) as `${string}.png`;

    await page.screenshot({ path: filePath, fullPage: true });
    console.log(`✅ Captura hecha: ${filePath}`);

    await page.close();
  }

  await browser.close();
}


function injectJsDocImages() {
  for (const { name, file } of pages) {
    const componentPath = path.join('src', 'app', file);
    if (!fs.existsSync(componentPath)) {
      console.warn(`⚠️ Archivo no encontrado: ${componentPath}`);
      continue;
    }

    const content = fs.readFileSync(componentPath, 'utf-8');
    const lines = content.split('\n');

    const imageMarkdown = ` * ![${name}](../assets/docs/screenshots/${name}.png)`;

    let inJSDoc = false;
    let injected = false;
    
    const newLines = lines.map((line, index) => {
      if (injected) return line;

      if (line.trim().startsWith('/**') && !inJSDoc) {
        inJSDoc = true;

        // Insert image markdown just after `/**`
        if (!lines[index + 1]?.includes('![')) {
          injected = true;
          return `${line}\n${imageMarkdown}`;
        }
      }

      if (line.trim().startsWith('*/') && inJSDoc) {
        inJSDoc = false;
      }

      return line;
    });

    if (injected) {
      fs.writeFileSync(componentPath, newLines.join('\n'), 'utf-8');
      console.log(`🖊️ Imagen inyectada en: ${file}`);
    } else {
      console.log(`ℹ️ Ya contenía imagen o no se encontró bloque JSDoc: ${file}`);
    }
  }
}

(async () => {
  await captureScreenshots();
  //injectJsDocImages();
})();
