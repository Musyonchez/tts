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
    // Novel title → slug for folder name
    const novelEl = document.querySelector('span.novel-title');
    const novelTitle = novelEl ? novelEl.textContent.trim() : 'unknown-novel';
    const novelSlug = slugify(novelTitle);

    // Chapter title
    const titleEl =
      document.querySelector('h1.chapter-article-title') ||
      document.querySelector('h1.chapter-title');
    const chapterTitle = titleEl ? titleEl.textContent.trim() : 'Unknown Chapter';

    // Chapter number from progress "1 / 325"
    const progressEl = document.querySelector('span.chapter-progress');
    let chapterNum = 1;
    if (progressEl) {
      const m = progressEl.textContent.trim().match(/^(\d+)/);
      if (m) chapterNum = parseInt(m[1], 10);
    }

    // Chapter text — paragraphs inside div.chapter-text, skip ads
    const contentDiv = document.querySelector('div.chapter-text');
    if (!contentDiv) return null;

    // Remove ad slots from a clone so we don't mutate the page
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
    btn.textContent = '📋 Copy for TTS';
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

      const payload = JSON.stringify(data, null, 2);
      navigator.clipboard.writeText(payload).then(() => {
        showToast(`✅ Copied: ${data.chapter_title}`);
      }).catch(() => {
        // Fallback for older clipboard API
        const ta = document.createElement('textarea');
        ta.value = payload;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        ta.remove();
        showToast(`✅ Copied: ${data.chapter_title}`);
      });
    });

    return btn;
  }

  document.body.appendChild(createButton());
})();
