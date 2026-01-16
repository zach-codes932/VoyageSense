import requests
import logging
from src.config import YOUTUBE_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeVlogManager:
    def __init__(self):
        self.api_key = YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3/search"

    def search_vlogs(self, destination_name, max_results=3):
        """
        Searches for travel vlogs for a specific destination.
        
        Args:
            destination_name (str): Name of the place (e.g., "Munnar Tea Gardens")
            max_results (int): Number of videos to return.
            
        Returns:
            list: List of dicts [{'title': ..., 'video_id': ...}, ...]
        """
        query = f"{destination_name} travel vlog India"
        
        params = {
            'part': 'snippet',
            'q': query,
            'maxResults': max_results,
            'type': 'video',
            'key': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                videos = []
                for item in data.get('items', []):
                    video_data = {
                        'title': item['snippet']['title'],
                        'video_id': item['id']['videoId'],
                        'thumbnail': item['snippet']['thumbnails']['high']['url']
                    }
                    videos.append(video_data)
                return videos
            elif response.status_code == 403:
                logger.error(f"YouTube 403 Error: {response.text}")
                return self._get_mock_data(destination_name)
            else:
                logger.error(f"YouTube API Error {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Exception searching YouTube: {e}")
            return self._get_mock_data(destination_name)

        return self._get_mock_data(destination_name)

    def _get_mock_data(self, destination):
        logger.warning(f"Using MOCK YouTube data for {destination}")
        return [
            {
                'title': f"Experience {destination} | Travel Vlog",
                'video_id': "i9E_Blai8vk", # Generic Travel Video (Kerala/Munnar vibes)
                'thumbnail': "https://img.youtube.com/vi/i9E_Blai8vk/hqdefault.jpg"
            },
            {
                'title': f"Top things to do in {destination}",
                'video_id': "ysz5S6PUM-U", # Another generic travel placeholder
                'thumbnail': "https://img.youtube.com/vi/ysz5S6PUM-U/hqdefault.jpg"
            }
        ]

if __name__ == "__main__":
    # Test Run
    yt = YouTubeVlogManager()
    place = "Munnar Tea Gardens"
    print(f"Searching for vlogs about: {place}...")
    
    vlogs = yt.search_vlogs(place)
    
    if vlogs:
        print("\n--- Found Vlogs ---")
        for v in vlogs:
            print(f"Title: {v['title']}")
            print(f"Link: https://www.youtube.com/watch?v={v['video_id']}\n")
    else:
        print("No vlogs found. Check API Key or Quota.")
