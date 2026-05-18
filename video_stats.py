import requests
import os
import json
from dotenv import load_dotenv
from app.logging.config import LoggerFactory

load_dotenv(dotenv_path=".env")

logger = LoggerFactory("VideoStats").get_logger()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_channel_playlist_id(channel_handle):
    logger.info(f"Fetching playlist ID for channel: {channel_handle}")
    
    try:

        url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={channel_handle}&key={YOUTUBE_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        data = response.json()
        channel_item = data['items'][0]
        return channel_item['contentDetails']['relatedPlaylists']['uploads']

    except requests.RequestException as e:
        logger.error(f"HTTP error occurred: {e}")
    except KeyError as e:
        logger.error(f"Key error occurred: {e}")
        return None

if __name__ == "__main__":
    channel_handle = "MrBeast"

    channel_playlist_id = get_channel_playlist_id(channel_handle)
    if channel_playlist_id:
        logger.info(f"Channel Playlist ID for {channel_handle}: {channel_playlist_id}")
        print(channel_playlist_id)
    else:
        logger.error("Failed to retrieve channel playlist ID.")