chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "extract-audio") {
    const video = document.querySelector("video");
    if (video && video.currentSrc) {
      chrome.runtime.sendMessage({
        action: "sendVideoToServer",
        videoUrl: video.currentSrc
      }, (response) => {
        if (response.success) {
          alert("Audio extraction started or completed. Check popup for status.");
        } else {
          alert("Failed to send video: " + response.error);
        }
      });
    } else {
      alert("No video found on this page.");
    }
  }
});
