import json
from pathlib import Path

class NonSteamGame:
    
    def __init__(self,
                 id:int,
                 name:str,
                 exe:str,
                 dir:str,
                 icon:str = "",
                 ShortcutPath:str = "",
                 LaunchOptions:str = "",
                 IsHidden:int = 0,
                 AllowDesktopConfig:int = 1,
                 AllowOverlay:int = 1,
                 OpenVR:int = 0,
                 Devkit:int = 0,
                 DevkitGameID:str = "",
                 DevkitOverrideAppID:int = 0,
                 LastPlayTime:int = 0,
                 FlatpakAppID:str = "",
                 tags:dict = {}
                 ):
        self.appid = id
        self.AppName= name
        self.Exe = exe
        self.StartDir = dir
        self.icon = icon 
        self.ShortcutPath = ShortcutPath 
        self.LaunchOptions = LaunchOptions 
        self.IsHidden = IsHidden 
        self.AllowDesktopConfig = AllowDesktopConfig
        self.AllowOverlay = AllowOverlay 
        self.OpenVR = OpenVR 
        self.Devkit = Devkit 
        self.DevkitGameID = DevkitGameID 
        self.DevkitOverrideAppID = DevkitOverrideAppID 
        self.LastPlayTime = LastPlayTime 
        self.FlatpakAppID = FlatpakAppID 
        self.tags = tags 
    
    @classmethod
    def from_candidate(cls, candidate):
        """Create a NonSteamGame from a GameCandidate."""
        return cls(
            id=candidate.steam_id,
            name=candidate.name,
            exe=str(candidate.exe_path),
            dir=str(candidate.start_dir)
        )
    
    def __str__(self):
        obj = {
            "name": self.AppName,
            "steamID": self.appid,
            "exe": str(self.Exe),
            "StartDir": str(self.StartDir),
        }
        return json.dumps(obj, indent=4)
     
    def as_dict(self):
        return self.__dict__