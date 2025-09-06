from typing import Optional

class NonSteamGame:
    
    def __init__(self,
                 id:int,
                 name:str,
                 exe:str,
                 dir:str,
                 icon:Optional[str],
                 ShortcutPath :Optional[str],
                 LaunchOptions:Optional[str],
                 IsHidden : Optional[str],
                 AllowDesktopConfig : Optional[str],
                 AllowOverlay : Optional[str],
                 OpenVR : Optional[str],
                 Devkit : Optional[str],
                 DevkitGameID : Optional[str],
                 DevkitOverrideAppID : Optional[str],
                 LastPlayTime : Optional[str],
                 FlatpakAppID : Optional[str],
                 tags = Optional[str]
                 ):
        self.appid = id
        self.AppName= name
        self.Exe = exe
        self.StartDir = dir
        self.icon = icon if icon is not None else "" 
        self.ShortcutPath = ShortcutPath if ShortcutPath is not None else ""
        self.LaunchOptions = LaunchOptions if LaunchOptions is not None else ""
        self.IsHidden = IsHidden if IsHidden is not None else 0
        self.AllowDesktopConfig = AllowDesktopConfig if AllowDesktopConfig is not None else 1
        self.AllowOverlay = AllowOverlay if AllowOverlay is not None else 1
        self.OpenVR = OpenVR if OpenVR is not None else 0
        self.Devkit = Devkit if Devkit is not None else 0
        self.DevkitGameID = DevkitGameID if DevkitGameID is not None else ""
        self.DevkitOverrideAppID = DevkitOverrideAppID if DevkitOverrideAppID is not None else 0
        self.LastPlayTime = LastPlayTime if LastPlayTime is not None else 0
        self.FlatpakAppID = FlatpakAppID if FlatpakAppID is not None else ""
        self.tags = tags if tags is not None else {}
    
    def as_dict(self):
        return self.__dict__