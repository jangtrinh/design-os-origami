"""One deep-linkable light catalogue surface over actual generated blank viewers."""
import html
from pathlib import Path
import re

from origami_cad.preview_model import build_preview_model
from origami_cad.viewer_html import generate_viewer_html, _script_json
from origami_cad.viewer_navigation import with_navigation


STYLE = '''
:root{--paper:#FFFFFF;--ink:#232327;--secondary:#6F6F78;--surface:#F4F4F6;--border:#E0E0E4;--line:#898992}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1120px;margin:auto;padding:24px 20px}h1{font-size:24px;line-height:1.3;margin:12px 0 8px}p{max-width:60ch;color:var(--secondary);font-size:14px}
.back{display:inline-flex;min-height:44px;align-items:center;color:var(--ink)}.chips{display:flex;flex-wrap:wrap;margin:16px -4px 0}
.chips a{display:flex;min-height:44px;align-items:center;margin:4px;padding:8px 12px;border:1px solid var(--border);border-radius:6px;color:var(--ink);text-decoration:none;font:12px/1.5 ui-monospace,SFMono-Regular,Consolas,monospace}
.chips a[aria-current="page"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}a:focus-visible{outline:2px solid var(--ink);outline-offset:3px}
iframe{display:block;width:100%;height:1100px;border:0}iframe[hidden]{display:none}#selection-status{margin:12px 0 0}
@media(hover:hover){.chips a:hover:not([aria-current]){background:var(--surface)}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto}}
'''

SCRIPT = '''
const choices = JSON.parse(document.getElementById('blank-choices').textContent);
const frame = document.getElementById('blank-viewer'), status = document.getElementById('selection-status');
const links = [...document.querySelectorAll('[data-model]')];
function choose(slug, updateURL) {
  const entry = choices.find(row => row.slug === slug);
  for (const link of links) {
    if (entry && link.dataset.model === slug) link.setAttribute('aria-current','page');
    else link.removeAttribute('aria-current');
  }
  if (!entry) {
    frame.hidden = true; frame.removeAttribute('src'); frame.setAttribute('aria-busy','false');
    status.textContent = 'Unknown blank. Choose a model above.'; return;
  }
  frame.hidden = false; frame.setAttribute('aria-busy','true');
  frame.title = entry.label + ': actual 2D dieline and fold preview';
  frame.src = entry.file;
  status.textContent = entry.label + (entry.available ? ' · 3D preview available' : ' · 2D available; 3D preview unavailable');
  if (updateURL) history.pushState(null,'',entry.deep_link);
}
for (const link of links) link.addEventListener('click', event => {
  if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  event.preventDefault(); choose(link.dataset.model,true);
});
frame.addEventListener('load', () => frame.setAttribute('aria-busy','false'));
addEventListener('message',event => {
  if (event.source !== frame.contentWindow || event.data?.type !== 'origami-viewer-height') return;
  const height = event.data.height;
  if (Number.isFinite(height) && height >= 200 && height <= 5000) frame.style.height = Math.ceil(height) + 'px';
});
const selected = () => new URLSearchParams(location.search).get('model') || choices[0].slug;
addEventListener('popstate',()=>choose(selected(),false));
choose(selected(),false);
if (window.parent !== window) {
  const notify = () => parent.postMessage({type:'origami-catalog-height',height:document.documentElement.scrollHeight}, '*');
  new ResizeObserver(notify).observe(document.body); addEventListener('load',notify);
}
'''


def generate_catalog_viewer(entries, output_dir):
    """Publish one source-derived viewer per blank and one query-addressable switcher."""
    slugs = [entry['slug'] for entry in entries]
    if not slugs or len(set(slugs)) != len(slugs) or any(not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) for slug in slugs):
        raise ValueError('Viewer entries require unique safe slugs')
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    choices = []
    for entry in entries:
        slug = entry['slug']
        file = target/(slug+'.html')
        model = build_preview_model(entry['cp'])
        page = with_navigation(generate_viewer_html(entry['cp'], str(file)))
        page = page.replace('<head>', '<head><link rel="canonical" href="https://jangtrinh.github.io/design-os-origami/demo/'+slug+'.html">')
        file.write_text(page, encoding='utf-8')
        choices.append(dict(slug=slug, label=entry['label'], file=file.name,
                            available=model['available'], deep_link='index.html?model='+slug))
    links = ''.join(f'<a href="{row["file"]}" data-model="{row["slug"]}">{html.escape(row["label"])}</a>' for row in choices)
    count = sum(row['available'] for row in choices)
    page = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="canonical" href="https://jangtrinh.github.io/design-os-origami/demo/index.html">
<title>Choose a blank · DESIGN:OS Origami fold preview</title><style>{STYLE}</style></head>
<body><main><a class="back" href="../index.html">Back to DESIGN:OS Origami</a>
<h1>Choose a blank.</h1><p>{len(choices)} blanks · {count} with 3D. Each drawing and preview uses its actual source geometry.</p>
<nav class="chips" aria-label="Choose a blank">{links}</nav>
<p id="selection-status" role="status" aria-live="polite">Select a blank to inspect.</p>
<iframe id="blank-viewer" src="{choices[0]['file']}" title="Actual 2D dieline and fold preview" aria-busy="true"></iframe>
<noscript><p>Use the model links to open each standalone 2D drawing. 3D requires JavaScript and WebGL.</p></noscript>
</main><script id="blank-choices" type="application/json">{_script_json(choices)}</script><script>{SCRIPT}</script></body></html>'''
    (target/'index.html').write_text(page, encoding='utf-8')
    return page
