(() => {
  // Only inject once
  if (document.getElementById('fz-tts-btn')) return;

  // --- Extraction helpers ---

  function slugify(text) {
    return text
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/[\s_]+/g, '-')
      .replace(/^-+|-+$/g, '');
  }

  function extractChapter() {
    const novelEl = document.querySelector('span.novel-title');
    const novelTitle = novelEl ? novelEl.textContent.trim() : 'unknown-novel';
    const novelSlug = slugify(novelTitle);

    const titleEl =
      document.querySelector('h1.chapter-article-title') ||
      document.querySelector('h1.chapter-title');
    const chapterTitle = titleEl ? titleEl.textContent.trim() : 'Unknown Chapter';

    const progressEl = document.querySelector('span.chapter-progress');
    let chapterNum = 1;
    if (progressEl) {
      const m = progressEl.textContent.trim().match(/^(\d+)/);
      if (m) chapterNum = parseInt(m[1], 10);
    }

    const contentDiv = document.querySelector('div.chapter-text');
    if (!contentDiv) return null;

    const clone = contentDiv.cloneNode(true);
    clone.querySelectorAll('div.ad-slot').forEach(el => el.remove());

    const paragraphs = [...clone.querySelectorAll('p')]
      .map(p => p.textContent.trim())
      .filter(Boolean);

    if (!paragraphs.length) return null;

    return {
      novel_slug: novelSlug,
      novel_title: novelTitle,
      chapter_num: chapterNum,
      chapter_title: chapterTitle,
      text: paragraphs.join('\n\n'),
    };
  }

  // --- UI ---

  function showToast(msg, color = '#2563eb') {
    const t = document.createElement('div');
    t.textContent = msg;
    Object.assign(t.style, {
      position: 'fixed',
      bottom: '80px',
      right: '20px',
      background: color,
      color: '#fff',
      padding: '10px 16px',
      borderRadius: '8px',
      fontSize: '14px',
      zIndex: '999999',
      boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
      transition: 'opacity 0.4s',
    });
    document.body.appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; }, 2000);
    setTimeout(() => t.remove(), 2500);
  }

  function createButton() {
    const btn = document.createElement('button');
    btn.id = 'fz-tts-btn';
    btn.textContent = '💾 Save for TTS';
    Object.assign(btn.style, {
      position: 'fixed',
      bottom: '20px',
      right: '20px',
      zIndex: '999999',
      background: '#2563eb',
      color: '#fff',
      border: 'none',
      borderRadius: '8px',
      padding: '10px 18px',
      fontSize: '14px',
      fontWeight: 'bold',
      cursor: 'pointer',
      boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
    });

    btn.addEventListener('click', () => {
      const data = extractChapter();
      if (!data) {
        showToast('❌ Chapter content not found', '#dc2626');
        return;
      }

      const filename = `fictionzone-tts/chapter-${String(data.chapter_num).padStart(4, '0')}-${data.novel_slug}.json`;
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);

      chrome.runtime.sendMessage({ action: 'download', url, filename }, () => {
        URL.revokeObjectURL(url);
        showToast(`✅ Saved: ${data.chapter_title}`);
      });
    });

    return btn;
  }

  document.body.appendChild(createButton());
})();
