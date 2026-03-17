"""End-to-end integration tests for discovery and image download workflow."""

import pytest

from core.services.game_discovery import GameDiscoveryService
from core.services.game_validator import GameValidator
from core.services.image_client import SteamImageClient
from core.services.steam_db_utils import SteamDatabase


@pytest.mark.integration
def test_end_to_end_workflow_with_real_data(tmp_path):
    """End-to-end test with real Steam database and image downloading."""
    db_path = tmp_path / "test.db"
    steam_db = SteamDatabase(str(db_path))

    test_games = [
        (730, "Counter-Strike 2"),
        (440, "Team Fortress 2"),
        (570, "Dota 2"),
    ]

    with steam_db._get_connection() as conn:
        for game_id, game_name in test_games:
            conn.execute(
                "INSERT INTO games (id, name, safe_name) VALUES (?, ?, ?)",
                (game_id, game_name, game_name),
            )
        conn.commit()

    for _, game_name in test_games:
        game_dir = tmp_path / game_name
        game_dir.mkdir()
        (game_dir / "game.exe").write_text("fake exe")

    validator = GameValidator(set(), set())
    discovery_service = GameDiscoveryService(steam_db, validator)

    candidates = discovery_service.discover_games_from_directory(tmp_path)

    assert len(candidates) == len(test_games)

    for candidate in candidates:
        assert candidate.steam_id in [gid for gid, _ in test_games]
        assert candidate.name in [name for _, name in test_games]
        assert isinstance(candidate.shortcut_id, int)
        assert candidate.shortcut_id & 0x80000000 != 0

    test_candidate = candidates[0]
    images_dir = tmp_path / "images"
    client = SteamImageClient(save_path=images_dir)

    client.save_images_from_id(test_candidate.steam_id, test_candidate.shortcut_id)

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
