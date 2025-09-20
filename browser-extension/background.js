let API_BASE_URL = "";

fetch(chrome.runtime.getURL('config.json'))
  .then(response => response.json())
  .then(config => {
    API_BASE_URL = config.API_BASE_URL;
  });

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "extract-audio",
    title: "Extract Audio from Video",
    contexts: ["video"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "extract-audio") {
    chrome.tabs.sendMessage(tab.id, { action: "extract-audio" });
  }
});

chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
  if (message.action === "sendVideoToServer") {
    try {
      // Wait for API_BASE_URL to be loaded
      while (!API_BASE_URL) {
        await new Promise(resolve => setTimeout(resolve, 50));
      }
      const response = await fetch(`${API_BASE_URL}/api/v1/extract-audio`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ videoUrl: message.videoUrl })
      });
      const data = await response.json();
      sendResponse({ success: true, data });
    } catch (e) {
      sendResponse({ success: false, error: e.toString() });
    }
    return true;
  }
});
