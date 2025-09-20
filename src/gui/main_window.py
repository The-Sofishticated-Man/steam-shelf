import tkinter as tk
from gui.utils.user_selection import UserSelectionFrame
from gui.widgets.games_display import GamesDisplayFrame
from gui.widgets.current_games import CurrentGamesFrame
from gui.widgets.loading_screen import LoadingScreen
from gui.utils.threading_utils import ThreadManager
from core.models.repository import NonSteamGameRepository
from core.services.steam_db_utils import SteamDatabase
from steamclient import get_users
import threading


class SteamShelfGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.main_user = None
        self.chosen_directory = None
        self.steam_repo = None
        self.users = None  # Will be loaded after sync
        self.steam_db = SteamDatabase()
        
        # Initialize thread manager
        self.thread_manager = ThreadManager(self.root)
        
        # UI Components
        self.loading_screen = None
        self.user_selection = None
        self.current_games = None
        self.games_display = None
        
        self.setup_window()
        self.show_loading_and_sync()
    
    def setup_window(self):
        """Initialize the main window."""
        self.root.title("Steam Shelf - Initializing")
        self.root.geometry("600x900")
        self.root.configure(bg='#2a2a2a')
        
        # Set custom icon - just put icon.ico in your project root
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass  # Use default icon if file not found
    
    def show_loading_and_sync(self):
        """Show loading screen and perform database synchronization."""
        # Create and show loading screen
        self.loading_screen = LoadingScreen(self.root)
        self.loading_screen.show()
        
        # Start database sync in a separate thread
        sync_thread = threading.Thread(target=self.perform_sync, daemon=True)
        sync_thread.start()
    
    def perform_sync(self):
        """Perform database synchronization with progress updates."""
        try:
            def progress_callback(progress, message):
                # Schedule UI update on main thread
                self.root.after(0, lambda: self.loading_screen.update_progress(progress, message))
            
            # Perform the sync
            self.steam_db.sync(progress_callback)
            
            # Load users after sync is complete
            self.users = get_users()
            
            # Schedule transition to user selection on main thread
            self.root.after(0, self.transition_to_user_selection)
            
        except Exception as e:
            # Handle sync errors
            error_message = f"Error during initialization: {str(e)}"
            self.root.after(0, lambda: self.loading_screen.update_progress(0, error_message))
            print(f"Sync error: {e}")
    
    def transition_to_user_selection(self):
        """Transition from loading screen to user selection."""
        # Hide and destroy loading screen
        self.loading_screen.hide()
        self.loading_screen.destroy()
        
        # Update window title
        self.root.title("Steam Shelf - User Selection")
        
        # Create user selection interface
        self.create_user_selection_interface()
    
    def create_user_selection_interface(self):
        """Create the user selection interface."""
        self.user_selection = UserSelectionFrame(
            self.root, 
            self.users, 
            self.on_user_selected
        )

    def on_user_selected(self, user):
        """Handle user selection and proceed to next step."""
        self.main_user = user
        # Pass the already-synced database to the repository
        self.steam_repo = NonSteamGameRepository(
            self.main_user.id, 
            discovery_service=None  # Will create with synced database
        )
        # Update the discovery service to use our synced database
        from core.services.game_discovery import GameDiscoveryService
        from core.services.game_validator import GameValidator
        
        games_already_added = {game.AppName for game in self.steam_repo.games}
        validator = GameValidator(
            {"steam"},  # BLACKLISTED_DIRECTORIES
            {"uninstall", "setup", "update"}  # BLACKLISTED_EXECUTABLES
        )
        
        self.steam_repo.discovery_service = GameDiscoveryService(
            self.steam_db,  # Use our synced database
            validator,
            added_games=games_already_added
        )
        
        # Hide user selection frame
        self.user_selection.hide()
        
        # Show main interface
        self.show_main_interface()

    def show_main_interface(self):
        """Show the main interface after user selection."""
        # Create current games display
        self.current_games = CurrentGamesFrame(self.root, self.steam_repo)
        
        # Create games discovery and addition interface
        self.games_display = GamesDisplayFrame(
            self.root, 
            self.steam_repo, 
            self.on_directory_chosen,
            self.thread_manager  # Pass thread manager
        )
        
        # Set callback for when games are added
        self.games_display.set_on_games_added_callback(self.on_games_added)

    def on_directory_chosen(self, directory):
        """Handle when a directory is chosen for scanning."""
        self.chosen_directory = directory

    def on_games_added(self):
        """Handle when games are successfully added to Steam."""
        # Refresh the current games display to show newly added games
        if self.current_games:
            self.current_games.refresh()

    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()
