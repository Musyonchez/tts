(() => {
  if (document.getElementById('nh-tts-btn')) return;

  // --- Helpers ---

  function slugify(text) {
    return text
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/[\s_]+/g, '-')
      .replace(/^-+|-+$/g, '');
  }

  function extractChapterNum(title) {
    const m = title.match(/chapter[\s\-_]*(\d+)/i);
    return m ? parseInt(m[1], 10) : null;
  }

  function extractChapter() {
    // Novel title — <a id="bookname">
    const novelEl = document.querySelector('a#bookname');
    const novelTitle = novelEl ? novelEl.textContent.trim() : 'unknown-novel';
    const novelSlug = slugify(novelTitle);

    // Chapter title — <h1> inside .single-header
    const titleEl = document.querySelector('.single-header h1') || document.querySelector('h1');
    const chapterTitle = titleEl ? titleEl.textContent.trim() : 'Unknown Chapter';

    // Chapter number from title text e.g. "Chapter 6: ..."
    const chapterNum = extractChapterNum(chapterTitle) || 1;

    // Content — div#htmlContent, text separated by <br><br>
    const contentDiv = document.querySelector('div#htmlContent');
    if (!contentDiv) return null;

    const clone = contentDiv.cloneNode(true);
    clone.querySelectorAll('script, style, iframe, .ads').forEach(el => el.remove());

    // Replace <br> with newlines, then split into paragraphs
    clone.querySelectorAll('br').forEach(br => br.replaceWith('\n'));
    const text = clone.innerText
      .split('\n')
      .map(l => l.trim())
      .filter(Boolean)
      .join('\n\n');

    if (!text) return null;

    return { novel_slug: novelSlug, novel_title: novelTitle, chapter_num: chapterNum, chapter_title: chapterTitle, text };
  }

  // --- UI ---

  const SAVE_ICON = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display:block">
    <path d="M12 3v13M5 10l7 7 7-7"/><line x1="3" y1="21" x2="21" y2="21"/>
  </svg>`;

  function showToast(msg, success = true) {
    const t = document.createElement('div');
    t.textContent = msg;
    Object.assign(t.style, {
      position: 'fixed', bottom: '72px', right: '20px',
      background: success ? '#fff' : '#111',
      color: success ? '#111' : '#fff',
      border: `1px solid ${success ? '#ccc' : '#444'}`,
      padding: '9px 14px', borderRadius: '6px', fontSize: '13px',
      fontFamily: 'system-ui, sans-serif', fontWeight: '500',
      zIndex: '999999', boxShadow: '0 2px 10px rgba(0,0,0,0.15)',
      opacity: '1', transition: 'opacity 0.4s',
      maxWidth: '320px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
    });
    document.body.appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; }, 2200);
    setTimeout(() => t.remove(), 2700);
  }

  function createButton() {
    const btn = document.createElement('button');
    btn.id = 'nh-tts-btn';
    btn.innerHTML = SAVE_ICON;
    btn.title = 'Save for TTS';
    Object.assign(btn.style, {
      position: 'fixed', bottom: '20px', right: '20px', zIndex: '999999',
      background: '#111', color: '#fff', border: '1px solid #333',
      borderRadius: '8px', width: '40px', height: '40px',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      cursor: 'pointer', boxShadow: '0 2px 8px rgba(0,0,0,0.35)', padding: '0',
    });

    btn.addEventListener('mouseenter', () => { btn.style.background = '#333'; });
    btn.addEventListener('mouseleave', () => { btn.style.background = '#111'; });

    btn.addEventListener('click', () => {
      const data = extractChapter();
      if (!data) {
        showToast('Chapter content not found', false);
        return;
      }
      const filename = `novelhall-tts/chapter-${String(data.chapter_num).padStart(4, '0')}-${data.novel_slug}.json`;
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      chrome.runtime.sendMessage({ action: 'download', url, filename }, () => {
        URL.revokeObjectURL(url);
        showToast(`Saved: ${data.chapter_title}`);
      });
    });

    return btn;
  }

  document.body.appendChild(createButton());
})();
