console.log("Content script loaded");

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  console.log("Content script received message:", msg);
  
  if (msg.action === "extract-audio") {
    const pageUrl = window.location.href;
    
    if (pageUrl.includes("youtube.com/watch")) {
      // Extract clean YouTube URL without any extra parameters
      const cleanUrl = cleanYouTubeUrl(pageUrl);
      console.log("Original URL:", pageUrl);
      console.log("Clean URL:", cleanUrl);
      
      if (cleanUrl) {
        // Send message to background script
        chrome.runtime.sendMessage({
          action: "sendVideoToServer",
          videoUrl: cleanUrl
        }, (response) => {
          if (chrome.runtime.lastError) {
            console.error("Error sending message to background:", chrome.runtime.lastError);
            alert("Error: " + chrome.runtime.lastError.message);
            return;
          }
          
          console.log("Background script response:", response);
          
          if (response.success) {
            alert("Audio extraction started. You'll be notified when it's ready for download.");
          } else {
            alert("Failed to start audio extraction: " + response.error);
          }
        });
      } else {
        console.error("Could not clean YouTube URL:", pageUrl);
        alert("Could not process this YouTube URL.");
      }
    } else {
      // For other sites, try to get the video element source
      const video = document.querySelector("video");
      if (video && video.currentSrc) {
        console.log("Found video element:", video.currentSrc);
        
        chrome.runtime.sendMessage({
          action: "sendVideoToServer",
          videoUrl: video.currentSrc
        }, (response) => {
          if (chrome.runtime.lastError) {
            console.error("Error sending message to background:", chrome.runtime.lastError);
            alert("Error: " + chrome.runtime.lastError.message);
            return;
          }
          
          console.log("Background script response:", response);
          
          if (response.success) {
            alert("Audio extraction started. You'll be notified when it's ready for download.");
          } else {
            alert("Failed to start audio extraction: " + response.error);
          }
        });
      } else {
        console.error("No video element found on page");
        alert("No supported video found on this page.");
      }
    }
  } 
  else if (msg.action === "extractionCompleted") {
    console.log("Extraction completed for job:", msg.jobId);
    alert("Audio extraction completed! The download should start automatically.");
  } 
  else if (msg.action === "extractionFailed") {
    console.error("Extraction failed:", msg.error);
    alert("Audio extraction failed: " + msg.error);
  }
  
  return true; // Keep message channel open
});

// Function to clean YouTube URL
function cleanYouTubeUrl(url) {
  try {
    const urlObj = new URL(url);
    
    // Only process if it's a YouTube watch URL
    if (urlObj.hostname.includes('youtube.com') && urlObj.pathname === '/watch') {
      // Get the video ID
      const videoId = urlObj.searchParams.get('v');
      
      if (videoId) {
        // Return a clean URL with only the video ID
        return `https://www.youtube.com/watch?v=${videoId}`;
      }
    }
    
    // If it's not a watch URL or no video ID, return null
    return null;
  } catch (e) {
    console.error("Error cleaning URL:", e);
    return null;
  }
}