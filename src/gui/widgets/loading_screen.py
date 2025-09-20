import tkinter as tk
from tkinter import ttk


class LoadingScreen:
    """Loading screen widget for displaying progress during database synchronization."""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.progress_bar = None
        self.status_label = None
        self.title_label = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the loading screen UI components."""
        # Create main frame
        self.frame = tk.Frame(self.parent, bg='#2a2a2a')
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a container for centered content
        container = tk.Frame(self.frame, bg='#2a2a2a')
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title label
        self.title_label = tk.Label(
            container,
            text="Steam Shelf",
            font=("Arial", 24, "bold"),
            fg='#ffffff',
            bg='#2a2a2a'
        )
        self.title_label.pack(pady=(0, 30))
        
        # Loading message
        loading_label = tk.Label(
            container,
            text="Initializing Steam Database...",
            font=("Arial", 14),
            fg='#cccccc',
            bg='#2a2a2a'
        )
        loading_label.pack(pady=(0, 20))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            container,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(pady=(0, 15))
        
        # Status label
        self.status_label = tk.Label(
            container,
            text="Preparing to sync...",
            font=("Arial", 10),
            fg='#888888',
            bg='#2a2a2a'
        )
        self.status_label.pack()
        
        # Style the progress bar for dark theme
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "TProgressbar",
            background='#4a9eff',
            darkcolor='#2a2a2a',
            lightcolor='#4a9eff',
            bordercolor='#555555',
            troughcolor='#404040'
        )
    
    def update_progress(self, progress_percent, status_message):
        """Update the progress bar and status message.
        
        Args:
            progress_percent (float): Progress percentage (0-100)
            status_message (str): Status message to display
        """
        if self.progress_bar:
            self.progress_bar['value'] = progress_percent
            
        if self.status_label:
            self.status_label.config(text=status_message)
            
        # Force UI update
        self.parent.update_idletasks()
    
    def show(self):
        """Show the loading screen."""
        if self.frame:
            self.frame.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        """Hide the loading screen."""
        if self.frame:
            self.frame.pack_forget()
            
    def destroy(self):
        """Destroy the loading screen."""
        if self.frame:
            self.frame.destroy()
            self.frame = None