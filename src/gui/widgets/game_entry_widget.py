import tkinter as tk
import threading
from tkinter import filedialog
from gui.utils.icon_extractor import IconExtractor


class GameEntryWidget:
    """Widget for displaying and editing a single game entry."""
    
    def __init__(self, parent, game_data, index, on_path_changed=None):
        """
        Initialize a game entry widget.
        
        Args:
            parent: Parent tkinter widget
            game_data (dict): Game data with 'name', 'path', 'selected', 'game_object'
            index (int): Index of this game in the list
            on_path_changed (callable): Callback when executable path is changed
        """
        self.parent = parent
        self.game_data = game_data
        self.index = index
        self.on_path_changed = on_path_changed
        
        # Widget state
        self.selected_var = tk.BooleanVar(value=game_data.get('selected', True))
        self.path_var = tk.StringVar(value=game_data.get('path', ''))
        self.icon_image = None  # Keep reference to prevent garbage collection
        
        # Loading animation state
        self.loading_animation = None
        self.loading_icons = ["⏳", "⌛", "🔄", "⚡"]
        self.loading_index = 0
        self.is_loading = False
        
        # Create the widget
        self.frame = self._create_widget()
    
    def _create_widget(self):
        """Create the game entry widget."""
        # Main game frame
        game_frame = tk.Frame(self.parent, bg='#404040', relief='raised', bd=1)
        
        # Header frame (checkbox, icon, name)
        header_frame = tk.Frame(game_frame, bg='#404040')
        header_frame.pack(fill=tk.X, padx=10, pady=(5, 0))
        
        # Checkbox for selection
        checkbox = tk.Checkbutton(header_frame, variable=self.selected_var, 
                                 bg='#404040', fg='white', selectcolor='#404040',
                                 activebackground='#404040')
        checkbox.pack(side='left')
        
        # Icon frame
        icon_frame = tk.Frame(header_frame, bg='#404040')
        icon_frame.pack(side='left', padx=(5, 10))
        
        # Store reference to icon frame for updates
        self.icon_frame = icon_frame
        
        # Get and display icon
        self._create_icon(icon_frame)
        
        # Game name
        name_label = tk.Label(header_frame, text=f"Game: {self.game_data.get('name', 'Unknown')}", 
                             font=("Arial", 10, "bold"),
                             bg='#404040', fg='white',
                             anchor='w')
        name_label.pack(side='left', fill=tk.X, expand=True, padx=(5, 0))
        
        # Executable path section
        self._create_path_section(game_frame)
        
        return game_frame
    
    def _create_icon(self, parent):
        """Create the icon display with asynchronous loading."""
        # Start with loading indicator
        self._start_loading_animation(parent)
        
        # Asynchronously load the real icon
        exe_path = self.game_data.get('path', '')
        if exe_path:
            print(f"Starting async icon loading for: {exe_path}")
            
            def on_icon_loaded(icon):
                print(f"Icon callback called for {exe_path}: {icon is not None}")
                # This callback runs in a background thread, so we need to schedule UI update
                def update_icon():
                    try:
                        # Stop loading animation
                        self._stop_loading_animation()
                        
                        # Check if widget still exists
                        if not hasattr(self, 'icon_label') or not self.icon_label.winfo_exists():
                            return
                        
                        if icon:
                            print(f"Updating with extracted icon for: {exe_path}")
                            # Replace the loading icon with the extracted image icon
                            self.icon_label.destroy()
                            new_icon_label = tk.Label(parent, image=icon, bg='#404040')
                            new_icon_label.pack()
                            self.icon_image = icon  # Keep reference to prevent garbage collection
                            self.icon_label = new_icon_label
                        else:
                            print(f"Using fallback icon for: {exe_path}")
                            # Show fallback game icon if extraction failed
                            fallback_icon = IconExtractor.get_default_icon("game", 16)
                            self.icon_label.configure(text=fallback_icon, fg='white')
                    except tk.TclError as e:
                        print(f"Error updating icon UI: {e}")
                
                # Schedule the UI update on the main thread using the parent widget
                try:
                    parent.after(0, update_icon)
                except Exception as e:
                    print(f"Error scheduling UI update: {e}")
            
            # Start async icon extraction
            IconExtractor.get_exe_icon_async(exe_path, (24, 24), on_icon_loaded)
        else:
            # No path available, show fallback immediately
            self._stop_loading_animation()
            fallback_icon = IconExtractor.get_default_icon("game", 16)
            self.icon_label.configure(text=fallback_icon, fg='white')
    
    def _start_loading_animation(self, parent):
        """Start the loading animation."""
        self.is_loading = True
        self.loading_index = 0
        
        # Create initial loading icon
        loading_icon = self.loading_icons[self.loading_index]
        icon_label = tk.Label(parent, text=loading_icon, font=("Arial", 16), 
                            bg='#404040', fg='orange')
        icon_label.pack()
        self.icon_label = icon_label
        
        # Start animation loop
        self._animate_loading()
    
    def _animate_loading(self):
        """Animate the loading icon."""
        if not self.is_loading or not hasattr(self, 'icon_label'):
            return
        
        try:
            if self.icon_label.winfo_exists():
                # Update to next loading icon
                self.loading_index = (self.loading_index + 1) % len(self.loading_icons)
                new_icon = self.loading_icons[self.loading_index]
                self.icon_label.configure(text=new_icon)
                
                # Schedule next animation frame
                self.loading_animation = self.icon_label.after(500, self._animate_loading)
        except tk.TclError:
            # Widget was destroyed, stop animation
            self.is_loading = False
    
    def _stop_loading_animation(self):
        """Stop the loading animation."""
        self.is_loading = False
        if hasattr(self, 'loading_animation') and self.loading_animation:
            try:
                self.icon_label.after_cancel(self.loading_animation)
            except:
                pass
            self.loading_animation = None
    
    def _refresh_icon(self):
        """Refresh the icon based on current executable path."""
        if hasattr(self, 'icon_label') and hasattr(self, 'icon_frame'):
            # Stop any current loading animation
            self._stop_loading_animation()
            
            # Clear existing icon
            for widget in self.icon_frame.winfo_children():
                widget.destroy()
            
            # Update game_data path for icon extraction
            self.game_data['path'] = self.path_var.get()
            
            # Create new icon with loading animation
            self._create_icon(self.icon_frame)
    
    def _create_path_section(self, parent):
        """Create the executable path editing section."""
        # Executable path frame
        path_frame = tk.Frame(parent, bg='#404040')
        path_frame.pack(fill=tk.X, padx=10, pady=5)
        
        path_label = tk.Label(path_frame, text="Executable:", 
                             font=("Arial", 9),
                             bg='#404040', fg='lightgray')
        path_label.pack(anchor='w')
        
        # Entry for path with browse button
        entry_frame = tk.Frame(path_frame, bg='#404040')
        entry_frame.pack(fill=tk.X, pady=2)
        
        path_entry = tk.Entry(entry_frame, textvariable=self.path_var,
                             font=("Arial", 9), bg='#555555', fg='white',
                             insertbackground='white')
        path_entry.pack(side='left', fill=tk.X, expand=True, padx=(0, 5))
        
        # Browse button
        browse_btn = tk.Button(entry_frame, text="Browse",
                              command=self._browse_executable,
                              font=("Arial", 8),
                              bg='#606060', fg='white',
                              activebackground='#707070')
        browse_btn.pack(side='right')
    
    def _browse_executable(self):
        """Open file dialog to select executable."""
        # Determine initial directory from current path
        current_path = self.path_var.get()
        initial_dir = None
        
        if current_path:
            import os
            # If current path exists, use its directory
            if os.path.exists(current_path):
                initial_dir = os.path.dirname(current_path)
            else:
                # If path doesn't exist, try to extract directory part
                dir_part = os.path.dirname(current_path)
                if os.path.exists(dir_part):
                    initial_dir = dir_part
        
        # If no initial directory determined, try to use game name to find folder
        if not initial_dir:
            game_name = self.game_data.get('name', '')
            if game_name and hasattr(self, 'parent'):
                # This is a heuristic - you may need to adjust based on your game discovery logic
                import os
                possible_paths = [
                    f"H:\\Games\\{game_name}",  # Common game directory structure
                    f"C:\\Games\\{game_name}",
                    f"C:\\Program Files\\{game_name}",
                    f"C:\\Program Files (x86)\\{game_name}"
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        initial_dir = path
                        break
        
        file_path = filedialog.askopenfilename(
            title="Select Executable",
            initialdir=initial_dir,
            filetypes=[
                ("Executable files", "*.exe"),
                ("Batch files", "*.bat"),
                ("Command files", "*.cmd"),
                ("Shortcut files", "*.lnk"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.path_var.set(file_path)
            # Update the game object's exe path
            if 'game_object' in self.game_data:
                self.game_data['game_object'].Exe = file_path
            
            # Refresh the icon with the new executable
            self._refresh_icon()
            
            # Notify parent of path change
            if self.on_path_changed:
                self.on_path_changed(self.index, file_path)
    
    def is_selected(self):
        """Check if this game is selected."""
        return self.selected_var.get()
    
    def get_path(self):
        """Get the current executable path."""
        return self.path_var.get()
    
    def get_game_object(self):
        """Get the associated game object."""
        return self.game_data.get('game_object')
    
    def get_name(self):
        """Get the game name."""
        return self.game_data.get('name', 'Unknown')
    
    def pack(self, **kwargs):
        """Pack the widget frame."""
        self.frame.pack(**kwargs)
    
    def destroy(self):
        """Clean up the widget."""
        if self.frame:
            self.frame.destroy()
