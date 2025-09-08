from typing import List, Dict
from NonSteamGame import NonSteamGame

class VDFSerializer:
    @staticmethod
    def games_to_vdf_dict(games: List[NonSteamGame]) -> Dict:
        """Convert a list of NonSteamGame objects to VDF format."""
        shortcuts = {}
        for i, game in enumerate(games):
            shortcuts[str(i)] = {
                **game.as_dict()
            }
        return {"shortcuts": shortcuts}
    
    @staticmethod
    def games_from_vdf_dict(vdf_data: Dict) -> List[NonSteamGame]:
        """Convert VDF data to a list of NonSteamGame objects."""
        games = []
        shortcuts = vdf_data.get("shortcuts", {})
        
        for shortcut_key in shortcuts:
            shortcut_data = shortcuts[shortcut_key]
            game = NonSteamGame(
                id=shortcut_data.get("appid", 0),
                name=shortcut_data.get("AppName", ""),
                exe=shortcut_data.get("Exe", ""),
                dir=shortcut_data.get("StartDir", ""),
                icon=shortcut_data.get("icon", ""),
                ShortcutPath=shortcut_data.get("ShortcutPath", ""),
                LaunchOptions=shortcut_data.get("LaunchOptions", ""),
                IsHidden=shortcut_data.get("IsHidden", 0),
                AllowDesktopConfig=shortcut_data.get("AllowDesktopConfig", 1),
                AllowOverlay=shortcut_data.get("AllowOverlay", 1),
                OpenVR=shortcut_data.get("OpenVR", 0),
                Devkit=shortcut_data.get("Devkit", 0),
                DevkitGameID=shortcut_data.get("DevkitGameID", ""),
                DevkitOverrideAppID=shortcut_data.get("DevkitOverrideAppID", 0),
                LastPlayTime=shortcut_data.get("LastPlayTime", 0),
                FlatpakAppID=shortcut_data.get("FlatpakAppID", ""),
                tags=shortcut_data.get("tags", {})
            )
            games.append(game)
        
        return games
