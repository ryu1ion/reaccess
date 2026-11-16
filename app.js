/* Small progressive enhancements; the paper and figures remain available without JS. */
const progress = document.querySelector('.reading-progress');
let scrollScheduled = false;
function updateProgress() {
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  progress.style.width = `${scrollable > 0 ? window.scrollY / scrollable * 100 : 0}%`;
  scrollScheduled = false;
}
window.addEventListener('scroll', () => {
  if (!scrollScheduled) { requestAnimationFrame(updateProgress); scrollScheduled = true; }
}, { passive: true });
window.addEventListener('resize', updateProgress);
window.addEventListener('load', updateProgress);

const navigation = [...document.querySelectorAll('.nav-links a')];
if ('IntersectionObserver' in window) {
  const sections = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      navigation.forEach(link => {
        const active = link.hash === `#${entry.target.id}`;
        link.classList.toggle('active', active);
        if (active) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    });
  }, { rootMargin: '-10% 0px -65% 0px', threshold: 0 });
  navigation.forEach(link => sections.observe(document.querySelector(link.hash)));
}

const dialog = document.querySelector('#figure-dialog');
const dialogImage = document.querySelector('#dialog-image');
const imageArea = document.querySelector('#dialog-image-area');
const zoomToggle = document.querySelector('#zoom-toggle');
let lastFigure;
function setZoom(zoomed) {
  imageArea.classList.toggle('zoomed', zoomed);
  zoomToggle.textContent = zoomed ? 'Fit to screen' : 'Zoom in';
  zoomToggle.setAttribute('aria-pressed', String(zoomed));
  imageArea.scrollTop = 0;
  imageArea.scrollLeft = 0;
}
document.querySelectorAll('[data-lightbox]').forEach(link => {
  link.addEventListener('click', event => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || typeof dialog.showModal !== 'function') return;
    event.preventDefault();
    lastFigure = link;
    dialogImage.src = link.href;
    dialogImage.alt = link.querySelector('img').alt;
    document.querySelector('#dialog-title').textContent = link.dataset.title;
    document.querySelector('#dialog-pdf').href = link.dataset.pdf;
    imageArea.style.setProperty('--zoom-width', `${Math.max(1500, Math.min(2300, window.innerWidth * 1.65))}px`);
    setZoom(false);
    dialog.showModal();
    document.body.classList.add('modal-open');
  });
});
zoomToggle.addEventListener('click', () => setZoom(!imageArea.classList.contains('zoomed')));
dialogImage.addEventListener('click', () => setZoom(!imageArea.classList.contains('zoomed')));
document.querySelector('#dialog-close').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => {
  if (event.target !== dialog) return;
  const bounds = dialog.getBoundingClientRect();
  if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
});
dialog.addEventListener('close', () => {
  document.body.classList.remove('modal-open');
  setZoom(false);
  lastFigure?.focus({ preventScroll: true });
});

const copyButton = document.querySelector('#copy-citation');
copyButton.addEventListener('click', async () => {
  const text = document.querySelector('#bibtex').textContent;
  try {
    if (navigator.clipboard && window.isSecureContext) await navigator.clipboard.writeText(text);
    else {
      const temporary = document.createElement('textarea');
      temporary.value = text;
      temporary.style.cssText = 'position:fixed;left:-9999px;top:0';
      document.body.append(temporary);
      temporary.select();
      const copied = document.execCommand('copy');
      temporary.remove();
      if (!copied) throw new Error('Copy unavailable');
    }
    copyButton.querySelector('span').textContent = 'Copied!';
    document.querySelector('#copy-status').textContent = 'BibTeX copied to clipboard.';
    setTimeout(() => { copyButton.querySelector('span').textContent = 'Copy BibTeX'; }, 2200);
  } catch {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(document.querySelector('#bibtex'));
    selection.removeAllRanges(); selection.addRange(range);
    document.querySelector('#copy-status').textContent = 'Select and copy the highlighted citation.';
    copyButton.querySelector('span').textContent = 'Select & copy';
  }
});
