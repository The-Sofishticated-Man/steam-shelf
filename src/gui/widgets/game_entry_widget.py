import tkinter as tk
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
        """Create the icon display."""
        try:
            icon = IconExtractor.get_exe_icon(self.game_data.get('path', ''))
            if icon:
                icon_label = tk.Label(parent, image=icon, bg='#404040')
                icon_label.pack()
                self.icon_image = icon  # Keep reference
            else:
                # Default game icon
                default_icon = IconExtractor.get_default_icon("game", 16)
                icon_label = tk.Label(parent, text=default_icon, font=("Arial", 16), 
                                    bg='#404040', fg='white')
                icon_label.pack()
        except:
            # Fallback icon
            fallback_icon = IconExtractor.get_default_icon("fallback", 16)
            icon_label = tk.Label(parent, text=fallback_icon, font=("Arial", 16), 
                                bg='#404040', fg='white')
            icon_label.pack()
    
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
        file_path = filedialog.askopenfilename(
            title="Select Executable",
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
