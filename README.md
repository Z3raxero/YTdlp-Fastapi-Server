####################
YTDLP SERVER
####################

 Whats Contained:
 1. Browser-Extension - This allows submission of files from a browser to the fast api server for download.
 2. Fast-API-Server - Server that process the request from the application and downloads the Youtube video as .mp3 and downloads the file on the browser.

Requirements:
Browser Extension: Can be on any browser however tested with Chrome and Opera GX. Machine OS irrelevant
Fast API Server to be hosted on a Linux ( Ubuntu ) machine.



Setup

1. Clone the REPO
2. Navigate to the Browser Extension Folder and find the config.json > You need to update this with the intended IP for the Fast API Server, The port is always 8000
3. Load the Browser extension into your browser > This can be on a different machine then the one hosting the FAST API SERVER they just need to be able to communicate. > See your browser doco on how to load custom browser extension
4. On the linux machine CD to the Base file of the repo IE ~/YTdlp-Fastapi-Server/fastapi-server.
5. Do chmod +x start_or_update.sh > This makes the file exectuable to install all the packages in requirements.txt and then execute the server
6. to Start the Server do ./start_or_update.sh
7. You can now right click a youtube video in a browser with the browser extension and click extract audio. After a minute or two the file will be downloaded in your browser.


Issues:
ffmpeg not found > Install it with sudo apt install ffmpeg -y > this is a weird bug where it isnt happy with the one in the requirements.txt because of the enviroment its installed in. 

-Z3raxero
