import tkinter as tk
from tkinter import messagebox, filedialog
import os
from pathlib import Path
from .game_list_widget import GameListWidget
from .progress_dialog import ProgressDialog, SimpleProgressDialog


class GamesDisplayFrame:
    def __init__(self, parent, steam_repo, on_directory_chosen_callback, thread_manager):
        self.parent = parent
        self.steam_repo = steam_repo
        self.on_directory_chosen_callback = on_directory_chosen_callback
        self.thread_manager = thread_manager
        self.found_games = []
        self.games_display_frame = None
        self.game_list_widget = None
        self.progress_dialog = None
        self.add_games_button = None
        self.on_games_added_callback = None
        self.create_directory_button()
    
    def set_on_games_added_callback(self, callback):
        """Set callback to be called when games are successfully added."""
        self.on_games_added_callback = callback

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
        # Show progress dialog
        self.progress_dialog = ProgressDialog(
            self.parent,
            title="Scanning Directory",
            message=f"Scanning {directory} for games...",
            cancellable=False
        )
        
        def scan_operation():
            """The actual scanning operation to run in background."""
            # Store current games count to know what's new
            initial_games_count = len(self.steam_repo.games)
            
            # Create a progress callback that updates the dialog
            def update_progress(message, progress):
                if self.progress_dialog:
                    # Schedule UI update on main thread
                    self.parent.after(0, lambda m=message, p=progress: self.progress_dialog.update_progress(m, p))
            
            # Use the repository's existing method to load games from directory
            # Now with progress callback support!
            self.steam_repo.load_games_from_directory(Path(directory), update_progress)
            
            # Get the newly discovered games
            new_games = self.steam_repo.games[initial_games_count:]
            
            # Convert to our display format
            found_games = []
            for game in new_games:
                found_games.append({
                    'name': game.AppName,
                    'path': game.Exe,
                    'selected': True,  # Default to selected
                    'game_object': game  # Store the actual NonSteamGame object
                })
            
            return found_games, directory
        
        def on_scan_success(result):
            """Called when scanning completes successfully."""
            found_games, directory = result
            self.found_games = found_games
            
            # Close progress dialog
            if self.progress_dialog:
                self.progress_dialog.close()
                self.progress_dialog = None
            
            # Display the found games with progressive loading
            self.show_found_games_progressive(directory)
        
        def on_scan_error(error):
            """Called when scanning fails."""
            # Close progress dialog
            if self.progress_dialog:
                self.progress_dialog.close()
                self.progress_dialog = None
            
            messagebox.showerror("Error", f"Error scanning directory: {str(error)}")
        
        # Start the background operation
        self.thread_manager.run_in_background(
            operation=scan_operation,
            on_success=on_scan_success,
            on_error=on_scan_error
        )

    def show_found_games_progressive(self, directory):
        """Display the found games with progressive loading to keep UI responsive."""
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
                                    text=f"Found {len(self.found_games)} potential games. Loading...",
                                    font=("Arial", 10),
                                    bg='#2a2a2a', fg='lightgray')
        instruction_label.pack(pady=(0, 10))
        
        # Create container for the game list
        list_container = tk.Frame(self.games_display_frame, bg='#2a2a2a')
        list_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create the game list widget but don't add games yet
        self.game_list_widget = GameListWidget(list_container, self.on_path_changed)
        self.game_list_widget.pack()
        
        # Add loading indicator
        self.loading_indicator = SimpleProgressDialog(list_container, "Loading games...")
        self.loading_indicator.show()
        
        # Start progressive loading of games
        self._load_games_progressively(instruction_label, 0)
    
    def _load_games_progressively(self, instruction_label, start_index, batch_size=2):
        """Load games in small batches to keep UI responsive."""
        end_index = min(start_index + batch_size, len(self.found_games))
        
        # Add this batch of games
        batch_games = self.found_games[start_index:end_index]
        if batch_games:
            self.game_list_widget.add_games_batch(batch_games, start_index)
        
        # Update progress
        progress = end_index / len(self.found_games)
        instruction_label.configure(text=f"Loading games... ({end_index}/{len(self.found_games)})")
        
        if end_index < len(self.found_games):
            # Schedule next batch with shorter delay for faster loading
            self.parent.after(5, lambda: self._load_games_progressively(instruction_label, end_index, batch_size))
        else:
            # All games loaded
            instruction_label.configure(text=f"Found {len(self.found_games)} potential games. Edit paths if needed:")
            
            # Hide loading indicator
            if hasattr(self, 'loading_indicator'):
                self.loading_indicator.hide()
            
            # Add the "Add Games" button
            self._add_games_button()
    
    def _add_games_button(self):
        """Add the 'Add Selected Games' button after all games are loaded."""
        self.add_games_button = tk.Button(self.games_display_frame, text="Add Selected Games to Steam",
                              command=self.add_selected_games,
                              font=("Arial", 11, "bold"),
                              bg='#0078d4', fg='white',
                              activebackground='#106ebe', activeforeground='white',
                              relief='flat', bd=0, pady=10)
        self.add_games_button.pack(pady=15)

    def show_found_games(self, directory):
        """Legacy method - use show_found_games_progressive instead."""
        self.show_found_games_progressive(directory)
    
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
        
        # Show progress dialog
        self.progress_dialog = ProgressDialog(
            self.parent,
            title="Adding Games",
            message="Saving games to Steam and downloading artwork...",
            cancellable=False
        )
        
        def save_operation():
            """The actual save operation to run in background."""
            # Create a progress callback for image downloading
            def progress_update(message, progress):
                if self.progress_dialog:
                    # Schedule update on main thread
                    self.parent.after(0, lambda m=message, p=progress: self.progress_dialog.update_progress(m, p))
            
            # Save the updated games to VDF
            self.steam_repo.save_games_as_vdf()
            
            # Download images for the new games with progress
            self.steam_repo.save_game_images(progress_callback=progress_update)
            
            return selected_games
        
        def on_save_success(selected_games):
            """Called when saving completes successfully."""
            # Close progress dialog
            if self.progress_dialog:
                self.progress_dialog.close()
                self.progress_dialog = None
            
            # Hide the add games button since games have been added
            if self.add_games_button:
                self.add_games_button.destroy()
                self.add_games_button = None
            
            # Notify parent window that games were added
            if self.on_games_added_callback:
                self.on_games_added_callback()
            
            game_names = [game['name'] for game in selected_games]
            messagebox.showinfo("Success", 
                f"Added {len(selected_games)} games to Steam!\n\nGames added:\n" + "\n".join(game_names))
        
        def on_save_error(error):
            """Called when saving fails."""
            # Close progress dialog
            if self.progress_dialog:
                self.progress_dialog.close()
                self.progress_dialog = None
            
            messagebox.showerror("Error", f"Error saving games: {str(error)}")
        
        # Start the background operation
        self.thread_manager.run_in_background(
            operation=save_operation,
            on_success=on_save_success,
            on_error=on_save_error
        )
