chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "extract-audio") {
    // For YouTube, get the page URL instead of video source
    const pageUrl = window.location.href;
    
    // Check if this is a YouTube video page
    if (pageUrl.includes("youtube.com/watch")) {
      console.log("Found YouTube video page:", pageUrl);  // Debug log
      chrome.runtime.sendMessage({
        action: "sendVideoToServer",
        videoUrl: pageUrl
      }, (response) => {
        if (response.success) {
          console.log("Server response:", response);  // Debug log
          alert("Audio extraction started. You'll be notified when it's ready for download.");
        } else {
          console.error("Error:", response.error);  // Debug log
          alert("Failed to extract audio: " + response.error);
        }
      });
    } else {
      // For other sites, try to get the video element source
      const video = document.querySelector("video");
      if (video && video.currentSrc) {
        console.log("Found video element:", video.currentSrc);  // Debug log
        chrome.runtime.sendMessage({
          action: "sendVideoToServer",
          videoUrl: video.currentSrc
        }, (response) => {
          if (response.success) {
            console.log("Server response:", response);  // Debug log
            alert("Audio extraction started. You'll be notified when it's ready for download.");
          } else {
            console.error("Error:", response.error);  // Debug log
            alert("Failed to extract audio: " + response.error);
          }
        });
      } else {
        alert("No supported video found on this page.");
      }
    }
  }
});