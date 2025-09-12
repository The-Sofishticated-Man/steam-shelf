import os
import subprocess
import tempfile
from PIL import Image, ImageTk


class IconExtractor:
    """Handles extraction and processing of icons from executable files."""
    
    @staticmethod
    def get_exe_icon(exe_path, size=(24, 24)):
        """
        Extract icon from executable file.
        
        Args:
            exe_path (str): Path to the executable file
            size (tuple): Desired icon size as (width, height)
            
        Returns:
            ImageTk.PhotoImage or None: The extracted icon or None if extraction failed
        """
        try:
            if not os.path.exists(exe_path):
                return None
            
            # Create a temporary ICO file
            temp_ico = os.path.join(tempfile.gettempdir(), f"temp_icon_{os.getpid()}.ico")
            
            # Use PowerShell to extract icon (Windows only)
            ps_command = f'''
            Add-Type -AssemblyName System.Drawing
            $icon = [System.Drawing.Icon]::ExtractAssociatedIcon("{exe_path}")
            $icon.ToBitmap().Save("{temp_ico}", [System.Drawing.Imaging.ImageFormat]::Png)
            $icon.Dispose()
            '''
            
            # Run PowerShell command
            result = subprocess.run(['powershell', '-Command', ps_command], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and os.path.exists(temp_ico):
                # Load the image with PIL and resize
                img = Image.open(temp_ico)
                img = img.resize(size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # Clean up temp file
                try:
                    os.remove(temp_ico)
                except:
                    pass
                
                return photo
            
        except Exception as e:
            print(f"Failed to extract icon for {exe_path}: {e}")
        
        return None
    
    @staticmethod
    def get_default_icon(icon_type="game", size=16):
        """
        Get a default text-based icon.
        
        Args:
            icon_type (str): Type of icon ("game", "fallback")
            size (int): Font size for the icon
            
        Returns:
            str: Unicode character to use as default icon
        """
        icons = {
            "game": "🎮",
            "fallback": "⚙️"
        }
        return icons.get(icon_type, "⚙️")
