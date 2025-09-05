import base64
from image_client import save_images_from_id
from pathlib import Path
import pytest
import pytest_mock


MOCK_GAME_ID = 391540
MOCK_USER_ID = 366276130 
MOCK_NON_STEAM_ID= 44197402

def test_successful_save(mocker: pytest_mock.MockerFixture,tmp_path: Path):

    mock_resp = mocker.Mock()
    mock_resp.status_code = 200
    mock_resp.content = b"NIKMOK NIKMOK NIKMOK NIKMOK"
    mock_img = mocker.Mock()
    mock_get = mocker.patch("image_client.requests.get",return_value = mock_resp)
    mocker.patch("image_client.Image.open", return_value= mock_img)

    save_images_from_id(MOCK_USER_ID,MOCK_GAME_ID,MOCK_NON_STEAM_ID,img_path=tmp_path)

    # all endpoints called
    IMG_TYPES = (
        "library_600x900_2x.jpg",
        "library_hero.jpg",
        "logo.png",
        "capsule_616x353.jpg"
    )
    
    # all files expected to be made
    EXPECTED =( 
        tmp_path / f"{MOCK_NON_STEAM_ID}p.jpg",
        tmp_path / f"{MOCK_NON_STEAM_ID}_hero.jpg",
        tmp_path / f"{MOCK_NON_STEAM_ID}_logo.png",
        tmp_path / f"{MOCK_NON_STEAM_ID}.jpg",
    )
    # verify requests got sent to the correct address
    for img_type in IMG_TYPES:
        mock_get.assert_any_call(
            f"https://steamcdn-a.akamaihd.net/steam/apps/{MOCK_GAME_ID}/{img_type}"
        )
    # verify files got saved 
    for expected in EXPECTED:
        mock_img.save.assert_any_call(expected)
        
    
def test_raises_on_404(mocker):
    mock_get = mocker.patch("image_client.requests.get")

    mock_resp = mocker.Mock()
    mock_resp.status_code = 404
    mock_get.return_value = mock_resp 

    # check it raises an exception
    with pytest.raises(Exception,match="Game ID was not found"):
        save_images_from_id(MOCK_USER_ID,MOCK_GAME_ID,MOCK_NON_STEAM_ID)


def test_uses_default_path(mocker, tmp_path):
    # Patch STEAM_PATH constant
    mocker.patch("image_client.STEAM_PATH", str(tmp_path))

    # Fake request + image
    fake_resp = mocker.Mock(status_code=200, content=b"AHHHHHHHHHHHHHHHH")
    mocker.patch("image_client.requests.get", return_value=fake_resp)

    fake_img = mocker.Mock()
    mocker.patch("image_client.Image.open", return_value=fake_img)

    # Run without img_path (forces default)
    save_images_from_id(123, 456, 789)

    # Verify directory exists
    expected_path = tmp_path / "userdata" / "123" / "config" / "grid"
    assert expected_path.exists()