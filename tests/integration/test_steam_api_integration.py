"""Integration tests for Steam API endpoints."""

import pytest
import requests


@pytest.mark.integration
def test_steam_app_list_endpoint_returns_game_titles():
    """Integration test that verifies Steam's app list endpoint returns game titles."""
    response = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/", timeout=20)

    assert response.status_code == 200

    payload = response.json()
    assert "applist" in payload
    assert "apps" in payload["applist"]

    apps = payload["applist"]["apps"]
    assert isinstance(apps, list)
    assert len(apps) > 0

    sample = apps[0]
    assert "appid" in sample
    assert "name" in sample
    assert isinstance(sample["appid"], int)
    assert isinstance(sample["name"], str)

    known_titles = {"Counter-Strike 2", "Dota 2", "Team Fortress 2"}
    returned_titles = {app.get("name", "") for app in apps}
    assert any(title in returned_titles for title in known_titles)


@pytest.mark.integration
def test_steam_api_endpoint_real():
    """Integration test that verifies Steam CDN API endpoints work."""
    test_game_id = 730
    base_url = "https://steamcdn-a.akamaihd.net"

    image_types = [
        "library_600x900_2x.jpg",
        "library_hero.jpg",
        "logo.png",
        "capsule_616x353.jpg",
    ]

    for img_type in image_types:
        url = f"{base_url}/steam/apps/{test_game_id}/{img_type}"
        response = requests.get(url, timeout=10)

        assert response.status_code == 200, f"Failed to fetch {img_type} from {url}"
        assert len(response.content) > 0, f"Empty response for {img_type}"

        content_type = response.headers.get("content-type", "")
        assert any(ct in content_type.lower() for ct in ["image", "jpeg", "png"]), (
            f"Invalid content type for {img_type}: {content_type}"
        )


@pytest.mark.integration
def test_steam_api_404_handling():
    """Test that Steam API properly returns error for non-existent games."""
    fake_game_id = 99999999
    base_url = "https://steamcdn-a.akamaihd.net"

    url = f"{base_url}/steam/apps/{fake_game_id}/logo.png"
    response = requests.get(url, timeout=10)

    assert response.status_code in [404, 502], f"Expected error status, got {response.status_code}"
