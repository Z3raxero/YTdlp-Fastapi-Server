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
  if (info.menuItemId === "extract-audio") {  // Fixed: Added 'if' keyword
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
      
      console.log("Sending URL to server:", message.videoUrl);  // Debug log
      
      const response = await fetch(`${API_BASE_URL}/api/v1/extract-audio`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: message.videoUrl })  // Fixed: Changed 'videoUrl' to 'url'
      });
      
      console.log("Server response status:", response.status);  // Debug log
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error("Server error:", errorData);
        sendResponse({ success: false, error: errorData.detail || "Server error" });
        return;
      }
      
      const data = await response.json();
      console.log("Server response data:", data);  // Debug log
      
      // Start polling for completion
      pollForCompletion(data.job_id, sendResponse);
      
    } catch (e) {
      console.error("Request error:", e);  // Debug log
      sendResponse({ success: false, error: e.toString() });
    }
    return true;  // Indicates async response
  }
});

async function pollForCompletion(jobId, sendResponse) {
  const maxAttempts = 30;  // 30 attempts * 2 seconds = 1 minute timeout
  let attempts = 0;
  
  const checkStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/status/${jobId}`);
      const data = await response.json();
      
      console.log(`Job ${jobId} status:`, data.status);  // Debug log
      
      if (data.status === "completed") {
        // Open download link in new tab
        chrome.tabs.create({ url: `${API_BASE_URL}/api/v1/download/${jobId}` });
        sendResponse({ success: true, data });
      } else if (data.status.startsWith("failed")) {
        sendResponse({ success: false, error: `Processing failed: ${data.status}` });
      } else if (attempts < maxAttempts) {
        attempts++;
        setTimeout(checkStatus, 2000);  // Check again in 2 seconds
      } else {
        sendResponse({ success: false, error: "Processing timed out" });
      }
    } catch (e) {
      console.error("Status check error:", e);  // Debug log
      if (attempts < maxAttempts) {
        attempts++;
        setTimeout(checkStatus, 2000);
      } else {
        sendResponse({ success: false, error: "Status check timed out" });
      }
    }
  };
  
  checkStatus();
}