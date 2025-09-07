from pathlib import Path
from vdf_utils import write_binary_vdf, parse_vdf
from NonSteamGame import NonSteamGame
from game_discovery import GameDiscoveryService
from game_validator import GameValidator
from vdf_serializer import VDFSerializer
from steam_db_utils import SteamDatabase

BLACKLISTED_DIRECTORIES = {"steam"}
BLACKLISTED_EXECUTABLES = {"uninstall", "setup", "update"}

class NonSteamGameRepository:
    def __init__(self, 
                 discovery_service: GameDiscoveryService = None,
                 serializer: VDFSerializer = None,
                 validator: GameValidator = None):
        self.games: list[NonSteamGame] = []
        
        # Use dependency injection or create default services
        self.validator = validator or GameValidator(
            BLACKLISTED_DIRECTORIES, 
            BLACKLISTED_EXECUTABLES
        )
        self.serializer = serializer or VDFSerializer()
        self.discovery_service = discovery_service or GameDiscoveryService(
            SteamDatabase(), 
            self.validator
        )
    
    def add_game(self, game: NonSteamGame):
        self.games.append(game)
    
    def load_games_from_directory(self, path: Path):
        """Load games by discovering them from a directory structure."""
        candidates = self.discovery_service.discover_games_from_directory(path)
        for candidate in candidates:
            game = NonSteamGame.from_candidate(candidate)
            self.add_game(game)
                
    def save_games_as_vdf(self, path: Path):
        """Save games to a VDF file."""
        vdf_data = self.serializer.games_to_vdf(self.games)
        write_binary_vdf(vdf_data, path)
        
    def load_games_from_vdf(self, path: Path):
        """Load games from an existing VDF file."""
        vdf_data = parse_vdf(path)
        games = self.serializer.games_from_vdf(vdf_data)
        for game in games:
            self.add_game(game)
            
    def __iter__(self):
        for game in self.games:
            yield game
if __name__ == "__main__":
    stuff = NonSteamGameRepository()
    stuff.load_games_from_directory(Path(r"H:\Games"))
    for game in stuff:
        print(game)
        