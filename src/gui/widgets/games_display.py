import tkinter as tk
from tkinter import messagebox, filedialog
import os
from pathlib import Path
from .game_list_widget import GameListWidget


class GamesDisplayFrame:
    def __init__(self, parent, steam_repo, on_directory_chosen_callback):
        self.parent = parent
        self.steam_repo = steam_repo
        self.on_directory_chosen_callback = on_directory_chosen_callback
        self.found_games = []
        self.games_display_frame = None
        self.game_list_widget = None
        self.create_directory_button()
    
    def create_directory_button(self):
        """Create the directory selection button."""
        # Directory selection button
        dir_button = tk.Button(self.parent, text="Choose Games Directory", 
                              command=self.pick_directory, font=("Arial", 10),
                              bg='#0078d4', fg='white',
                              activebackground='#106ebe', activeforeground='white',
                              relief='flat', bd=0, pady=8)
        dir_button.pack(pady=10)

    def pick_directory(self):
        """Handle directory selection and scan for games."""
        folder = filedialog.askdirectory()
        if folder:
            self.on_directory_chosen_callback(folder)
            self.scan_directory_for_games(folder)

    def scan_directory_for_games(self, directory):
        """Scan the selected directory for games using NonSteamGameRepository."""
        try:
            # Store current games count to know what's new
            initial_games_count = len(self.steam_repo.games)
            
            # Use the repository's existing method to load games from directory
            self.steam_repo.load_games_from_directory(Path(directory))
            
            # Get the newly discovered games
            new_games = self.steam_repo.games[initial_games_count:]
            
            # Convert to our display format
            self.found_games = []
            for game in new_games:
                self.found_games.append({
                    'name': game.AppName,
                    'path': game.Exe,
                    'selected': True,  # Default to selected
                    'game_object': game  # Store the actual NonSteamGame object
                })
        
        except Exception as e:
            messagebox.showerror("Error", f"Error scanning directory: {str(e)}")
            return
        
        # Display the found games
        self.show_found_games(directory)

    def show_found_games(self, directory):
        """Display the found games with options to edit executable paths."""
        # Remove existing games display frame if it exists
        if self.games_display_frame:
            self.games_display_frame.destroy()
        
        # Create new frame for found games
        self.games_display_frame = tk.Frame(self.parent, bg='#2a2a2a')
        self.games_display_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Title showing selected directory
        dir_title = tk.Label(self.games_display_frame, 
                            text=f"Games found in: {directory}", 
                            font=("Arial", 12, "bold"),
                            bg='#2a2a2a', fg='lightgreen')
        dir_title.pack(pady=(0, 10))
        
        if not self.found_games:
            no_games_label = tk.Label(self.games_display_frame, 
                                     text="No executable files found in the selected directory.",
                                     font=("Arial", 10),
                                     bg='#2a2a2a', fg='gray')
            no_games_label.pack(pady=20)
            return
        
        # Instructions
        instruction_label = tk.Label(self.games_display_frame, 
                                    text=f"Found {len(self.found_games)} potential games. Edit paths if needed:",
                                    font=("Arial", 10),
                                    bg='#2a2a2a', fg='lightgray')
        instruction_label.pack(pady=(0, 10))
        
        # Create container for the game list
        list_container = tk.Frame(self.games_display_frame, bg='#2a2a2a')
        list_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create and populate the game list widget
        self.game_list_widget = GameListWidget(list_container, self.on_path_changed)
        self.game_list_widget.add_games(self.found_games)
        self.game_list_widget.pack()
        
        # Add games button
        add_button = tk.Button(self.games_display_frame, text="Add Selected Games to Steam",
                              command=self.add_selected_games,
                              font=("Arial", 11, "bold"),
                              bg='#0078d4', fg='white',
                              activebackground='#106ebe', activeforeground='white',
                              relief='flat', bd=0, pady=10)
        add_button.pack(pady=15)
    
    def on_path_changed(self, game_index, new_path):
        """Handle when a game's executable path is changed."""
        if game_index < len(self.found_games):
            self.found_games[game_index]['path'] = new_path

    def add_selected_games(self):
        """Add the selected games to Steam using the repository."""
        if not self.game_list_widget:
            messagebox.showwarning("No Games", "No games to add.")
            return
        
        selected_games, games_to_remove = self.game_list_widget.get_selected_games()
        
        # Remove unselected games from repository
        for game_to_remove in games_to_remove:
            if game_to_remove in self.steam_repo.games:
                self.steam_repo.games.remove(game_to_remove)
        
        if not selected_games:
            messagebox.showwarning("No Games Selected", "No games were selected to add.")
            return
        
        try:
            # Save the updated games to VDF
            self.steam_repo.save_games_as_vdf()
            
            # Download images for the new games
            self.steam_repo.save_game_images()
            
            game_names = [game['name'] for game in selected_games]
            messagebox.showinfo("Success", f"Added {len(selected_games)} games to Steam!\n\nGames added:\n" + "\n".join(game_names))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving games: {str(e)}")
