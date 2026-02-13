// Counter Speech Extension - Content Script
// Injects a persistent overlay that stays open until the user clicks the close button

(function () {
    const OVERLAY_ID = 'counterspeech-extension-overlay';
    const POPUP_URL = chrome.runtime.getURL('popup.html');
  
    let overlay = document.getElementById(OVERLAY_ID);
  
    if (overlay) {
      // If overlay already exists, remove it completely so a fresh
      // instance (with cleared inputs) is created next time.
      overlay.remove();
      return;
    }
  
    // Create overlay container (transparent - clicks outside pass through to page)
    overlay = document.createElement('div');
    overlay.id = OVERLAY_ID;
    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      display: flex;
      justify-content: flex-end;
      align-items: flex-start;
      padding: 60px 16px 16px;
      box-sizing: border-box;
      z-index: 2147483647;
      pointer-events: none;
    `;
  
    // Create panel wrapper (enables pointer events for the panel only)
    const panelWrapper = document.createElement('div');
    panelWrapper.style.cssText = `
      position: relative;
      width: 432px;
      max-width: calc(100vw - 32px);
      max-height: calc(100vh - 80px);
      background: #f5f5f5;
      border-radius: 8px;
      box-shadow: 0 4px 24px rgba(0,0,0,0.15);
      pointer-events: auto;
      overflow: hidden;
    `;
  
    // Close button (X) in the corner
    const closeBtn = document.createElement('button');
    closeBtn.setAttribute('aria-label', 'Close');
    closeBtn.innerHTML = '×';
    closeBtn.style.cssText = `
      position: absolute;
      top: 8px;
      right: 8px;
      width: 32px;
      height: 32px;
      border: none;
      background: transparent;
      color: #666;
      font-size: 24px;
      line-height: 1;
      cursor: pointer;
      z-index: 10;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0;
      transition: background 0.2s, color 0.2s;
    `;
    closeBtn.addEventListener('mouseenter', () => {
      closeBtn.style.background = 'rgba(0,0,0,0.08)';
      closeBtn.style.color = '#333';
    });
    closeBtn.addEventListener('mouseleave', () => {
      closeBtn.style.background = 'transparent';
      closeBtn.style.color = '#666';
    });
    closeBtn.addEventListener('click', () => {
      // Remove the overlay entirely so that reopening creates
      // a fresh iframe with empty inputs and default state.
      overlay.remove();
    });
  
    // Iframe containing the popup
    const iframe = document.createElement('iframe');
    iframe.src = POPUP_URL;
    iframe.style.cssText = `
      width: 100%;
      height: min(90vh, 700px);
      border: none;
      display: block;
    `;
  
    panelWrapper.appendChild(closeBtn);
    panelWrapper.appendChild(iframe);
    overlay.appendChild(panelWrapper);
    document.documentElement.appendChild(overlay);
  })();