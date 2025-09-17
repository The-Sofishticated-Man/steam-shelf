import os
import subprocess
import tempfile
import threading
from PIL import Image, ImageTk
from functools import lru_cache


class IconExtractor:
    """Handles extraction and processing of icons from executable files."""
    
    @staticmethod
    @lru_cache(maxsize=100)  # Cache icons to avoid re-extraction
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
            
            # Run PowerShell command with shorter timeout for responsiveness
            result = subprocess.run(['powershell', '-Command', ps_command], 
                                  capture_output=True, text=True, timeout=3)
            
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
    def get_exe_icon_async(exe_path, size=(24, 24), callback=None):
        """
        Extract icon from executable file asynchronously.
        
        Args:
            exe_path (str): Path to the executable file
            size (tuple): Desired icon size as (width, height)
            callback (callable): Function to call with the result
        """
        def extract_icon():
            try:
                print(f"Starting icon extraction for: {exe_path}")
                
                if not os.path.exists(exe_path):
                    print(f"File does not exist: {exe_path}")
                    if callback:
                        callback(None)
                    return
                
                # Create a temporary ICO file
                temp_ico = os.path.join(tempfile.gettempdir(), f"temp_icon_{threading.get_ident()}.ico")
                
                # Use PowerShell to extract icon (Windows only) with better error handling
                ps_command = f'''
                try {{
                    Add-Type -AssemblyName System.Drawing -ErrorAction Stop
                    $icon = [System.Drawing.Icon]::ExtractAssociatedIcon("{exe_path}")
                    if ($icon -ne $null) {{
                        $bitmap = $icon.ToBitmap()
                        $bitmap.Save("{temp_ico}", [System.Drawing.Imaging.ImageFormat]::Png)
                        $bitmap.Dispose()
                        $icon.Dispose()
                        Write-Output "SUCCESS"
                    }} else {{
                        Write-Error "No icon found"
                        exit 1
                    }}
                }} catch {{
                    Write-Error $_.Exception.Message
                    exit 1
                }}
                '''
                
                print(f"Running PowerShell command for: {exe_path}")
                
                # Run PowerShell command with longer timeout and better flags
                result = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', ps_command], 
                                      capture_output=True, text=True, timeout=15)
                
                print(f"PowerShell result for {exe_path}: {result.returncode}")
                if result.stdout:
                    print(f"PowerShell stdout: {result.stdout.strip()}")
                if result.stderr:
                    print(f"PowerShell stderr: {result.stderr.strip()}")
                
                # Check if extraction was successful
                success = (result.returncode == 0 and 
                          os.path.exists(temp_ico) and 
                          os.path.getsize(temp_ico) > 0 and
                          "SUCCESS" in result.stdout)
                
                if success:
                    print(f"Successfully extracted icon for: {exe_path}, size: {os.path.getsize(temp_ico)} bytes")
                    # Load the image with PIL and resize
                    img = Image.open(temp_ico)
                    img = img.resize(size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    # Clean up temp file
                    try:
                        os.remove(temp_ico)
                    except:
                        pass
                    
                    if callback:
                        callback(photo)
                else:
                    print(f"Failed to extract icon for {exe_path}: return code {result.returncode}")
                    print(f"File exists: {os.path.exists(temp_ico)}, Size: {os.path.getsize(temp_ico) if os.path.exists(temp_ico) else 'N/A'}")
                    if result.stderr:
                        print(f"PowerShell error: {result.stderr}")
                    if callback:
                        callback(None)
                
            except subprocess.TimeoutExpired:
                print(f"PowerShell command timed out for {exe_path}")
                if callback:
                    callback(None)
            except Exception as e:
                print(f"Exception during icon extraction for {exe_path}: {e}")
                if callback:
                    callback(None)
        
        # Run extraction in background thread
        thread = threading.Thread(target=extract_icon, daemon=True)
        thread.start()
    
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
