import tkinter as tk
from .game_entry_widget import GameEntryWidget


class GameListWidget:
    """Scrollable widget for displaying multiple game entries."""
    
    def __init__(self, parent, on_path_changed=None):
        """
        Initialize the game list widget.
        
        Args:
            parent: Parent tkinter widget
            on_path_changed (callable): Callback when a game's executable path is changed
        """
        self.parent = parent
        self.on_path_changed = on_path_changed
        self.game_widgets = []
        
        # Create the scrollable frame
        self.canvas = tk.Canvas(parent, bg='#2a2a2a', highlightthickness=0)
        self.scrollbar = tk.Scrollbar(parent, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#2a2a2a')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind("<Configure>", self._configure_canvas)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
    
    def _configure_canvas(self, event):
        """Handle canvas resize events."""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def add_games(self, games_data):
        """
        Add games to the list.
        
        Args:
            games_data (list): List of game dictionaries
        """
        self.clear_games()
        
        for i, game_data in enumerate(games_data):
            game_widget = GameEntryWidget(
                self.scrollable_frame, 
                game_data, 
                i, 
                self.on_path_changed
            )
            game_widget.pack(fill=tk.X, pady=5, padx=5)
            self.game_widgets.append(game_widget)
    
    def add_games_batch(self, games_data, start_index=0):
        """
        Add a batch of games to the list without clearing existing ones.
        
        Args:
            games_data (list): List of game dictionaries to add
            start_index (int): Starting index for game numbering
        """
        for i, game_data in enumerate(games_data):
            game_widget = GameEntryWidget(
                self.scrollable_frame, 
                game_data, 
                start_index + i,  # Use correct index for callbacks
                self.on_path_changed
            )
            game_widget.pack(fill=tk.X, pady=5, padx=5)
            self.game_widgets.append(game_widget)
    
    def clear_games(self):
        """Clear all games from the list."""
        for widget in self.game_widgets:
            widget.destroy()
        self.game_widgets.clear()
    
    def get_selected_games(self):
        """
        Get information about selected games.
        
        Returns:
            tuple: (selected_games_info, games_to_remove)
                - selected_games_info: list of dicts with 'name', 'path', 'game_object'
                - games_to_remove: list of game objects that should be removed
        """
        selected_games = []
        games_to_remove = []
        
        for widget in self.game_widgets:
            if widget.is_selected():
                selected_games.append({
                    'name': widget.get_name(),
                    'path': widget.get_path(),
                    'game_object': widget.get_game_object()
                })
            else:
                # Game is not selected, should be removed
                game_obj = widget.get_game_object()
                if game_obj:
                    games_to_remove.append(game_obj)
        
        return selected_games, games_to_remove
    
    def pack(self, **kwargs):
        """Pack the canvas and scrollbar."""
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
    
    def destroy(self):
        """Clean up the widget."""
        self.clear_games()
        if self.canvas:
            self.canvas.destroy()
        if self.scrollbar:
            self.scrollbar.destroy()
