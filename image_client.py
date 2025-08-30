from typing import Literal
from pathlib import Path
from io import BytesIO
from PIL import Image
import requests as rq

BASE_URL:str = "https://steamcdn-a.akamaihd.net/"
IMG_TYPES = ["library_600x900_2x.jpg","library_hero.jpg","logo.png"]

game_id:int 

def save_images_from_id(game_id:int):
    # get the image via web request to steam's CDN
    for img_type in IMG_TYPES:
        request = rq.get(f"{BASE_URL}/steam/apps/{game_id}/{img_type}")
        if request.status_code != 200:
            raise Exception("Game ID was not found")
        print(f"Got image {img_type} for game id {game_id} ")

        # open image in memory
        img = Image.open(BytesIO(request.content))

        # create image path
        img_path = Path("img") / str(game_id)
        img_path.mkdir(parents=True, exist_ok=True)

        img.save(img_path / img_type)
        print(f"saved in {img_path}")