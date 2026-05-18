import requests
import os
import json
from dotenv import load_dotenv
from app.logging.config import LoggerFactory
from datetime import date

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
    all_video_ids = []
    try:
        while True:
            url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={MAX_RESULTS}&playlistId={playlist_id}&key={YOUTUBE_API_KEY}"

            if PAGE_TOKEN:
                url += f"&pageToken={PAGE_TOKEN}"
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful
            data = response.json()
            video_ids = [item['contentDetails']['videoId'] for item in data['items']]
            all_video_ids.extend(video_ids)
            PAGE_TOKEN = data.get('nextPageToken')
            
            if not PAGE_TOKEN:
                break
        return all_video_ids

    except requests.RequestException as e:
        logger.error(f"HTTP error occurred: {e}")
    except KeyError as e:
        logger.error(f"Key error occurred: {e}")
        return None

def batch_list_video_ids(video_ids, batch_size=50):
    for video_id in range(0, len(video_ids), batch_size):
        yield video_ids[video_id:video_id + batch_size]


def extract_video_stats(video_ids):
    extract_video_data = []
    url = "https://www.googleapis.com/youtube/v3/videos?part=contentDetails&part=statistics&part=snippet&id={video_ids}&key={YOUTUBE_API_KEY}"

    try:
        for batch in batch_list_video_ids(video_ids, MAX_RESULTS):
            video_ids_str = ",".join(batch)  
            response = requests.get(url.format(video_ids=video_ids_str, YOUTUBE_API_KEY=YOUTUBE_API_KEY))
            response.raise_for_status()  # Check if the request was successful
            data = response.json()
            for item in data.get('items', []):
                extract_video_data.append({
                    'videoId': item['id'],
                    'title': item['snippet']['title'],
                    'publishedAt': item['snippet']['publishedAt'],
                    'duration': item['contentDetails']['duration'],
                    'viewCount': item['statistics'].get('viewCount', 0),
                    'likeCount': item['statistics'].get('likeCount', 0),
                    'commentCount': item['statistics'].get('commentCount', 0)
                })

        return extract_video_data
    
    except requests.RequestException as e:
        logger.error(f"HTTP error occurred: {e}")
    except KeyError as e:
        logger.error(f"Key error occurred: {e}")

def save_video_stats(extracted_video_stats):
    file_path = f"data/video_stats_{date.today()}.json"
    try:
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(extracted_video_stats, json_file, indent=4, ensure_ascii=False)
        logger.info(f"Video stats saved to {file_path}")
    except IOError as e:
        logger.error(f"IO error occurred: {e}")

if __name__ == "__main__":
    channel_handle = "MrBeast"

    channel_playlist_id = get_channel_playlist_id(channel_handle)
    if channel_playlist_id:
        logger.info(f"Channel Playlist ID for {channel_handle}: {channel_playlist_id}")
        video_ids = get_video_ids(channel_playlist_id)
        logger.info(f"Video IDs for {channel_handle}: {video_ids}")
        video_stats = extract_video_stats(video_ids)
        logger.info(f"Extracted video stats for {channel_handle}: {video_stats}")
        save_video_stats(video_stats)
    else:
        logger.error("Failed to retrieve channel playlist ID.")