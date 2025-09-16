from pathlib import Path
from io import BytesIO
from PIL import Image
import requests

# Import STEAM_PATH at module level for tests that need to patch it
try:
    from steamclient import STEAM_PATH
except ImportError:
    STEAM_PATH = None


class SteamImageClient:
    """Client for downloading and saving Steam game images."""
    

    STEAM_GAME_IMAGE_CDNS = (
        # Modern CDN endpoints
        "https://cdn.cloudflare.steamstatic.com/",
        "https://cdn.fastly.steamstatic.com/",
        "https://cdn.akamai.steamstatic.com/",

        # Store asset mirrors
        "https://shared.cloudflare.steamstatic.com/store_item_assets/",
        "https://shared.fastly.steamstatic.com/store_item_assets/",
        "https://shared.akamai.steamstatic.com/store_item_assets/",

        # Legacy domain (still works)
        "https://steamcdn-a.akamaihd.net/",
    )

    
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
        self.save_path = save_path or Path.cwd() / "images"
    
    def save_images_from_id(self, game_id: int, shortcut_id: int = None):
        """Download and save Steam game images.
        
        Args:
            game_id: Steam game ID to download images for
            shortcut_id: Non-Steam shortcut ID for file naming (defaults to game_id)
            
        Raises:
            Exception: If game ID is not found (404 response)
        """
        # Use shortcut_id for file naming, fallback to game_id if not provided
        file_id = shortcut_id if shortcut_id is not None else game_id
        
        # make sure directory exists
        self.save_path.mkdir(parents=True, exist_ok=True)
        
        # Download each image type
        for img_type in self.IMG_TYPES:
            self._download_and_save_image(game_id, img_type, file_id, self.save_path)
    
    def _download_and_save_image(self, game_id: int, img_type: str, file_id: int, save_path: Path) -> None:
        """Download a single image and save it.
        
        Args:
            game_id: Steam game ID for downloading from CDN
            img_type: Type of image to download
            file_id: ID to use for file naming (shortcut app ID)
            save_path: Directory to save the image
        """
        # Try each CDN URL as a fallback
        for base_url in self.STEAM_GAME_IMAGE_CDNS:
            try:
                url = f"{base_url}steam/apps/{game_id}/{img_type}"
                print(f"Requesting {url}")

                # try to download the image
                response = requests.get(url, timeout=10)
                print(f"Response status code: {response.status_code}")

                if response.status_code == 404:
                    print(f"Image {img_type} for game ID {game_id} not found on {base_url}, trying next CDN...")
                    continue
                elif response.status_code == 502:
                    print(f"Bad gateway for {base_url}, trying next CDN...")
                    continue
                
                response.raise_for_status()  # Raise for other HTTP errors
                
                print(f"Got image {img_type} for game id {game_id} from {base_url}")
                
                # Open image in memory
                img = Image.open(BytesIO(response.content))
                
                # Generate filename and save using file_id for naming
                filename = f"{file_id}{self.IMG_TYPES[img_type]}"
                img.save(save_path / filename)
                print(f"Saved {filename} in {save_path}")
                
                # Successfully downloaded and saved, exit
                return
                
            except Exception as e:
                print(f"Failed to download from {base_url}: {e}")
                continue
        
        # If we get here, all CDNs failed
        print(f"Image {img_type} for game {game_id} was not found on any CDN")
        
        # Special handling for library portrait - use fallback image
        if img_type == "library_600x900_2x.jpg":
            self._use_portrait_fallback(file_id, save_path)
    
    def _use_portrait_fallback(self, file_id: int, save_path: Path) -> None:
        """Use portrait.png as fallback for library_600x900_2x.jpg.
        
        Args:
            file_id: ID to use for file naming (shortcut app ID)
            save_path: Directory to save the image
        """
        try:
            # Try to download portrait.png from CDNs
            for base_url in self.STEAM_GAME_IMAGE_CDNS:
                try:
                    url = f"{base_url}steam/apps/portrait.png"
                    print(f"Requesting fallback portrait: {url}")
                    
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        # Open image in memory
                        img = Image.open(BytesIO(response.content))
                        
                        # Save with the library portrait filename
                        filename = f"{file_id}{self.IMG_TYPES['library_600x900_2x.jpg']}"
                        img.save(save_path / filename)
                        print(f"Saved fallback portrait as {filename} in {save_path}")
                        return
                        
                except Exception as e:
                    print(f"Failed to download portrait fallback from {base_url}: {e}")
                    continue
            
            print("Could not download portrait.png fallback from any CDN")
            
        except Exception as e:
            print(f"Error using portrait fallback: {e}")


def _get_default_image_path(user_id: int) -> Path:
    """Get the default Steam grid image path for a user.
    
    Args:
        user_id: Steam user ID
        
    Returns:
        Path to the user's Steam grid directory
    """
    steam_path = STEAM_PATH
    if steam_path is None:
        # Fallback if STEAM_PATH is not available
        steam_path = Path.home() / ".steam"
    return Path(steam_path) / "userdata" / str(user_id) / "config" / "grid"


def save_images_from_id(user_id: int, game_id: int, non_steam_id: int, img_path: Path = None):
    """Standalone function to download and save Steam game images.
    
    Args:
        user_id: Steam user ID for default path calculation
        game_id: Steam game ID to download images for
        non_steam_id: Non-Steam game ID for file naming
        img_path: Optional custom path to save images
        
    Raises:
        Exception: If game ID is not found (404 response)
    """
    save_path = img_path or _get_default_image_path(user_id)
    client = SteamImageClient(save_path)
    client.save_images_from_id(game_id, non_steam_id)
