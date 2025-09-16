from pathlib import Path

from steamclient import STEAM_PATH
from core.services.image_client import SteamImageClient
from core.utils.vdf_utils import write_binary_vdf, parse_vdf
from core.models.non_steam_game import NonSteamGame
from core.services.game_discovery import GameDiscoveryService
from core.services.game_validator import GameValidator
from core.utils.vdf_serializer import VDFSerializer
from core.services.steam_db_utils import SteamDatabase

BLACKLISTED_DIRECTORIES = {"steam"}
BLACKLISTED_EXECUTABLES = {"uninstall", "setup", "update"}

class NonSteamGameRepository:
    """Repository for managing non-Steam games.
        
    Args:
        user_id (int): Steam user ID for saving images
        steam_path (Path): Steam installation path
        discovery_service (GameDiscoveryService, optional): Game discovery service
        serializer (VDFSerializer, optional): VDF serialization service
        validator (GameValidator, optional): Game validation service
        steam_image_client (SteamImageClient, optional): Image downloading service
    """
    def __init__(self, 
                 user_id: int,
                 steam_path : Path = Path(STEAM_PATH),
                 discovery_service: GameDiscoveryService = None,
                 serializer: VDFSerializer = None,
                 validator: GameValidator = None,
                 steam_image_client:SteamImageClient = None):
        self.user_id = user_id
        self.games: list[NonSteamGame] = []
        self.game_candidates: list = []  # Store original candidates for image downloading
        
        # Use dependency injection or create default services
        self.validator = validator or GameValidator(
            BLACKLISTED_DIRECTORIES, 
            BLACKLISTED_EXECUTABLES
        )
        self.serializer = serializer or VDFSerializer()
        self.steam_path = steam_path
        self.shortcuts_vdf_path = steam_path /"userdata"/str(user_id)/"config"/"shortcuts.vdf"
        self.image_client = steam_image_client or SteamImageClient(
            save_path= steam_path/"userdata"/str(user_id)/"config"/"grid"
        )
        if self.shortcuts_vdf_path.exists():
            self.load_games_from_vdf(self.shortcuts_vdf_path)
        else:
            print("No shortcuts.vdf file found, defaulting to empty repo")
        games_already_added = {game.AppName for game in self.games}
        self.discovery_service = discovery_service or GameDiscoveryService(
            SteamDatabase(), 
            self.validator,
            added_games=games_already_added
        )
        
    
    def add_game(self, game: NonSteamGame):
        """Add a game to the repository.
        
        Args:
            game (NonSteamGame): Game to add
        """
        self.games.append(game)
    
    def load_games_from_directory(self, path: Path):
        """Load games by discovering them from a directory structure.
        
        Args:
            path (Path): Directory to scan for games
            
        Raises:
            FileNotFoundError: If directory doesn't exist
        """
        candidates = self.discovery_service.discover_games_from_directory(path)
        self.game_candidates.extend(candidates)  # Store candidates for image downloading
        for candidate in candidates:
            game = NonSteamGame.from_candidate(candidate)
            self.add_game(game)
                
        
    def load_games_from_vdf(self, path: Path):
        """Load games from an existing VDF file.
        
        Args:
            path (Path): Path to VDF file
            
        Raises:
            FileNotFoundError: If VDF file doesn't exist
        """
        vdf_data = parse_vdf(path)
        games = self.serializer.games_from_vdf_dict(vdf_data)
        for game in games:
            self.add_game(game)
            
    def save_games_as_vdf(self, path: Path = None):
        """Save games to a VDF file.
        
        Args:
            path (Path, optional): Output VDF file path
        """
        save_path = path if path else self.shortcuts_vdf_path
        if save_path.exists():
            # delete current shortcuts.vdf file
            save_path.unlink()

        vdf_data = self.serializer.games_to_vdf_dict(self.games)
        write_binary_vdf(vdf_data, save_path)

    def save_game_images(self):
        """Download and save Steam artwork for all games.
        
        Raises:
            Exception: If game ID not found on Steam
        """
        # Use candidates to get Steam IDs for image downloading
        for candidate in self.game_candidates:
            # All candidates should have Steam IDs since discovery requires them
            print(f"Downloading images for {candidate.name} (Steam ID: {candidate.steam_id}, Shortcut ID: {candidate.shortcut_id})")
            self.image_client.save_images_from_id(candidate.steam_id, candidate.shortcut_id)
            
    def __iter__(self):
        """Iterate over games in the repository."""
        for game in self.games:
            yield game
if __name__ == "__main__":
    stuff = NonSteamGameRepository()
    stuff.load_games_from_directory(Path(r"H:\Games"))
    for game in stuff:
        print(game)
        