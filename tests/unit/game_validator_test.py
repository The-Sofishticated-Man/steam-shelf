import pytest
from pathlib import Path
from core.services.game_validator import GameValidator


@pytest.fixture
def validator():
    """Create a GameValidator instance with test blacklists."""
    blacklisted_dirs = {"steam", "uninstall", "temp"}
    blacklisted_exes = {"uninstall", "setup", "update", "launcher"}
    return GameValidator(blacklisted_dirs, blacklisted_exes)


@pytest.fixture
def temp_game_dir(tmp_path):
    """Create a temporary game directory with executables."""
    game_dir = tmp_path / "Test Game"
    game_dir.mkdir()
    
    # Create various executable files
    (game_dir / "game.exe").write_text("main game executable")
    (game_dir / "TestGame.exe").write_text("exact name match")
    (game_dir / "Test Game.exe").write_text("exact name with spaces")
    (game_dir / "uninstall.exe").write_text("uninstaller")
    (game_dir / "setup.exe").write_text("setup program")
    (game_dir / "launcher.exe").write_text("game launcher")
    (game_dir / "data.txt").write_text("not an executable")
    
    return game_dir


class TestGameValidator:
    """Tests for GameValidator class."""
    
    def test_init(self):
        """Test GameValidator initialization."""
        blacklisted_dirs = {"test"}
        blacklisted_exes = {"setup"}
        validator = GameValidator(blacklisted_dirs, blacklisted_exes)
        
        assert validator.blacklisted_dirs == blacklisted_dirs
        assert validator.blacklisted_exes == blacklisted_exes
    
    def test_is_valid_directory_valid(self, validator, tmp_path):
        """Test valid directory detection."""
        valid_dir = tmp_path / "Valid Game"
        valid_dir.mkdir()
        
        assert validator.is_valid_directory(valid_dir) is True
    
    def test_is_valid_directory_blacklisted(self, validator, tmp_path):
        """Test blacklisted directory rejection."""
        blacklisted_dir = tmp_path / "steam"
        blacklisted_dir.mkdir()
        
        assert validator.is_valid_directory(blacklisted_dir) is False
    
    def test_is_valid_directory_case_insensitive(self, validator, tmp_path):
        """Test blacklisted directory is case insensitive."""
        blacklisted_dir = tmp_path / "STEAM"
        blacklisted_dir.mkdir()
        
        assert validator.is_valid_directory(blacklisted_dir) is False
    
    def test_is_valid_directory_not_directory(self, validator, tmp_path):
        """Test file instead of directory."""
        file_path = tmp_path / "not_a_directory.txt"
        file_path.write_text("test")
        
        assert validator.is_valid_directory(file_path) is False
    
    def test_filter_executables_all_valid(self, validator, temp_game_dir):
        """Test filtering when all executables are valid."""
        exe_files = [
            temp_game_dir / "game.exe",
            temp_game_dir / "TestGame.exe",
            temp_game_dir / "Test Game.exe"
        ]
        
        filtered = validator.filter_executables(exe_files)
        assert len(filtered) == 3
        assert all(exe in filtered for exe in exe_files)
    
    def test_filter_executables_with_blacklisted(self, validator, temp_game_dir):
        """Test filtering removes blacklisted executables."""
        exe_files = [
            temp_game_dir / "game.exe",
            temp_game_dir / "uninstall.exe",
            temp_game_dir / "setup.exe",
            temp_game_dir / "launcher.exe"
        ]
        
        filtered = validator.filter_executables(exe_files)
        assert len(filtered) == 1
        assert temp_game_dir / "game.exe" in filtered
        assert temp_game_dir / "uninstall.exe" not in filtered
    
    def test_filter_executables_case_insensitive(self, validator, tmp_path):
        """Test filtering is case insensitive."""
        exe_dir = tmp_path / "test"
        exe_dir.mkdir()
        (exe_dir / "UNINSTALL.EXE").write_text("uppercase uninstaller")
        (exe_dir / "Setup.exe").write_text("mixed case setup")
        
        exe_files = [exe_dir / "UNINSTALL.EXE", exe_dir / "Setup.exe"]
        filtered = validator.filter_executables(exe_files)
        
        assert len(filtered) == 0  # Both should be filtered out
    
    def test_find_main_executable_exact_match(self, validator, temp_game_dir):
        """Test finding main executable with exact name match."""
        valid_exes = [
            temp_game_dir / "game.exe",
            temp_game_dir / "TestGame.exe",
            temp_game_dir / "Test Game.exe"
        ]
        
        # Test exact match (case insensitive)
        main_exe = validator.find_main_executable(valid_exes, "TestGame")
        assert main_exe == temp_game_dir / "TestGame.exe"
    
    def test_find_main_executable_name_with_spaces(self, validator, temp_game_dir):
        """Test finding main executable with spaces in name."""
        valid_exes = [
            temp_game_dir / "game.exe",
            temp_game_dir / "Test Game.exe"
        ]
        
        # Test exact match with spaces
        main_exe = validator.find_main_executable(valid_exes, "Test Game")
        assert main_exe == temp_game_dir / "Test Game.exe"
    
    def test_find_main_executable_space_normalized(self, validator, temp_game_dir):
        """Test finding main executable with space normalization."""
        # Create an exe with no spaces
        (temp_game_dir / "TestGame.exe").write_text("normalized name match")
        
        valid_exes = [
            temp_game_dir / "game.exe",
            temp_game_dir / "TestGame.exe"
        ]
        
        # Search for game name with spaces, should match exe without spaces
        main_exe = validator.find_main_executable(valid_exes, "Test Game")
        assert main_exe == temp_game_dir / "TestGame.exe"
    
    def test_find_main_executable_by_size(self, validator, tmp_path):
        """Test finding main executable by file size when no name match."""
        game_dir = tmp_path / "Game"
        game_dir.mkdir()
        
        # Create files with different sizes
        small_exe = game_dir / "small.exe"
        large_exe = game_dir / "large.exe"
        
        small_exe.write_text("small")  # 5 bytes
        large_exe.write_text("this is a much larger executable file")  # 38 bytes
        
        valid_exes = [small_exe, large_exe]
        
        # No name match, should pick largest file
        main_exe = validator.find_main_executable(valid_exes, "NoMatch")
        assert main_exe == large_exe
    
    def test_find_main_executable_no_executables(self, validator):
        """Test finding main executable with empty list."""
        with pytest.raises(ValueError, match="No valid executables found"):
            validator.find_main_executable([], "Game")
    
    def test_find_main_executable_file_access_error(self, validator, tmp_path, mocker):
        """Test handling file access errors gracefully."""
        game_dir = tmp_path / "Game"
        game_dir.mkdir()
        
        exe1 = game_dir / "game1.exe"
        exe2 = game_dir / "game2.exe"
        exe1.write_text("executable 1")
        exe2.write_text("executable 2")
        
        # Mock stat to raise an error for one file
        original_stat = Path.stat
        def mock_stat(self):
            if self.name == "game1.exe":
                raise PermissionError("Access denied")
            return original_stat(self)
        
        mocker.patch.object(Path, 'stat', mock_stat)
        
        valid_exes = [exe1, exe2]
        
        # Should handle the error and pick the accessible file
        main_exe = validator.find_main_executable(valid_exes, "NoMatch")
        assert main_exe == exe2


class TestGameValidatorEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_blacklists(self, tmp_path):
        """Test validator with empty blacklists."""
        validator = GameValidator(set(), set())
        
        test_dir = tmp_path / "test"
        test_dir.mkdir()
        assert validator.is_valid_directory(test_dir) is True
        
        exe_files = [test_dir / "any.exe"]
        (test_dir / "any.exe").write_text("test")
        filtered = validator.filter_executables(exe_files)
        assert len(filtered) == 1
    
    def test_partial_name_matches(self, tmp_path):
        """Test that partial name matches don't trigger filtering."""
        blacklisted_exes = {"install"}  # Should not match "installer"
        validator = GameValidator(set(), blacklisted_exes)
        
        exe_dir = tmp_path / "test"
        exe_dir.mkdir()
        (exe_dir / "installer.exe").write_text("should not be filtered")
        
        exe_files = [exe_dir / "installer.exe"]
        filtered = validator.filter_executables(exe_files)
        
        # Should be filtered because "install" is in "installer"
        assert len(filtered) == 0
    
    def test_complex_directory_structure(self, validator, tmp_path):
        """Test validator with complex directory structure."""
        # Create nested directories
        game_dir = tmp_path / "Complex Game"
        subdir1 = game_dir / "bin"
        subdir2 = game_dir / "data"
        steam_dir = game_dir / "steam"  # This should be valid as it's not the root
        
        game_dir.mkdir()
        subdir1.mkdir()
        subdir2.mkdir()  
        steam_dir.mkdir()
        
        # All should be valid directories when checked individually
        assert validator.is_valid_directory(game_dir) is True
        assert validator.is_valid_directory(subdir1) is True
        assert validator.is_valid_directory(subdir2) is True
        assert validator.is_valid_directory(steam_dir) is False  # blacklisted name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])