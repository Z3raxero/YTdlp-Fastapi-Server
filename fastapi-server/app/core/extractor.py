from yt_dlp import YoutubeDL
import os
import tempfile

class AudioExtractor:
    def __init__(self):
        self.yt_dlp_options = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(tempfile.gettempdir(), '%(title)s.%(ext)s'),
        }

    def extract_audio(self, video_url):
        with YoutubeDL(self.yt_dlp_options) as ydl:
            info = ydl.extract_info(video_url, download=True)
            audio_file_path = ydl.prepare_filename(info)
            return audio_file_path

    def clean_up(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)