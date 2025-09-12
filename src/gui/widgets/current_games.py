import tkinter as tk


class CurrentGamesFrame:
    def __init__(self, parent, steam_repo):
        self.parent = parent
        self.steam_repo = steam_repo
        self.frame = None
        self.create_interface()
    
    def create_interface(self):
        """Create the current games display interface."""
        # Main interface label
        main_label = tk.Label(self.parent, text=f"Selected User: {self.steam_repo.user_id}", 
                             font=("Arial", 12, "bold"),
                             bg='#2a2a2a', fg='white')
        main_label.pack(pady=10)

        # Create a frame for the games list with scrollbar
        games_container = tk.Frame(self.parent, bg='#2a2a2a')
        games_container.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Add a title for the games section
        if self.steam_repo.games:
            games_title = tk.Label(games_container, text="Current Non-Steam Games:", 
                                  font=("Arial", 11, "bold"),
                                  bg='#2a2a2a', fg='lightgray')
            games_title.pack(pady=(0, 10))
            
            # Create canvas and scrollbar for scrollable content
            canvas = tk.Canvas(games_container, bg='#2a2a2a', highlightthickness=0)
            scrollbar = tk.Scrollbar(games_container, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='#2a2a2a')
            
            # Configure scrolling
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            # Configure canvas to expand frame to full width
            def configure_canvas(event):
                canvas.itemconfig(canvas_frame, width=event.width)
            
            canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.bind("<Configure>", configure_canvas)
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Display each game in the scrollable frame
            for i, game in enumerate(self.steam_repo.games, 1):
                game_label = tk.Label(scrollable_frame, 
                                     text=f"{i:2d}. {game.AppName}",
                                     font=("Arial", 10),
                                     bg='#404040', fg='white',
                                     relief='flat', bd=1,
                                     anchor='w', padx=10, pady=5)
                game_label.pack(fill=tk.X, pady=2, padx=0)
            
            # Pack canvas and scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Enable mouse wheel scrolling
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
        else:
            no_games_label = tk.Label(games_container, text="No non-Steam games found.",
                                     font=("Arial", 10),
                                     bg='#2a2a2a', fg='gray')
            no_games_label.pack(pady=10)
