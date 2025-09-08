from pathlib import Path
from io import BytesIO
from PIL import Image
import requests


class SteamImageClient:
    """Client for downloading and saving Steam game images."""
    
    BASE_URL = "https://steamcdn-a.akamaihd.net"
    
    # Image types and their corresponding file suffixes
    IMG_TYPES = {
        "library_600x900_2x.jpg": "p.jpg",
        "library_hero.jpg": "_hero.jpg", 
        "logo.png": "_logo.png",
        "capsule_616x353.jpg": ".jpg"
    }
    
    def __init__(self, save_path: Path = None):
        """Initialize the image client.
        
        Args:
            save_path: path where to save game images
        """
        self.save_path = save_path or self._get_default_image_path(user_id)
    
    def save_images_from_id(self, game_id: int):
        """Download and save Steam game images.
        
        Args:
            game_id: Steam game ID to download images for
            
        Raises:
            Exception: If game ID is not found (404 response)
        """
        # make sure directory exists
        self.save_path.mkdir(parents=True, exist_ok=True)
        
        # Download each image type
        for img_type in self.IMG_TYPES:
            self._download_and_save_image(game_id, img_type, self.save_path)
    
    def _download_and_save_image(self, game_id: int, img_type: str, 
                                non_steam_id: int, save_path: Path) -> None:
        """Download a single image and save it.
        
        Args:
            game_id: Steam game ID
            img_type: Type of image to download
            non_steam_id: Non-Steam game ID for file naming
            save_path: Directory to save the image
            
        Raises:
            Exception: If game ID is not found (404 response)
        """
        # Request image from Steam CDN
        url = f"{self.BASE_URL}/steam/apps/{game_id}/{img_type}"
        response = requests.get(url)
        
        if response.status_code == 404:
            raise Exception("Game ID was not found")
        
        response.raise_for_status()  # Raise for other HTTP errors
        
        print(f"Got image {img_type} for game id {game_id}")
        
        # Open image in memory
        img = Image.open(BytesIO(response.content))
        
        # Generate filename and save
        filename = f"{game_id}{self.IMG_TYPES[img_type]}"
        img.save(save_path / filename)
        print(f"Saved {filename} in {save_path}")
