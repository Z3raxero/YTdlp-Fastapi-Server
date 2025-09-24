let API_BASE_URL = "";

// Load configuration
fetch(chrome.runtime.getURL('config.json'))
  .then(response => {
    if (!response.ok) {
      throw new Error(`Failed to load config: ${response.status}`);
    }
    return response.json();
  })
  .then(config => {
    console.log("Config loaded:", config);
    API_BASE_URL = config.API_BASE_URL;
    console.log("API_BASE_URL set to:", API_BASE_URL);
  })
  .catch(error => {
    console.error("Error loading config:", error);
    API_BASE_URL = "http://localhost:8000";
    console.log("Using default API_BASE_URL:", API_BASE_URL);
  });

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "extract-audio",
    title: "Extract Audio from Video",
    contexts: ["video"]
  });
  
  console.log("Extension installed, context menu created");
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  console.log("Context menu clicked:", info);
  if (info.menuItemId === "extract-audio") {
    console.log("Sending extract-audio message to tab:", tab.id);
    chrome.tabs.sendMessage(tab.id, { action: "extract-audio" }, (response) => {
      if (chrome.runtime.lastError) {
        console.error("Error sending message to tab:", chrome.runtime.lastError);
      }
    });
  } 
});

// Store active jobs to track progress
const activeJobs = {};

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log("Received message:", message);
  
  if (message.action === "sendVideoToServer") {
    // Send immediate response to prevent port closure
    sendResponse({ success: true, message: "Extraction started" });
    
    // Process extraction asynchronously
    processExtraction(message.videoUrl, sender.tab.id)
      .catch(error => {
        console.error("Extraction failed:", error);
        // Notify content script of failure
        chrome.tabs.sendMessage(sender.tab.id, {
          action: "extractionFailed",
          error: error.toString()
        });
      });
    
    return true; // Keep message channel open for async response
  }
  else if (message.action === "showNotification") {
    // Show notification based on type
    showNotification(message.type, message.message);
    return true;
  }
  
  return false;
});

// Function to show notifications (without icons)
function showNotification(type, message) {
  const titles = {
    info: "YouTube Audio Extractor",
    success: "Extraction Complete!",
    error: "Extraction Failed"
  };
  
  chrome.notifications.create({
    type: "basic",
    title: titles[type],
    message: message
  }, (notificationId) => {
    console.log(`Notification created with ID: ${notificationId}`);
    
    // Auto-close info notifications after 3 seconds
    if (type === "info") {
      setTimeout(() => {
        chrome.notifications.clear(notificationId, (wasCleared) => {
          console.log(`Notification ${notificationId} cleared: ${wasCleared}`);
        });
      }, 3000);
    }
  });
}

async function processExtraction(videoUrl, tabId) {
  try {
    // Wait for API_BASE_URL to be loaded
    while (!API_BASE_URL) {
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    
    console.log("Processing URL:", videoUrl);
    
    // Start extraction
    const response = await fetch(`${API_BASE_URL}/api/v1/extract-audio`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify({ url: videoUrl })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Server error: ${response.status}`);
    }
    
    const data = await response.json();
    console.log("Job created:", data.job_id);
    
    // Store job info
    activeJobs[data.job_id] = {
      tabId: tabId,
      videoUrl: videoUrl
    };
    
    // Start polling for completion
    pollForCompletion(data.job_id);
    
  } catch (error) {
    console.error("Error in processExtraction:", error);
    throw error;
  }
}

async function pollForCompletion(jobId) {
  console.log(`Polling for job ${jobId}`);
  
  const maxAttempts = 30;
  let attempts = 0;
  
  const checkStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/status/${jobId}`);
      const data = await response.json();
      
      console.log(`Job ${jobId} status:`, data.status);
      
      if (data.status === "completed") {
        console.log(`Job ${jobId} completed`);
        
        // Get job info
        const job = activeJobs[jobId];
        if (job) {
          // Open download in new tab
          chrome.tabs.create({ 
            url: `${API_BASE_URL}/api/v1/download/${jobId}`,
            active: false  // Open in background
          });
          
          // Notify content script
          chrome.tabs.sendMessage(job.tabId, {
            action: "extractionCompleted",
            jobId: jobId
          });
          
          // Clean up
          delete activeJobs[jobId];
        }
      } 
      else if (data.status.startsWith("failed")) {
        console.error(`Job ${jobId} failed:`, data.status);
        
        const job = activeJobs[jobId];
        if (job) {
          chrome.tabs.sendMessage(job.tabId, {
            action: "extractionFailed",
            error: `Processing failed: ${data.status}`
          });
          delete activeJobs[jobId];
        }
      }
      else if (attempts < maxAttempts) {
        attempts++;
        setTimeout(checkStatus, 2000);
      }
      else {
        console.error(`Job ${jobId} timed out`);
        
        const job = activeJobs[jobId];
        if (job) {
          chrome.tabs.sendMessage(job.tabId, {
            action: "extractionFailed",
            error: "Processing timed out"
          });
          delete activeJobs[jobId];
        }
      }
    } 
    catch (error) {
      console.error(`Error checking status for job ${jobId}:`, error);
      
      if (attempts < maxAttempts) {
        attempts++;
        setTimeout(checkStatus, 2000);
      } else {
        const job = activeJobs[jobId];
        if (job) {
          chrome.tabs.sendMessage(job.tabId, {
            action: "extractionFailed",
            error: "Status check failed"
          });
          delete activeJobs[jobId];
        }
      }
    }
  };
  
  checkStatus();
}