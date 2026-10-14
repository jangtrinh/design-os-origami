// Only the embedded, source-generated viewer may report its required height.
const previewFrame = document.querySelector('iframe.demo');
if (previewFrame) addEventListener('message', event => {
  if (event.source !== previewFrame.contentWindow || event.data?.type !== 'origami-catalog-height') return;
  const height = event.data.height;
  if (Number.isFinite(height) && height >= 200 && height <= 8000)
    previewFrame.style.height = Math.ceil(height) + 'px';
});
