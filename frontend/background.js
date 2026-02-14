// Counter Speech Extension - Background Service Worker
chrome.action.onClicked.addListener(async (tab) => {
    // Cannot inject into browser internal pages
    if (!tab.url || tab.url.startsWith('chrome://') || tab.url.startsWith('edge://') || tab.url.startsWith('about:')) {
      return;
    }
  
    try {
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content.js']
      });
    } catch (err) {
      console.error('Counter Speech: Could not inject overlay', err);
    }
  });