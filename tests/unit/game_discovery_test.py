import pytest
from pathlib import Path
from core.services.game_discovery import GameDiscoveryService, GameCandidate
from core.services.game_validator import GameValidator
from core.services.steam_db_utils import SteamDatabase


@pytest.fixture
def steam_db(tmp_path):
    """Create a test Steam database."""
    db_path = tmp_path / "test.db"
    db = SteamDatabase(str(db_path))
    
    # Add some test games
    test_games = [
        (123, "Test Game", "Test Game"),
        (456, "Another Game", "Another Game"),
        (789, "Space Game", "Space Game"),
        (999, "Racing Game", "Racing Game")
    ]
    
    with db._get_connection() as conn:
        for game_id, name, safe_name in test_games:
            conn.execute(
                "INSERT INTO games (id, name, safe_name) VALUES (?, ?, ?)",
                (game_id, name, safe_name)
            )
        conn.commit()
    
    return db


@pytest.fixture
def validator():
    """Create a test validator."""
    return GameValidator(
        blacklisted_dirs={"steam", "uninstall"},
        blacklisted_exes={"uninstall", "setup"}
    )


@pytest.fixture
def discovery_service(steam_db, validator):
    """Create a GameDiscoveryService instance."""
    return GameDiscoveryService(steam_db, validator)


@pytest.fixture
def test_game_structure(tmp_path):
    """Create a test directory structure with multiple games."""
    
    # Test Game (valid, in database)
    test_game_dir = tmp_path / "Test Game"
    test_game_dir.mkdir()
    (test_game_dir / "TestGame.exe").write_text("main executable")
    (test_game_dir / "data.txt").write_text("game data")
    
    # Another Game (valid, in database)
    another_game_dir = tmp_path / "Another Game"
    another_game_dir.mkdir()
    (another_game_dir / "game.exe").write_text("another game exe")
    (another_game_dir / "AnotherGame.exe").write_text("exact name match")
    
    # Unknown Game (valid directory, but not in database)
    unknown_game_dir = tmp_path / "Unknown Game"
    unknown_game_dir.mkdir()
    (unknown_game_dir / "unknown.exe").write_text("unknown game")
    
    # Steam directory (blacklisted)
    steam_dir = tmp_path / "steam"
    steam_dir.mkdir()
    (steam_dir / "steam.exe").write_text("steam client")
    
    # Game with no executables
    no_exe_dir = tmp_path / "Space Game"
    no_exe_dir.mkdir()
    (no_exe_dir / "readme.txt").write_text("no executables here")
    
    # Game with only blacklisted executables
    bad_exe_dir = tmp_path / "Racing Game"
    bad_exe_dir.mkdir()
    (bad_exe_dir / "uninstall.exe").write_text("uninstaller")
    (bad_exe_dir / "setup.exe").write_text("setup program")
    
    return tmp_path


class TestGameDiscoveryService:
    """Tests for GameDiscoveryService class."""
    
    def test_init(self, steam_db, validator):
        """Test GameDiscoveryService initialization."""
        service = GameDiscoveryService(steam_db, validator)
        
        assert service.steam_db == steam_db
        assert service.validator == validator
        assert service.games_already_added == set()
    
    def test_init_with_added_games(self, steam_db, validator):
        """Test GameDiscoveryService initialization with pre-added games."""
        added_games = {"Game 1", "Game 2"}
        service = GameDiscoveryService(steam_db, validator, added_games)
        
        assert service.games_already_added == added_games
    
    def test_discover_games_success(self, discovery_service, test_game_structure):
        """Test successful game discovery."""
        candidates = discovery_service.discover_games_from_directory(test_game_structure)
        
        # Should find Test Game and Another Game
        assert len(candidates) == 2
        
        # Verify the candidates
        candidate_names = [c.name for c in candidates]
        assert "Test Game" in candidate_names
        assert "Another Game" in candidate_names
        
        # Check Test Game candidate
        test_game_candidate = next(c for c in candidates if c.name == "Test Game")
        assert test_game_candidate.steam_id == 123
        assert isinstance(test_game_candidate.shortcut_id, int)
        assert test_game_candidate.exe_path.name == "TestGame.exe"
        assert test_game_candidate.start_dir == test_game_candidate.exe_path.parent
    
    def test_discover_games_with_progress_callback(self, discovery_service, test_game_structure):
        """Test game discovery with progress callback."""
        progress_calls = []
        
        def progress_callback(message, progress):
            progress_calls.append((message, progress))
        
        candidates = discovery_service.discover_games_from_directory(
            test_game_structure, 
            progress_callback=progress_callback
        )
        
        # Should have received progress updates
        assert len(progress_calls) > 0
        # Final progress should be completion
        assert progress_calls[-1] == ("Game discovery complete", 1.0)
        
        # Should still find games
        assert len(candidates) == 2
    
    def test_discover_games_skips_unknown(self, discovery_service, test_game_structure):
        """Test that discovery skips games not in Steam database."""
        candidates = discovery_service.discover_games_from_directory(test_game_structure)
        
        # Should not find "Unknown Game" as it's not in the database
        candidate_names = [c.name for c in candidates]
        assert "Unknown Game" not in candidate_names
    
    def test_discover_games_skips_blacklisted_dirs(self, discovery_service, test_game_structure):
        """Test that discovery skips blacklisted directories."""
        candidates = discovery_service.discover_games_from_directory(test_game_structure)
        
        # Should not find "steam" directory as it's blacklisted
        candidate_names = [c.name for c in candidates]
        assert "steam" not in candidate_names
    
    def test_discover_games_skips_no_executables(self, discovery_service, test_game_structure):
        """Test that discovery skips games with no valid executables."""
        candidates = discovery_service.discover_games_from_directory(test_game_structure)
        
        # Should not find "Space Game" as it has no executables
        candidate_names = [c.name for c in candidates]
        assert "Space Game" not in candidate_names
    
    def test_discover_games_skips_already_added(self, steam_db, validator, test_game_structure):
        """Test that discovery skips already added games."""
        added_games = {"Test Game"}
        service = GameDiscoveryService(steam_db, validator, added_games)
        
        candidates = service.discover_games_from_directory(test_game_structure)
        
        # Should only find "Another Game", not "Test Game"
        assert len(candidates) == 1
        assert candidates[0].name == "Another Game"
    
    def test_discover_games_empty_directory(self, discovery_service, tmp_path):
        """Test discovery with empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        candidates = discovery_service.discover_games_from_directory(empty_dir)
        assert len(candidates) == 0
    
    def test_discover_games_permission_error(self, discovery_service, test_game_structure, mocker):
        """Test handling of permission errors during discovery."""
        # Mock directory iteration to raise permission error for one directory
        original_iterdir = Path.iterdir
        
        def mock_iterdir(self):
            if self.name.endswith("Another Game"):
                raise PermissionError("Access denied")
            return original_iterdir(self)
        
        mocker.patch.object(Path, 'iterdir', mock_iterdir)
        
        # Should handle error gracefully and continue with other directories
        candidates = discovery_service.discover_games_from_directory(test_game_structure)
        
        # Should still find Test Game despite permission error on Another Game
        assert len(candidates) >= 1
        candidate_names = [c.name for c in candidates]
        assert "Test Game" in candidate_names


class TestGameCandidate:
    """Tests for GameCandidate NamedTuple."""
    
    def test_game_candidate_creation(self, tmp_path):
        """Test GameCandidate creation."""
        exe_path = tmp_path / "game.exe"
        exe_path.write_text("test")
        start_dir = tmp_path
        
        candidate = GameCandidate(
            steam_id=123,
            shortcut_id=456,
            name="Test Game",
            exe_path=exe_path,
            start_dir=start_dir
        )
        
        assert candidate.steam_id == 123
        assert candidate.shortcut_id == 456
        assert candidate.name == "Test Game"
        assert candidate.exe_path == exe_path
        assert candidate.start_dir == start_dir
        assert candidate.confirmed is False  # Default value
    
    def test_game_candidate_with_confirmed(self, tmp_path):
        """Test GameCandidate with confirmed flag."""
        exe_path = tmp_path / "game.exe"
        start_dir = tmp_path
        
        candidate = GameCandidate(
            steam_id=123,
            shortcut_id=456,
            name="Test Game",
            exe_path=exe_path,
            start_dir=start_dir,
            confirmed=True
        )
        
        assert candidate.confirmed is True


class TestPrivateMethods:
    """Tests for private methods in GameDiscoveryService."""
    
    def test_process_directory_success(self, discovery_service, tmp_path):
        """Test successful directory processing."""
        # Create a valid game directory
        game_dir = tmp_path / "Test Game"
        game_dir.mkdir()
        (game_dir / "TestGame.exe").write_text("main executable")
        
        candidate = discovery_service._process_directory(game_dir)
        
        assert candidate is not None
        assert candidate.name == "Test Game"
        assert candidate.steam_id == 123  # From fixture
        assert isinstance(candidate.shortcut_id, int)
        assert candidate.exe_path.name == "TestGame.exe"
    
    def test_process_directory_already_added(self, steam_db, validator, tmp_path):
        """Test processing directory that's already added."""
        added_games = {"Test Game"}
        service = GameDiscoveryService(steam_db, validator, added_games)
        
        game_dir = tmp_path / "Test Game"
        game_dir.mkdir()
        (game_dir / "TestGame.exe").write_text("main executable")
        
        candidate = service._process_directory(game_dir)
        assert candidate is None
    
    def test_process_directory_invalid_directory(self, discovery_service, tmp_path):
        """Test processing invalid directory."""
        # Create a blacklisted directory
        steam_dir = tmp_path / "steam"
        steam_dir.mkdir()
        (steam_dir / "steam.exe").write_text("steam client")
        
        candidate = discovery_service._process_directory(steam_dir)
        assert candidate is None
    
    def test_process_directory_not_in_database(self, discovery_service, tmp_path):
        """Test processing directory for game not in database."""
        unknown_dir = tmp_path / "Unknown Game"
        unknown_dir.mkdir()
        (unknown_dir / "unknown.exe").write_text("unknown game")
        
        candidate = discovery_service._process_directory(unknown_dir)
        assert candidate is None
    
    def test_process_directory_no_valid_executables(self, discovery_service, tmp_path):
        """Test processing directory with no valid executables."""
        game_dir = tmp_path / "Test Game"  # In database
        game_dir.mkdir()
        (game_dir / "uninstall.exe").write_text("blacklisted exe")
        (game_dir / "readme.txt").write_text("not an executable")
        
        candidate = discovery_service._process_directory(game_dir)
        assert candidate is None


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_shortcut_id_consistency(self, discovery_service, tmp_path):
        """Test that shortcut IDs are consistent for same game."""
        game_dir = tmp_path / "Test Game"
        game_dir.mkdir()
        (game_dir / "TestGame.exe").write_text("main executable")
        
        # Process the same directory multiple times
        candidate1 = discovery_service._process_directory(game_dir)
        candidate2 = discovery_service._process_directory(game_dir)
        
        assert candidate1.shortcut_id == candidate2.shortcut_id
    
    def test_different_exe_paths_same_game(self, discovery_service, tmp_path):
        """Test games with different executable structures."""
        # Game with exe in subdirectory
        game_dir = tmp_path / "Test Game"
        bin_dir = game_dir / "bin"
        game_dir.mkdir()
        bin_dir.mkdir()
        (bin_dir / "TestGame.exe").write_text("main executable")
        
        candidate = discovery_service._process_directory(game_dir)
        
        assert candidate is not None
        assert candidate.exe_path == bin_dir / "TestGame.exe"
        assert candidate.start_dir == bin_dir  # Should be exe's parent


if __name__ == "__main__":
    pytest.main([__file__, "-v"])