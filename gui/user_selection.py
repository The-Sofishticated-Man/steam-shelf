import tkinter as tk


class UserSelectionFrame:
    def __init__(self, parent, users, callback):
        self.parent = parent
        self.users = users
        self.callback = callback
        self.frame = None
        self.create_interface()
    
    def create_interface(self):
        """Create the user selection interface."""
        # Create user selection frame
        self.frame = tk.Frame(self.parent, bg='#2a2a2a')
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(self.frame, text="Select Steam User", 
                              font=("Arial", 16, "bold"), 
                              bg='#2a2a2a', fg='white')
        title_label.pack(pady=(0, 20))
        
        if not self.users:
            # No users found
            no_users_label = tk.Label(self.frame, text="No Steam users found!", 
                                     font=("Arial", 12), 
                                     bg='#2a2a2a', fg='red')
            no_users_label.pack(pady=20)
        else:
            # Instructions
            instruction_label = tk.Label(self.frame, text="Choose the Steam user to add games to:", 
                                        font=("Arial", 11), 
                                        bg='#2a2a2a', fg='lightgray')
            instruction_label.pack(pady=(0, 15))

            # User buttons
            for i, user in enumerate(self.users):
                user_text = f"(ID: {user.id})"
                
                user_button = tk.Button(self.frame, 
                                       text=user_text,
                                       command=lambda u=user: self.callback(u),
                                       font=("Arial", 10),
                                       bg='#404040',
                                       fg='white',
                                       activebackground='#505050',
                                       activeforeground='white',
                                       relief='flat',
                                       bd=1,
                                       pady=10,
                                       width=30)
                user_button.pack(pady=5)
                
                # Highlight first user as default choice
                if i == 0:
                    user_button.configure(bg='#0078d4', activebackground='#106ebe')

    def hide(self):
        """Hide the user selection frame."""
        if self.frame:
            self.frame.pack_forget()
