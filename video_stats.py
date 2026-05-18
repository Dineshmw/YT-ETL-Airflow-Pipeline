import requests
import os
import json
from dotenv import load_dotenv
from app.logging.config import LoggerFactory

load_dotenv(dotenv_path=".env")

logger = LoggerFactory("VideoStats").get_logger()
MAX_RESULTS = 50

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
    


def get_video_ids(playlist_id):
    logger.info(f"Fetching video IDs for playlist: {playlist_id}")

    PAGE_TOKEN = None
    try:
        while True:
            url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={MAX_RESULTS}&playlistId={playlist_id}&key={YOUTUBE_API_KEY}"

            if PAGE_TOKEN:
                url += f"&pageToken={PAGE_TOKEN}"
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful
            data = response.json()
            video_ids = [item['contentDetails']['videoId'] for item in data['items']]
            PAGE_TOKEN = data.get('nextPageToken')
            
            if not PAGE_TOKEN:
                break
        return video_ids

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
        video_ids = get_video_ids(channel_playlist_id)
        logger.info(f"Video IDs for {channel_handle}: {video_ids}")
    else:
        logger.error("Failed to retrieve channel playlist ID.")