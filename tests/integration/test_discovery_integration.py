"""Integration tests for game discovery and model conversion flows."""

from core.models.non_steam_game import NonSteamGame
from core.services.game_discovery import GameCandidate, GameDiscoveryService
from core.services.game_validator import GameValidator
from core.services.steam_db_utils import SteamDatabase
from core.utils.shortcut_utils import generate_shortcut_appid


def test_game_discovery_generates_shortcut_ids(tmp_path):
    """Test that game discovery generates shortcut app IDs for games in Steam DB."""
    game_dir = tmp_path / "Test Game"
    game_dir.mkdir()

    test_exe = game_dir / "game.exe"
    test_exe.write_text("fake exe")

    validator = GameValidator(set(), set())

    db_path = tmp_path / "test.db"
    steam_db = SteamDatabase(str(db_path))

    with steam_db._get_connection() as conn:
        conn.execute(
            "INSERT INTO games (id, name, safe_name) VALUES (?, ?, ?)",
            (123456, "Test Game", "Test Game"),
        )
        conn.commit()

    discovery_service = GameDiscoveryService(steam_db, validator)
    candidates = discovery_service.discover_games_from_directory(tmp_path)

    assert len(candidates) == 1
    candidate = candidates[0]

    assert isinstance(candidate, GameCandidate)
    assert candidate.name == "Test Game"
    assert candidate.exe_path == test_exe.resolve()
    assert candidate.start_dir == game_dir

    assert isinstance(candidate.shortcut_id, int)
    assert candidate.shortcut_id & 0x80000000 != 0

    expected_id = generate_shortcut_appid("Test Game", str(test_exe))
    assert candidate.shortcut_id == expected_id
    assert candidate.steam_id == 123456


def test_game_discovery_skips_unknown_games(tmp_path):
    """Test that game discovery skips games not in Steam database."""
    game_dir = tmp_path / "Unknown Game"
    game_dir.mkdir()

    test_exe = game_dir / "game.exe"
    test_exe.write_text("fake exe")

    validator = GameValidator(set(), set())
    steam_db = SteamDatabase(":memory:")
    discovery_service = GameDiscoveryService(steam_db, validator)

    candidates = discovery_service.discover_games_from_directory(tmp_path)
    assert len(candidates) == 0


def test_nonsteam_game_creation_from_candidate(tmp_path):
    """Test that NonSteamGame creation uses shortcut_id."""
    game_dir = tmp_path / "Mock Game"
    game_dir.mkdir()
    exe_path = game_dir / "mock.exe"
    exe_path.write_text("mock")

    shortcut_id = generate_shortcut_appid("Mock Game", str(exe_path))

    candidate = GameCandidate(
        steam_id=123456,
        shortcut_id=shortcut_id,
        name="Mock Game",
        exe_path=exe_path,
        start_dir=game_dir,
    )

    game = NonSteamGame.from_candidate(candidate)

    assert game.appid == shortcut_id
    assert game.AppName == "Mock Game"
    assert game.Exe == str(exe_path)
    assert game.StartDir == str(game_dir)
