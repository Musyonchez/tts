chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.action === 'download') {
    chrome.downloads.download(
      { url: msg.url, filename: msg.filename, saveAs: false },
      () => sendResponse({})
    );
    return true;
  }
});
