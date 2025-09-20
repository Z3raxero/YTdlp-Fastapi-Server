let API_BASE_URL = "";

fetch(chrome.runtime.getURL('config.json'))
  .then(response => response.json())
  .then(config => {
    API_BASE_URL = config.API_BASE_URL;
  });

document.getElementById("checkStatus").onclick = async () => {
  const jobId = prompt("Enter Job ID:");
  if (!jobId) return;
  // Wait for API_BASE_URL to be loaded
  while (!API_BASE_URL) {
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  const resp = await fetch(`${API_BASE_URL}/api/v1/status/${jobId}`);
  const data = await resp.json();
  document.getElementById("status").innerText = JSON.stringify(data, null, 2);
};
