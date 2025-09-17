import tkinter as tk
from tkinter import ttk


class ProgressDialog:
    """A modal progress dialog for showing operation progress."""
    
    def __init__(self, parent, title="Processing...", message="Please wait...", cancellable=False):
        """Initialize the progress dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            message: Initial message
            cancellable: Whether the operation can be cancelled
        """
        self.parent = parent
        self.cancelled = False
        self._on_cancel = None
        
        # Create the dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg='#2a2a2a')
        
        # Make it modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self._center_dialog()
        
        # Create the UI
        self._create_ui(message, cancellable)
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_window_close)
    
    def _center_dialog(self):
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate center position
        dialog_width = self.dialog.winfo_reqwidth()
        dialog_height = self.dialog.winfo_reqheight()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def _create_ui(self, message, cancellable):
        """Create the dialog UI elements."""
        # Main frame
        main_frame = tk.Frame(self.dialog, bg='#2a2a2a', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Message label
        self.message_label = tk.Label(main_frame, 
                                     text=message,
                                     font=("Arial", 10),
                                     bg='#2a2a2a', fg='white',
                                     wraplength=350,
                                     justify='center')
        self.message_label.pack(pady=(0, 15))
        
        # Progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.Horizontal.TProgressbar",
                       background='#0078d4',
                       troughcolor='#404040',
                       borderwidth=1,
                       lightcolor='#0078d4',
                       darkcolor='#0078d4')
        
        self.progress_bar = ttk.Progressbar(main_frame,
                                          style="Custom.Horizontal.TProgressbar",
                                          mode='indeterminate',
                                          length=300)
        self.progress_bar.pack(pady=(0, 15))
        
        # Start the progress animation
        self.progress_bar.start(10)
        
        # Cancel button (if cancellable)
        if cancellable:
            button_frame = tk.Frame(main_frame, bg='#2a2a2a')
            button_frame.pack()
            
            self.cancel_button = tk.Button(button_frame,
                                         text="Cancel",
                                         command=self._on_cancel_clicked,
                                         font=("Arial", 10),
                                         bg='#666666',
                                         fg='white',
                                         activebackground='#777777',
                                         relief='flat',
                                         bd=0,
                                         pady=8,
                                         padx=20)
            self.cancel_button.pack()
    
    def update_progress(self, message=None, progress=None):
        """Update the progress dialog.
        
        Args:
            message: New message to display (None to keep current)
            progress: Progress value 0.0-1.0 (None for indeterminate)
        """
        if message is not None:
            self.message_label.configure(text=message)
        
        if progress is not None:
            # Switch to determinate mode
            self.progress_bar.stop()
            self.progress_bar.configure(mode='determinate')
            self.progress_bar['value'] = progress * 100
        else:
            # Switch to indeterminate mode if not already
            if self.progress_bar['mode'] != 'indeterminate':
                self.progress_bar.configure(mode='indeterminate')
                self.progress_bar.start(10)
        
        # Update the dialog
        self.dialog.update_idletasks()
    
    def set_cancel_callback(self, callback):
        """Set the callback to call when cancel is clicked.
        
        Args:
            callback: Function to call when cancel is clicked
        """
        self._on_cancel = callback
    
    def _on_cancel_clicked(self):
        """Handle cancel button click."""
        self.cancelled = True
        if self._on_cancel:
            self._on_cancel()
        self.close()
    
    def _on_window_close(self):
        """Handle window close button."""
        if hasattr(self, 'cancel_button'):
            # If cancellable, treat close as cancel
            self._on_cancel_clicked()
        # Otherwise, ignore close attempts during operation
    
    def is_cancelled(self):
        """Check if the operation was cancelled."""
        return self.cancelled
    
    def close(self):
        """Close the progress dialog."""
        try:
            self.progress_bar.stop()
            self.dialog.grab_release()
            self.dialog.destroy()
        except tk.TclError:
            # Dialog already destroyed
            pass
    
    def show(self):
        """Show the dialog (blocking)."""
        self.dialog.wait_window()


class SimpleProgressDialog:
    """A simpler non-modal progress indicator."""
    
    def __init__(self, parent, message="Loading..."):
        """Initialize simple progress dialog.
        
        Args:
            parent: Parent widget to show progress in
            message: Message to display
        """
        self.parent = parent
        self.overlay_frame = None
        self.message = message
        
    def show(self):
        """Show the progress overlay."""
        # Create overlay frame
        self.overlay_frame = tk.Frame(self.parent, 
                                    bg='#2a2a2a', 
                                    relief='raised', 
                                    bd=2)
        self.overlay_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Add loading message
        loading_label = tk.Label(self.overlay_frame,
                               text=self.message,
                               font=("Arial", 12, "bold"),
                               bg='#2a2a2a', fg='white',
                               padx=30, pady=20)
        loading_label.pack()
        
        # Add spinner (simple text animation)
        self.spinner_label = tk.Label(self.overlay_frame,
                                    text="⠋",
                                    font=("Arial", 16),
                                    bg='#2a2a2a', fg='#0078d4')
        self.spinner_label.pack(pady=(0, 10))
        
        # Start spinner animation
        self._animate_spinner()
    
    def _animate_spinner(self):
        """Animate the spinner."""
        if self.overlay_frame and self.overlay_frame.winfo_exists():
            spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
            current = self.spinner_label.cget('text')
            try:
                next_index = (spinner_chars.index(current) + 1) % len(spinner_chars)
                self.spinner_label.configure(text=spinner_chars[next_index])
            except ValueError:
                self.spinner_label.configure(text=spinner_chars[0])
            
            # Schedule next animation frame
            self.parent.after(100, self._animate_spinner)
    
    def hide(self):
        """Hide the progress overlay."""
        if self.overlay_frame:
            self.overlay_frame.destroy()
            self.overlay_frame = None