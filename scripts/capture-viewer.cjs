// README procedure: actual viewer, keyboard folds, immutable JSON; no server.
'use strict';
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const assert = require('assert/strict');
const {pathToFileURL} = require('url');
const THREE_URL = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
const THREE_SHA256 = '9274bbcec8d96168626c732b5d31c775aa8cfb7eaa0599bec0c175908a2c1ce2';
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const dependency = message => { const e = new Error(`LOOK: NOT RUN — ${message}`); e.code = 2; throw e; };
const escape = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const image = bytes => `data:image/png;base64,${bytes.toString('base64')}`;
let activeBrowser = null, cancelled = false;
process.on('SIGTERM', () => {
  cancelled = true;
  if (activeBrowser) activeBrowser.close().catch(() => {});
});

async function captureBlank(browser, blank, three, intercepted) {
  const page = await browser.newPage({viewport:{width:1440,height:1100}, reducedMotion:'reduce', serviceWorkers:'block'});
  const errors = [], external = [], failed = [];
  const localURLs = new Set([pathToFileURL(blank.viewer).href, pathToFileURL(blank.svg).href]);
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', e => { if (e.type() === 'error') errors.push(e.text()); });
  page.on('requestfailed', r => failed.push({url:r.url(),error:r.failure()}));
  await page.route('**/*', async route => {
    const url = route.request().url();
    if (url === THREE_URL) { intercepted.push(url); await route.fulfill({body:three,contentType:'application/javascript'}); }
    else if (localURLs.has(url) || url.startsWith('data:')) await route.continue();
    else { external.push(url); await route.abort('blockedbyclient'); }
  });
  if (typeof page.routeWebSocket !== 'function') {await page.close();dependency('cached Playwright lacks WebSocket interception');}
  await page.routeWebSocket('**/*', socket => {
    external.push(socket.url()); socket.close();
  });
  try {
    assert.equal(hash(fs.readFileSync(blank.viewer)),blank.viewer_hash,'L5: viewer changed before capture');
    await page.goto(pathToFileURL(blank.viewer).href,{waitUntil:'networkidle'});
    await page.waitForFunction(()=>document.querySelector('#three-viewport').getAttribute('aria-busy')==='false');
    const original = await page.locator('#fold-model').textContent();
    assert.deepEqual(JSON.parse(original),blank.model,'L7: rendered model differs from source');
    assert.equal(await page.locator('h1').textContent(),blank.name,'L3: incorrect displayed model');
    assert.equal(await page.locator('.cad-canvas svg').count(),1,'L9: missing SVG');
    const proof = {name:blank.name,available:blank.model.available,frames:[],checks:{L7:'PASS'},
                   viewer_hash:blank.viewer_hash,svg_hash:blank.svg_hash};
    const pictures = [];
    if (blank.model.available) {
      const slider = page.locator('#fold-slider');
      assert.equal(await slider.getAttribute('aria-disabled'),'false','L4: slider disabled');
      for (const progress of [25,50,75,100]) {
        await slider.focus(); await slider.press('Home');
        for (let n=0;n<progress;n++) await slider.press('ArrowRight');
        assert.equal(await slider.getAttribute('aria-valuenow'),String(progress),'L4: requested progress missed');
        assert.equal(await page.locator('#fold-percent').textContent(),`${progress}%`,'L4: label mismatch');
        await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
        const pixels = await page.locator('#three-viewport canvas').evaluate(canvas=>{
          const gl=canvas.getContext('webgl2')||canvas.getContext('webgl');
          if (!gl||!canvas.width||!canvas.height) return {nonblank:false};
          const data=new Uint8Array(canvas.width*canvas.height*4);
          gl.readPixels(0,0,canvas.width,canvas.height,gl.RGBA,gl.UNSIGNED_BYTE,data);
          let distinct=0;
          for(let n=4;n<data.length;n+=4) if(data[n]!==data[0]||data[n+1]!==data[1]||data[n+2]!==data[2]) distinct++;
          return {nonblank:distinct>0,distinct_pixels:distinct,width:canvas.width,height:canvas.height};
        });
        assert.equal(pixels.nonblank,true,'L6: canvas is blank');
        assert.equal(await page.locator('#fold-model').textContent(),original,'L5: controls changed model');
        const png=await page.screenshot({fullPage:true});
        pictures.push({title:`${blank.name} · ${progress}% · Preview available`,png});
        proof.frames.push({progress,sha256:hash(png),canvas:pixels});
      }
      Object.assign(proof.checks,{L4:'PASS',L6:'PASS',L9:'NOT APPLICABLE — preview available'});
    } else {
      assert.equal(await page.locator('#three-viewport canvas').count(),0,'L9: unavailable preview has canvas');
      assert.equal(await page.locator('#fold-slider').getAttribute('aria-disabled'),'true','L9: enabled unavailable control');
      proof.status=await page.locator('#fold-status').textContent();
      assert.equal(proof.status,blank.model.status,'L9: source unavailable status changed');
      pictures.push({title:`${blank.name} · 3D unavailable · ${proof.status}`,png:await page.screenshot({fullPage:true})});
      Object.assign(proof.checks,{L4:'NOT APPLICABLE — unavailable',L6:'NOT APPLICABLE — unavailable',L9:'PASS'});
    }
    assert.equal(await page.locator('#fold-model').textContent(),original,'L5: model changed');
    assert.equal(hash(fs.readFileSync(blank.viewer)),blank.viewer_hash,'L5: viewer changed during capture');
    assert.deepEqual(errors,[],'L8: browser errors');
    assert.deepEqual(external,[],'L8: rejected external requests');
    assert.deepEqual(failed,[],'L8: resource failures');
    Object.assign(proof.checks,{L5:'PASS',L8:'PASS'});
    return {proof,pictures};
  } finally { await page.close(); }
}

async function capture(job) {
  const cache=path.resolve(job.browser_cache),threePath=path.join(cache,'three-r128.min.js');
  let three;
  try {three=fs.readFileSync(threePath);} catch {dependency('pinned Three r128 cache unavailable');}
  if(hash(three)!==THREE_SHA256) dependency('pinned Three r128 cache checksum mismatch');
  let chromium;
  try {({chromium}=require(path.join(cache,'node_modules/playwright')));} catch {dependency('cached Playwright unavailable');}
  const configPath=path.join(cache,'browser.json');
  const suffix=chromium.executablePath().match(/[\\/](chromium-\d+[\\/].*)$/);
  let executable=suffix?path.join(cache,'browsers',suffix[1]):null;
  if(fs.existsSync(configPath)) {
    try {
      const config=JSON.parse(fs.readFileSync(configPath,'utf8'));
      if(typeof config.executable_path!=='string'||!path.isAbsolute(config.executable_path)) dependency('browser.json needs absolute executable_path');
      executable=config.executable_path;
    } catch(e) {dependency(`invalid browser cache configuration: ${e.message}`);}
  }
  if(!executable||!fs.existsSync(executable)) dependency('cached Chromium executable unavailable');
  let browser;
  try {browser=await chromium.launch({headless:true,executablePath:executable,
    args:['--disable-background-networking','--disable-component-update','--disable-sync']});}
  catch(e) {dependency(`Chromium launch failed: ${e.message}`);}
  activeBrowser = browser;
  const proofs=[],pictures=[],intercepted=[];
  try {
    for(const blank of job.blanks) {
      if (cancelled) throw new Error('look: operation cancelled');
      const result=await captureBlank(browser,blank,three,intercepted);proofs.push(result.proof);
      const svg=fs.readFileSync(blank.svg);assert.equal(hash(svg),blank.svg_hash,'L5: SVG changed during capture');
      const flat=await browser.newPage({viewport:{width:1440,height:900}});
      try {
        const blocked=[];
        await flat.route('**/*',route=>{
          if(route.request().url().startsWith('data:')) return route.continue();
          blocked.push(route.request().url());return route.abort('blockedbyclient');
        });
        await flat.setContent(`<html lang="en"><head><title>Full source blank</title><style>body{margin:0;background:#FFFFFF;color:#232327;font:16px system-ui}h1{font-size:24px;margin:24px}img{display:block;width:1392px;height:800px;object-fit:contain;margin:24px}</style></head><body><h1>${escape(blank.name)} · Full source SVG</h1><img alt="Full source dieline" src="data:image/svg+xml;base64,${svg.toString('base64')}"></body></html>`);
        await flat.locator('img').evaluate(img=>img.decode());
        assert.deepEqual(blocked,[],'L8: external SVG resources');
        pictures.push({title:`${blank.name} · Full source SVG`,png:await flat.screenshot({fullPage:true})},...result.pictures);
      } finally {await flat.close();}
    }
    const sheet=await browser.newPage({viewport:{width:1440,height:1100}});
    try {
      await sheet.setContent(`<html lang="en"><head><title>DESIGN:OS Origami look sheet</title><style>body{margin:0;background:#FFFFFF;color:#232327;font:16px/1.5 system-ui}main{padding:24px}h1{font-size:24px;margin:0 0 16px}p{margin:0 0 24px;color:#6F6F78}.frames{display:grid;grid-template-columns:1fr 1fr;gap:24px}figure{margin:0;min-width:0}figure:first-child{grid-column:1/-1}img{display:block;width:100%;height:auto}figcaption{font-size:14px;overflow-wrap:anywhere;margin:8px 0}</style></head><body><main><h1>DESIGN:OS Origami · Source-bound look sheet</h1><p>1440px captures · Sampled continuity only · Physical fold/fit and recipient import: NOT VERIFIED</p><div class="frames">${pictures.map(p=>`<figure><img alt="${escape(p.title)}" src="${image(p.png)}"><figcaption>${escape(p.title)}</figcaption></figure>`).join('')}</div></main></body></html>`);
      await sheet.locator('img').evaluateAll(images=>Promise.all(images.map(img=>img.decode())));
      assert.equal(await sheet.evaluate(()=>document.documentElement.scrollWidth),1440,'sheet overflow');
      const bytes=await sheet.screenshot({fullPage:true});
      if (cancelled) throw new Error('look: operation cancelled');
      fs.mkdirSync(path.dirname(job.sheet),{recursive:true});fs.writeFileSync(job.sheet,bytes,{flag:'wx'});
      const receipt={schema_version:1,ok:true,sheet:job.sheet,sheet_hash:hash(bytes),
        artifact_hash:job.artifact_hash,source_hash:job.source_hash,contract_hash:job.contract_hash,
        dependency:{three_url:THREE_URL,three_sha256:THREE_SHA256,intercepted,
          playwright:require(path.join(cache,'node_modules/playwright/package.json')).version,chromium:browser.version()},
        viewport:{width:1440,height:1100},responsive:'SKIPPED (owner default)',blanks:proofs,
        visual_checks:'L1-L3 require human inspection',physical_fold_fit:'NOT VERIFIED',recipient_import:'NOT VERIFIED'};
      fs.writeFileSync(job.receipt,JSON.stringify(receipt,null,2)+'\n',{flag:'wx'});return receipt;
    } finally {await sheet.close();}
  } finally {await browser.close();activeBrowser=null;}
}

if(require.main===module) {
  Promise.resolve().then(()=>JSON.parse(fs.readFileSync(0,'utf8'))).then(capture)
    .then(result=>process.stdout.write(JSON.stringify(result)+'\n'))
    .catch(e=>{process.stderr.write(e.message+'\n');process.exitCode=e.code===2?2:1;});
}
module.exports={capture,THREE_URL,THREE_SHA256};
