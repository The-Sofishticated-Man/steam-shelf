"""Integration tests for Steam image download and file storage behavior."""

import pytest

from core.services.image_client import SteamImageClient, save_images_from_id
from core.utils.shortcut_utils import generate_shortcut_appid


@pytest.mark.integration
def test_image_client_real_download_and_file_storage(tmp_path):
    """Integration test that downloads real images and verifies file storage."""
    steam_game_id = 730
    test_shortcut_id = 2147483647

    client = SteamImageClient(save_path=tmp_path)
    client.save_images_from_id(steam_game_id, test_shortcut_id)

    expected_files = [
        tmp_path / f"{test_shortcut_id}p.jpg",
        tmp_path / f"{test_shortcut_id}_hero.jpg",
        tmp_path / f"{test_shortcut_id}_logo.png",
        tmp_path / f"{test_shortcut_id}.jpg",
    ]

    for expected_file in expected_files:
        assert expected_file.exists(), f"Expected file not created: {expected_file}"
        assert expected_file.stat().st_size > 0, f"File is empty: {expected_file}"

        with open(expected_file, "rb") as f:
            header = f.read(10)
            if expected_file.suffix == ".jpg":
                assert header.startswith(b"\xff\xd8"), f"Invalid JPEG header: {expected_file}"
            elif expected_file.suffix == ".png":
                assert header.startswith(b"\x89PNG"), f"Invalid PNG header: {expected_file}"


@pytest.mark.integration
def test_standalone_function_real_download(tmp_path):
    """Test the standalone save_images_from_id function with real downloads."""
    steam_game_id = 730
    user_id = 123456789
    shortcut_id = generate_shortcut_appid("Counter-Strike 2", "csgo.exe")

    save_images_from_id(user_id, steam_game_id, shortcut_id, img_path=tmp_path)

    expected_files = [
        tmp_path / f"{shortcut_id}p.jpg",
        tmp_path / f"{shortcut_id}_hero.jpg",
        tmp_path / f"{shortcut_id}_logo.png",
        tmp_path / f"{shortcut_id}.jpg",
    ]

    for expected_file in expected_files:
        assert expected_file.exists(), f"Expected file not created: {expected_file}"
        assert expected_file.stat().st_size > 0, f"File is empty: {expected_file}"


@pytest.mark.integration
def test_directory_creation_and_permissions(tmp_path):
    """Test that image client creates directories and handles permissions correctly."""
    deep_path = tmp_path / "userdata" / "123456" / "config" / "grid"

    client = SteamImageClient(save_path=deep_path)

    assert not deep_path.exists()

    steam_game_id = 730
    shortcut_id = 2147483647
    client.save_images_from_id(steam_game_id, shortcut_id)

    assert deep_path.exists()
    assert deep_path.is_dir()

    expected_file = deep_path / f"{shortcut_id}p.jpg"
    assert expected_file.exists()

    assert expected_file.stat().st_size > 0
    with open(expected_file, "rb") as f:
        data = f.read()
        assert len(data) > 0


@pytest.mark.integration
def test_error_handling_with_invalid_game_id(tmp_path):
    """Test error handling when game ID doesn't exist on Steam."""
    client = SteamImageClient(save_path=tmp_path)
    fake_game_id = 99999999
    shortcut_id = 123456

    client.save_images_from_id(fake_game_id, shortcut_id)

    assert tmp_path.exists()
