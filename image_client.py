from pathlib import Path
from io import BytesIO
from PIL import Image
from steamclient import STEAM_PATH
import requests 

BASE_URL:str = "https://steamcdn-a.akamaihd.net"

# each image type has a suffix that will be added to the saved file's name
IMG_TYPES = {
    "library_600x900_2x.jpg":"p.jpg",
    "library_hero.jpg":"_hero.jpg",
    "logo.png":"_logo.png",
    "capsule_616x353.jpg":".jpg"
    }

game_id:int 

def save_images_from_id(user_id:int,game_id:int,non_steam_id:int, img_path:str=None):
    # get the image via web request to steam's CDN
    for img_type in IMG_TYPES:
        request = requests.get(f"{BASE_URL}/steam/apps/{game_id}/{img_type}")
        if request.status_code == 404:
            raise Exception("Game ID was not found")
        print(f"Got image {img_type} for game id {game_id} ")

        # open image in memory
        img = Image.open(BytesIO(request.content))

        # create image path in steam folder
        if not img_path:
            img_path = Path(f"{STEAM_PATH}\\userdata\\{user_id}\\config\\grid")
        img_path.mkdir(parents=True, exist_ok=True)

        # save the image as the non-steam ID + its type suffix
        # eg: library_hero.jpg of the bending of isaac becomes 250900_hero.jpg
        img.save(img_path / (str(non_steam_id)+IMG_TYPES[img_type]))
        print(f"saved in {img_path}")