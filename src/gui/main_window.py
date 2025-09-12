import tkinter as tk
from gui.utils.user_selection import UserSelectionFrame
from gui.widgets.games_display import GamesDisplayFrame
from gui.widgets.current_games import CurrentGamesFrame
from core.models.repository import NonSteamGameRepository
from steamclient import get_users


class SteamShelfGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.main_user = None
        self.chosen_directory = None
        self.steam_repo = None
        self.users = get_users()
        
        # UI Components
        self.user_selection = None
        self.current_games = None
        self.games_display = None
        
        self.setup_window()
        self.create_user_selection_interface()
    
    def setup_window(self):
        """Initialize the main window."""
        self.root.title("Steam Shelf - User Selection")
        self.root.geometry("500x800")
        self.root.configure(bg='#2a2a2a')
    
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
        self.steam_repo = NonSteamGameRepository(self.main_user.id)
        
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
            self.on_directory_chosen
        )

    def on_directory_chosen(self, directory):
        """Handle when a directory is chosen for scanning."""
        self.chosen_directory = directory

    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()
