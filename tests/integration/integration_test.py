"""Integration test to verify the new shortcut app ID generation."""
import pytest
import requests
from core.services.game_discovery import GameDiscoveryService, GameCandidate
from core.services.game_validator import GameValidator
from core.services.steam_db_utils import SteamDatabase
from core.models.non_steam_game import NonSteamGame
from core.utils.shortcut_utils import generate_shortcut_appid
from core.services.image_client import SteamImageClient, save_images_from_id


def test_game_discovery_generates_shortcut_ids(tmp_path):
    """Test that game discovery generates shortcut app IDs for games in Steam DB."""
    
    # Create a test game directory structure
    game_dir = tmp_path / "Test Game"
    game_dir.mkdir()
    
    # Create a test executable
    test_exe = game_dir / "game.exe"
    test_exe.write_text("fake exe")
    
    # Set up the discovery service with a database that has our test game
    validator = GameValidator(set(), set())
    
    # Use a temporary file database for testing instead of memory
    db_path = tmp_path / "test.db"
    steam_db = SteamDatabase(str(db_path))
    
    # Add the test game to the database using the proper context manager
    with steam_db._get_connection() as conn:
        conn.execute(
            "INSERT INTO games (id, name, safe_name) VALUES (?, ?, ?)",
            (123456, "Test Game", "Test Game")
        )
        conn.commit()
    
    discovery_service = GameDiscoveryService(steam_db, validator)
    
    # Discover games
    candidates = discovery_service.discover_games_from_directory(tmp_path)
    
    # Should find one candidate
    assert len(candidates) == 1
    candidate = candidates[0]
    
    # Verify the candidate has the expected structure
    assert isinstance(candidate, GameCandidate)
    assert candidate.name == "Test Game"
    assert candidate.exe_path == test_exe.resolve()
    assert candidate.start_dir == game_dir
    
    # Verify shortcut_id is generated
    assert isinstance(candidate.shortcut_id, int)
    assert candidate.shortcut_id & 0x80000000 != 0  # Should have high bit set
    
    # Verify it matches what we'd expect from the utility function
    expected_id = generate_shortcut_appid("Test Game", str(test_exe))
    assert candidate.shortcut_id == expected_id
    
    # Steam ID should be set since it was in the database
    assert candidate.steam_id == 123456


def test_game_discovery_skips_unknown_games(tmp_path):
    """Test that game discovery skips games not in Steam database."""
    
    # Create a test game directory structure
    game_dir = tmp_path / "Unknown Game"
    game_dir.mkdir()
    
    # Create a test executable
    test_exe = game_dir / "game.exe"
    test_exe.write_text("fake exe")
    
    # Set up the discovery service with empty database
    validator = GameValidator(set(), set())
    steam_db = SteamDatabase(":memory:")  # Use in-memory database for testing
    discovery_service = GameDiscoveryService(steam_db, validator)
    
    # Discover games
    candidates = discovery_service.discover_games_from_directory(tmp_path)
    
    # Should find no candidates since game is not in database
    assert len(candidates) == 0


def test_nonsteam_game_creation_from_candidate(tmp_path):
    """Test that NonSteamGame creation uses shortcut_id."""
    
    # Create a mock candidate
    game_dir = tmp_path / "Mock Game"
    game_dir.mkdir()
    exe_path = game_dir / "mock.exe"
    exe_path.write_text("mock")
    
    shortcut_id = generate_shortcut_appid("Mock Game", str(exe_path))
    
    candidate = GameCandidate(
        steam_id=123456,  # Now has a Steam ID since discovery requires it
        shortcut_id=shortcut_id,
        name="Mock Game",
        exe_path=exe_path,
        start_dir=game_dir
    )
    
    # Create NonSteamGame from candidate
    game = NonSteamGame.from_candidate(candidate)
    
    # Verify it uses the shortcut_id
    assert game.appid == shortcut_id
    assert game.AppName == "Mock Game"
    assert game.Exe == str(exe_path)
    assert game.StartDir == str(game_dir)


@pytest.mark.integration
def test_steam_api_endpoint_real():
    """Integration test that verifies Steam CDN API endpoints work."""
    # Use a known Steam game ID that should always exist: Counter-Strike 2 (730)
    test_game_id = 730
    base_url = "https://steamcdn-a.akamaihd.net"
    
    # Test each image type endpoint
    image_types = [
        "library_600x900_2x.jpg",
        "library_hero.jpg", 
        "logo.png",
        "capsule_616x353.jpg"
    ]
    
    for img_type in image_types:
        url = f"{base_url}/steam/apps/{test_game_id}/{img_type}"
        response = requests.get(url, timeout=10)
        
        # Should get a successful response
        assert response.status_code == 200, f"Failed to fetch {img_type} from {url}"
        
        # Should have content
        assert len(response.content) > 0, f"Empty response for {img_type}"
        
        # Should be image content (basic check)
        content_type = response.headers.get('content-type', '')
        assert any(ct in content_type.lower() for ct in ['image', 'jpeg', 'png']), \
            f"Invalid content type for {img_type}: {content_type}"


@pytest.mark.integration  
def test_steam_api_404_handling():
    """Test that Steam API properly returns error for non-existent games."""
    # Use a game ID that should not exist (very high number)
    fake_game_id = 99999999
    base_url = "https://steamcdn-a.akamaihd.net"
    
    url = f"{base_url}/steam/apps/{fake_game_id}/logo.png"
    response = requests.get(url, timeout=10)
    
    # Should get an error status (404 or 502) for non-existent game
    assert response.status_code in [404, 502], f"Expected error status, got {response.status_code}"


@pytest.mark.integration
def test_image_client_real_download_and_file_storage(tmp_path):
    """Integration test that downloads real images and verifies file storage."""
    # Use Counter-Strike 2 (730) - a game that should always have images
    steam_game_id = 730
    test_shortcut_id = 2147483647  # Example shortcut ID
    
    # Create image client with test directory
    client = SteamImageClient(save_path=tmp_path)
    
    # Download images
    client.save_images_from_id(steam_game_id, test_shortcut_id)
    
    # Verify all expected files were created with correct naming
    expected_files = [
        tmp_path / f"{test_shortcut_id}p.jpg",        # library_600x900_2x.jpg
        tmp_path / f"{test_shortcut_id}_hero.jpg",    # library_hero.jpg
        tmp_path / f"{test_shortcut_id}_logo.png",    # logo.png
        tmp_path / f"{test_shortcut_id}.jpg",         # capsule_616x353.jpg
    ]
    
    for expected_file in expected_files:
        assert expected_file.exists(), f"Expected file not created: {expected_file}"
        assert expected_file.stat().st_size > 0, f"File is empty: {expected_file}"
        
        # Verify it's a valid image file by checking headers
        with open(expected_file, 'rb') as f:
            header = f.read(10)
            if expected_file.suffix == '.jpg':
                assert header.startswith(b'\xff\xd8'), f"Invalid JPEG header: {expected_file}"
            elif expected_file.suffix == '.png':
                assert header.startswith(b'\x89PNG'), f"Invalid PNG header: {expected_file}"


@pytest.mark.integration
def test_standalone_function_real_download(tmp_path):
    """Test the standalone save_images_from_id function with real downloads."""
    steam_game_id = 730  # Counter-Strike 2
    user_id = 123456789  # Mock user ID
    shortcut_id = generate_shortcut_appid("Counter-Strike 2", "csgo.exe")
    
    # Use the standalone function
    save_images_from_id(user_id, steam_game_id, shortcut_id, img_path=tmp_path)
    
    # Verify files were created with shortcut_id naming
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
    # Create nested directory structure
    deep_path = tmp_path / "userdata" / "123456" / "config" / "grid"
    
    client = SteamImageClient(save_path=deep_path)
    
    # Directory shouldn't exist yet
    assert not deep_path.exists()
    
    # Download images - should create directory structure
    steam_game_id = 730
    shortcut_id = 2147483647
    client.save_images_from_id(steam_game_id, shortcut_id)
    
    # Directory should now exist
    assert deep_path.exists()
    assert deep_path.is_dir()
    
    # Files should be in the correct location
    expected_file = deep_path / f"{shortcut_id}p.jpg"
    assert expected_file.exists()
    
    # Should be able to read/write (check permissions)
    assert expected_file.stat().st_size > 0
    with open(expected_file, 'rb') as f:
        data = f.read()
        assert len(data) > 0


@pytest.mark.integration
def test_error_handling_with_invalid_game_id(tmp_path):
    """Test error handling when game ID doesn't exist on Steam."""
    client = SteamImageClient(save_path=tmp_path)
    fake_game_id = 99999999
    shortcut_id = 123456
    
    # The client handles 404s gracefully and doesn't raise exceptions
    # It tries multiple CDNs and fallback images
    client.save_images_from_id(fake_game_id, shortcut_id)
    
    # Directory should exist even if no images were downloaded
    assert tmp_path.exists()


@pytest.mark.integration
def test_end_to_end_workflow_with_real_data(tmp_path):
    """End-to-end test with real Steam database and image downloading."""
    # Set up a real Steam database using temporary file
    db_path = tmp_path / "test.db"
    steam_db = SteamDatabase(str(db_path))
    
    # Add some known Steam games
    test_games = [
        (730, "Counter-Strike 2"),
        (440, "Team Fortress 2"), 
        (570, "Dota 2")
    ]
    
    with steam_db._get_connection() as conn:
        for game_id, game_name in test_games:
            conn.execute(
                "INSERT INTO games (id, name, safe_name) VALUES (?, ?, ?)",
                (game_id, game_name, game_name)
            )
        conn.commit()
    
    # Create game directories
    for _, game_name in test_games:
        game_dir = tmp_path / game_name
        game_dir.mkdir()
        (game_dir / "game.exe").write_text("fake exe")
    
    # Set up discovery
    validator = GameValidator(set(), set())
    discovery_service = GameDiscoveryService(steam_db, validator)
    
    # Discover games
    candidates = discovery_service.discover_games_from_directory(tmp_path)
    
    # Should find all test games
    assert len(candidates) == len(test_games)
    
    # Verify each candidate
    for candidate in candidates:
        assert candidate.steam_id in [gid for gid, _ in test_games]
        assert candidate.name in [name for _, name in test_games]
        assert isinstance(candidate.shortcut_id, int)
        assert candidate.shortcut_id & 0x80000000 != 0  # High bit set
    
    # Test image downloading for one game (to avoid too many API calls)
    test_candidate = candidates[0]
    images_dir = tmp_path / "images"
    client = SteamImageClient(save_path=images_dir)
    
    # Download images
    client.save_images_from_id(test_candidate.steam_id, test_candidate.shortcut_id)
    
    # Verify files created with shortcut ID naming
    expected_files = [
        images_dir / f"{test_candidate.shortcut_id}p.jpg",
        images_dir / f"{test_candidate.shortcut_id}_hero.jpg",
        images_dir / f"{test_candidate.shortcut_id}_logo.png", 
        images_dir / f"{test_candidate.shortcut_id}.jpg",
    ]
    
    for expected_file in expected_files:
        assert expected_file.exists(), f"Missing file: {expected_file}"
        assert expected_file.stat().st_size > 0
    
    steam_db.close()
