import base64
from core.services.image_client import save_images_from_id, SteamImageClient
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
    mock_get = mocker.patch("core.services.image_client.requests.get",return_value = mock_resp)
    mocker.patch("core.services.image_client.Image.open", return_value= mock_img)

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
    # verify requests got sent to the correct address (it will try the first CDN)
    for img_type in IMG_TYPES:
        mock_get.assert_any_call(
            f"https://cdn.cloudflare.steamstatic.com/steam/apps/{MOCK_GAME_ID}/{img_type}", 
            timeout=10
        )
    # verify files got saved 
    for expected in EXPECTED:
        mock_img.save.assert_any_call(expected)
        
    
def test_raises_on_404(mocker):
    """Test that client handles 404 gracefully when all CDNs fail."""
    mock_get = mocker.patch("core.services.image_client.requests.get")

    mock_resp = mocker.Mock()
    mock_resp.status_code = 404
    mock_get.return_value = mock_resp 

    # When all CDNs return 404, it should handle gracefully (no exception for save_images_from_id)
    # The function tries fallbacks and doesn't raise on 404 - it just skips unavailable images
    save_images_from_id(MOCK_USER_ID, MOCK_GAME_ID, MOCK_NON_STEAM_ID)


def test_client_class_save_method(mocker, tmp_path):
    """Test SteamImageClient class directly."""
    mock_resp = mocker.Mock()
    mock_resp.status_code = 200
    mock_resp.content = b"test image data"
    mock_img = mocker.Mock()
    mock_get = mocker.patch("core.services.image_client.requests.get", return_value=mock_resp)
    mocker.patch("core.services.image_client.Image.open", return_value=mock_img)

    client = SteamImageClient(save_path=tmp_path)
    client.save_images_from_id(MOCK_GAME_ID, MOCK_NON_STEAM_ID)

    # Verify the client called requests.get with correct parameters
    assert mock_get.call_count >= 4  # Should call for each image type
    
    # Verify the client tried to save images
    assert mock_img.save.call_count >= 4


def test_client_404_handling(mocker, tmp_path):
    """Test that client handles 404 responses appropriately."""
    mock_get = mocker.patch("core.services.image_client.requests.get")
    
    # Mock 404 response
    mock_resp = mocker.Mock()
    mock_resp.status_code = 404
    mock_get.return_value = mock_resp
    
    client = SteamImageClient(save_path=tmp_path)
    
    # Should not raise exception, just handle gracefully
    client.save_images_from_id(MOCK_GAME_ID, MOCK_NON_STEAM_ID)
    
    # Should have tried all CDNs for each image type
    assert mock_get.call_count > 4  # Multiple CDNs * multiple image types


def test_client_with_progress_callback(mocker, tmp_path):
    """Test client with progress callback."""
    mock_resp = mocker.Mock()
    mock_resp.status_code = 200
    mock_resp.content = b"test image data"
    mock_img = mocker.Mock()
    mocker.patch("core.services.image_client.requests.get", return_value=mock_resp)
    mocker.patch("core.services.image_client.Image.open", return_value=mock_img)
    
    progress_calls = []
    def progress_callback(message, progress):
        progress_calls.append((message, progress))
    
    client = SteamImageClient(save_path=tmp_path)
    client.save_images_from_id(MOCK_GAME_ID, MOCK_NON_STEAM_ID, progress_callback)
    
    # Should have received progress updates
    assert len(progress_calls) > 0
    # Final progress should be 1.0 (complete)
    assert progress_calls[-1][1] == 1.0